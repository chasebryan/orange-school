#!/usr/bin/env python3
"""Bounded typed-AST to IR to byte-artifact teaching pipeline.

Cairn is independent courseware.  It is not an Orange frontend, IR, bytecode,
or compatibility model.
"""

from __future__ import annotations

from dataclasses import dataclass
import struct


I32 = "i32"
BOOL = "bool"
I32_MIN = -(1 << 31)
I32_MAX = (1 << 31) - 1
MAX_SOURCE_NODES = 63
MAX_AST_DEPTH = 24
MAX_BINDINGS = 16
MAX_NAME_BYTES = 24
_MISSING = object()
MAX_IR_INSTRUCTIONS = 63
MAGIC = b"CIR1"
VERSION = 1
HEADER_SIZE = 12
INSTRUCTION_SIZE = 16
MAX_ARTIFACT_BYTES = HEADER_SIZE + MAX_IR_INSTRUCTIONS * INSTRUCTION_SIZE
NO_REGISTER = 0xFFFF


@dataclass(frozen=True, slots=True)
class IntLiteral:
    value: int


@dataclass(frozen=True, slots=True)
class BoolLiteral:
    value: bool


@dataclass(frozen=True, slots=True)
class Name:
    identifier: str


@dataclass(frozen=True, slots=True)
class Add:
    left: object
    right: object


@dataclass(frozen=True, slots=True)
class Less:
    left: object
    right: object


@dataclass(frozen=True, slots=True)
class Choose:
    condition: object
    when_true: object
    when_false: object


@dataclass(frozen=True, slots=True)
class Let:
    identifier: str
    value: object
    body: object


SOURCE_TYPES = (IntLiteral, BoolLiteral, Name, Add, Less, Choose, Let)


@dataclass(frozen=True, slots=True)
class Diagnostic:
    code: str
    message: str


class PipelineError(ValueError):
    """One deterministic contract failure."""

    def __init__(self, code: str, message: str) -> None:
        self.diagnostic = Diagnostic(code, message)
        super().__init__(f"{code}: {message}")


@dataclass(frozen=True, slots=True)
class TypedValue:
    type_name: str
    value: object


@dataclass(frozen=True, slots=True)
class Instruction:
    opcode: str
    result_type: str
    destination: int
    argument_1: int | None = None
    argument_2: int | None = None
    argument_3: int | None = None
    immediate: int | None = None


@dataclass(frozen=True, slots=True)
class Program:
    instructions: tuple[Instruction, ...]
    result_register: int
    result_type: str


_OPCODE_TO_BYTE = {
    "const_i32": 1,
    "const_bool": 2,
    "add_i32": 3,
    "less_i32": 4,
    "select": 5,
}
_BYTE_TO_OPCODE = {value: key for key, value in _OPCODE_TO_BYTE.items()}
_TYPE_TO_BYTE = {I32: 1, BOOL: 2}
_BYTE_TO_TYPE = {value: key for key, value in _TYPE_TO_BYTE.items()}


def _fail(code: str, message: str) -> None:
    raise PipelineError(code, message)


def _plain_identifier(value: object) -> str:
    if type(value) is not str:
        _fail("S004", "binding name must be a string")
    try:
        encoded = value.encode("ascii")
    except UnicodeEncodeError:
        _fail("S004", "binding name must use ASCII lowercase letters, digits, or underscore")
    if not encoded or not (97 <= encoded[0] <= 122):
        _fail("S004", "binding name must begin with an ASCII lowercase letter")
    if any(not (byte == 95 or 48 <= byte <= 57 or 97 <= byte <= 122) for byte in encoded[1:]):
        _fail("S004", "binding name must use ASCII lowercase letters, digits, or underscore")
    if len(encoded) > MAX_NAME_BYTES:
        _fail("S004", f"binding name exceeds {MAX_NAME_BYTES} bytes")
    return value


def _plain_i32(value: object) -> int:
    if type(value) is not int or not I32_MIN <= value <= I32_MAX:
        _fail("S005", "integer literal must fit signed 32-bit range")
    return value


class _Lowerer:
    def __init__(self) -> None:
        self.nodes = 0
        self.instructions: list[Instruction] = []

    def visit(
        self,
        expression: object,
        environment: dict[str, tuple[str, int]],
        depth: int,
        binding_depth: int,
    ) -> tuple[str, int]:
        if type(expression) not in SOURCE_TYPES:
            _fail("S001", "source node has an unsupported exact type")
        if depth > MAX_AST_DEPTH:
            _fail("S003", f"source depth exceeds {MAX_AST_DEPTH}")
        self.nodes += 1
        if self.nodes > MAX_SOURCE_NODES:
            _fail("S002", f"source node count exceeds {MAX_SOURCE_NODES}")

        if type(expression) is IntLiteral:
            return I32, self.emit("const_i32", I32, immediate=_plain_i32(expression.value))
        if type(expression) is BoolLiteral:
            if type(expression.value) is not bool:
                _fail("S005", "boolean literal must be an exact bool")
            return BOOL, self.emit("const_bool", BOOL, immediate=int(expression.value))
        if type(expression) is Name:
            identifier = _plain_identifier(expression.identifier)
            if identifier not in environment:
                _fail("T001", f"undefined name: {identifier}")
            return environment[identifier]
        if type(expression) is Add:
            left_type, left = self.visit(expression.left, environment, depth + 1, binding_depth)
            right_type, right = self.visit(expression.right, environment, depth + 1, binding_depth)
            if (left_type, right_type) != (I32, I32):
                _fail("T002", "add operands must both have type i32")
            return I32, self.emit("add_i32", I32, left, right)
        if type(expression) is Less:
            left_type, left = self.visit(expression.left, environment, depth + 1, binding_depth)
            right_type, right = self.visit(expression.right, environment, depth + 1, binding_depth)
            if (left_type, right_type) != (I32, I32):
                _fail("T003", "less operands must both have type i32")
            return BOOL, self.emit("less_i32", BOOL, left, right)
        if type(expression) is Choose:
            condition_type, condition = self.visit(
                expression.condition, environment, depth + 1, binding_depth
            )
            true_type, when_true = self.visit(
                expression.when_true, environment, depth + 1, binding_depth
            )
            false_type, when_false = self.visit(
                expression.when_false, environment, depth + 1, binding_depth
            )
            if condition_type != BOOL:
                _fail("T004", "choose condition must have type bool")
            if true_type != false_type:
                _fail("T005", "choose branches must have the same type")
            return true_type, self.emit(
                "select", true_type, condition, when_true, when_false
            )
        if type(expression) is Let:
            identifier = _plain_identifier(expression.identifier)
            if binding_depth >= MAX_BINDINGS:
                _fail("S006", f"active binding count exceeds {MAX_BINDINGS}")
            value_type, value = self.visit(
                expression.value, environment, depth + 1, binding_depth
            )
            previous = environment.get(identifier, _MISSING)
            environment[identifier] = (value_type, value)
            try:
                return self.visit(
                    expression.body, environment, depth + 1, binding_depth + 1
                )
            finally:
                if previous is _MISSING:
                    del environment[identifier]
                else:
                    environment[identifier] = previous
        raise AssertionError("source type dispatch is incomplete")

    def emit(
        self,
        opcode: str,
        result_type: str,
        argument_1: int | None = None,
        argument_2: int | None = None,
        argument_3: int | None = None,
        immediate: int | None = None,
    ) -> int:
        if len(self.instructions) >= MAX_IR_INSTRUCTIONS:
            _fail("I001", f"instruction count exceeds {MAX_IR_INSTRUCTIONS}")
        destination = len(self.instructions)
        self.instructions.append(
            Instruction(
                opcode,
                result_type,
                destination,
                argument_1,
                argument_2,
                argument_3,
                immediate,
            )
        )
        return destination


def lower(expression: object) -> Program:
    """Type-check and lower one closed Cairn expression to validated typed IR."""

    lowerer = _Lowerer()
    result_type, result_register = lowerer.visit(expression, {}, 1, 0)
    program = Program(tuple(lowerer.instructions), result_register, result_type)
    validate_ir(program)
    return program


def _require_prior(register: object, destination: int, types: list[str], label: str) -> str:
    if type(register) is not int or not 0 <= register < destination:
        _fail("I004", f"{label} must reference a prior register")
    return types[register]


def validate_ir(program: object) -> None:
    """Validate exact shape, SSA order, operand types, and the result contract."""

    if type(program) is not Program or type(program.instructions) is not tuple:
        _fail("I002", "IR must be an exact Program containing an instruction tuple")
    count = len(program.instructions)
    if not 1 <= count <= MAX_IR_INSTRUCTIONS:
        _fail("I001", f"instruction count must be 1 through {MAX_IR_INSTRUCTIONS}")
    types: list[str] = []
    for destination, instruction in enumerate(program.instructions):
        if type(instruction) is not Instruction:
            _fail("I002", "every IR entry must be an exact Instruction")
        if type(instruction.destination) is not int or instruction.destination != destination:
            _fail("I003", "destinations must be contiguous single assignments from register zero")
        if type(instruction.result_type) is not str or instruction.result_type not in (I32, BOOL):
            _fail("I005", "instruction has an unknown result type")
        op = instruction.opcode
        if type(op) is not str:
            _fail("I006", "instruction has an unknown opcode")
        if op == "const_i32":
            if (
                type(instruction.immediate) is not int
                or not I32_MIN <= instruction.immediate <= I32_MAX
                or instruction.result_type != I32
                or any(
                    value is not None
                    for value in (
                        instruction.argument_1,
                        instruction.argument_2,
                        instruction.argument_3,
                    )
                )
            ):
                _fail("I005", "const_i32 fields or result type are invalid")
        elif op == "const_bool":
            if instruction.immediate not in (0, 1) or type(instruction.immediate) is not int:
                _fail("I005", "const_bool immediate must be zero or one")
            if instruction.result_type != BOOL or any(
                value is not None
                for value in (instruction.argument_1, instruction.argument_2, instruction.argument_3)
            ):
                _fail("I005", "const_bool fields or result type are invalid")
        elif op in ("add_i32", "less_i32"):
            left_type = _require_prior(instruction.argument_1, destination, types, "left operand")
            right_type = _require_prior(instruction.argument_2, destination, types, "right operand")
            expected_result = I32 if op == "add_i32" else BOOL
            if (
                left_type != I32
                or right_type != I32
                or instruction.result_type != expected_result
                or instruction.argument_3 is not None
                or instruction.immediate is not None
            ):
                _fail("I005", f"{op} fields or operand types are invalid")
        elif op == "select":
            condition_type = _require_prior(
                instruction.argument_1, destination, types, "select condition"
            )
            true_type = _require_prior(
                instruction.argument_2, destination, types, "select true operand"
            )
            false_type = _require_prior(
                instruction.argument_3, destination, types, "select false operand"
            )
            if (
                condition_type != BOOL
                or true_type != false_type
                or instruction.result_type != true_type
                or instruction.immediate is not None
            ):
                _fail("I005", "select fields or operand types are invalid")
        else:
            _fail("I006", "instruction has an unknown opcode")
        types.append(instruction.result_type)
    if type(program.result_register) is not int or not 0 <= program.result_register < count:
        _fail("I007", "result register is outside the program")
    if (
        type(program.result_type) is not str
        or program.result_type not in (I32, BOOL)
        or types[program.result_register] != program.result_type
    ):
        _fail("I007", "result type does not match the result register")


def execute_ir(program: object) -> TypedValue:
    """Validate and execute the pure straight-line IR using mathematical integers."""

    validate_ir(program)
    values: list[object] = []
    for instruction in program.instructions:
        if instruction.opcode in ("const_i32", "const_bool"):
            value: object = (
                bool(instruction.immediate)
                if instruction.opcode == "const_bool"
                else instruction.immediate
            )
        elif instruction.opcode == "add_i32":
            value = values[instruction.argument_1] + values[instruction.argument_2]
            if not I32_MIN <= value <= I32_MAX:
                _fail("R001", "i32 addition overflowed")
        elif instruction.opcode == "less_i32":
            value = values[instruction.argument_1] < values[instruction.argument_2]
        else:
            value = (
                values[instruction.argument_2]
                if values[instruction.argument_1]
                else values[instruction.argument_3]
            )
        values.append(value)
    return TypedValue(program.result_type, values[program.result_register])


def _evaluate(
    expression: object,
    environment: dict[str, TypedValue],
    state: list[int],
    depth: int,
    binding_depth: int,
) -> TypedValue:
    if type(expression) not in SOURCE_TYPES:
        _fail("S001", "source node has an unsupported exact type")
    if depth > MAX_AST_DEPTH:
        _fail("S003", f"source depth exceeds {MAX_AST_DEPTH}")
    state[0] += 1
    if state[0] > MAX_SOURCE_NODES:
        _fail("S002", f"source node count exceeds {MAX_SOURCE_NODES}")
    if type(expression) is IntLiteral:
        return TypedValue(I32, _plain_i32(expression.value))
    if type(expression) is BoolLiteral:
        if type(expression.value) is not bool:
            _fail("S005", "boolean literal must be an exact bool")
        return TypedValue(BOOL, expression.value)
    if type(expression) is Name:
        identifier = _plain_identifier(expression.identifier)
        if identifier not in environment:
            _fail("T001", f"undefined name: {identifier}")
        return environment[identifier]
    if type(expression) in (Add, Less):
        left = _evaluate(expression.left, environment, state, depth + 1, binding_depth)
        right = _evaluate(expression.right, environment, state, depth + 1, binding_depth)
        if left.type_name != I32 or right.type_name != I32:
            code = "T002" if type(expression) is Add else "T003"
            word = "add" if type(expression) is Add else "less"
            _fail(code, f"{word} operands must both have type i32")
        if type(expression) is Less:
            return TypedValue(BOOL, left.value < right.value)
        value = left.value + right.value
        if not I32_MIN <= value <= I32_MAX:
            _fail("R001", "i32 addition overflowed")
        return TypedValue(I32, value)
    if type(expression) is Choose:
        condition = _evaluate(expression.condition, environment, state, depth + 1, binding_depth)
        when_true = _evaluate(expression.when_true, environment, state, depth + 1, binding_depth)
        when_false = _evaluate(expression.when_false, environment, state, depth + 1, binding_depth)
        if condition.type_name != BOOL:
            _fail("T004", "choose condition must have type bool")
        if when_true.type_name != when_false.type_name:
            _fail("T005", "choose branches must have the same type")
        return when_true if condition.value else when_false
    identifier = _plain_identifier(expression.identifier)
    if binding_depth >= MAX_BINDINGS:
        _fail("S006", f"active binding count exceeds {MAX_BINDINGS}")
    value = _evaluate(expression.value, environment, state, depth + 1, binding_depth)
    previous = environment.get(identifier, _MISSING)
    environment[identifier] = value
    try:
        return _evaluate(
            expression.body, environment, state, depth + 1, binding_depth + 1
        )
    finally:
        if previous is _MISSING:
            del environment[identifier]
        else:
            environment[identifier] = previous


def evaluate_source(expression: object) -> TypedValue:
    """Reference source evaluator, intentionally independent of the IR evaluator."""

    return _evaluate(expression, {}, [0], 1, 0)


def encode(program: object) -> bytes:
    """Validate and encode a fixed-width, big-endian Cairn artifact."""

    validate_ir(program)
    header = struct.pack(
        ">4sBBHHBB",
        MAGIC,
        VERSION,
        0,
        len(program.instructions),
        program.result_register,
        _TYPE_TO_BYTE[program.result_type],
        0,
    )
    records: list[bytes] = []
    for instruction in program.instructions:
        arguments = [
            NO_REGISTER if value is None else value
            for value in (
                instruction.argument_1,
                instruction.argument_2,
                instruction.argument_3,
            )
        ]
        immediate = 0 if instruction.immediate is None else instruction.immediate
        records.append(
            struct.pack(
                ">BBHHHHiH",
                _OPCODE_TO_BYTE[instruction.opcode],
                _TYPE_TO_BYTE[instruction.result_type],
                instruction.destination,
                arguments[0],
                arguments[1],
                arguments[2],
                immediate,
                0,
            )
        )
    artifact = header + b"".join(records)
    if len(artifact) > MAX_ARTIFACT_BYTES:
        raise AssertionError("validated artifact exceeded its derived byte cap")
    return artifact


def decode(artifact: object) -> Program:
    """Decode exact bytes, rejecting truncation, trailing data, and invalid IR."""

    if type(artifact) is not bytes:
        _fail("A001", "artifact must be exact bytes")
    if len(artifact) < HEADER_SIZE:
        _fail("A002", "artifact is shorter than the header")
    magic, version, flags, count, result, result_type_byte, reserved = struct.unpack(
        ">4sBBHHBB", artifact[:HEADER_SIZE]
    )
    if magic != MAGIC or version != VERSION:
        _fail("A003", "artifact magic or version is unsupported")
    if flags != 0 or reserved != 0:
        _fail("A004", "artifact reserved fields must be zero")
    if not 1 <= count <= MAX_IR_INSTRUCTIONS:
        _fail("A005", f"artifact instruction count must be 1 through {MAX_IR_INSTRUCTIONS}")
    expected_size = HEADER_SIZE + count * INSTRUCTION_SIZE
    if len(artifact) != expected_size:
        _fail("A006", "artifact length does not match its instruction count")
    if result_type_byte not in _BYTE_TO_TYPE:
        _fail("A007", "artifact result type is unknown")
    instructions: list[Instruction] = []
    for index in range(count):
        start = HEADER_SIZE + index * INSTRUCTION_SIZE
        fields = struct.unpack(">BBHHHHiH", artifact[start : start + INSTRUCTION_SIZE])
        opcode_byte, type_byte, destination, arg1, arg2, arg3, immediate, record_reserved = fields
        if opcode_byte not in _BYTE_TO_OPCODE or type_byte not in _BYTE_TO_TYPE:
            _fail("A007", "artifact instruction opcode or type is unknown")
        if record_reserved != 0:
            _fail("A004", "artifact reserved fields must be zero")
        opcode = _BYTE_TO_OPCODE[opcode_byte]
        if opcode not in ("const_i32", "const_bool") and immediate != 0:
            _fail("A004", "unused artifact immediate fields must be zero")
        instructions.append(
            Instruction(
                opcode,
                _BYTE_TO_TYPE[type_byte],
                destination,
                None if arg1 == NO_REGISTER else arg1,
                None if arg2 == NO_REGISTER else arg2,
                None if arg3 == NO_REGISTER else arg3,
                immediate if opcode in ("const_i32", "const_bool") else None,
            )
        )
    program = Program(tuple(instructions), result, _BYTE_TO_TYPE[result_type_byte])
    validate_ir(program)
    return program


def compile_artifact(expression: object) -> bytes:
    return encode(lower(expression))
