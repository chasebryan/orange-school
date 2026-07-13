#!/usr/bin/env python3
"""A bounded static and dynamic semantics for the independent Lumen language."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias


MAX_AST_NODES = 256
MAX_AST_DEPTH = 32
MAX_ENV_BINDINGS = 24
MAX_STEPS = 256
MAX_OUTPUTS = 64
MAX_NAME_BYTES = 24
MIN_INT = -1_000_000
MAX_INT = 1_000_000


class Type(Enum):
    INT = "Int"
    BOOL = "Bool"
    UNIT = "Unit"


class Effect(Enum):
    EMIT = "emit"


class Expr:
    """Marker base class; only the frozen node classes below are accepted."""


@dataclass(frozen=True, slots=True)
class IntLit(Expr):
    value: int


@dataclass(frozen=True, slots=True)
class BoolLit(Expr):
    value: bool


@dataclass(frozen=True, slots=True)
class Var(Expr):
    name: str


@dataclass(frozen=True, slots=True)
class Add(Expr):
    left: Expr
    right: Expr


@dataclass(frozen=True, slots=True)
class Sub(Expr):
    left: Expr
    right: Expr


@dataclass(frozen=True, slots=True)
class Eq(Expr):
    left: Expr
    right: Expr


@dataclass(frozen=True, slots=True)
class If(Expr):
    condition: Expr
    then_branch: Expr
    else_branch: Expr


@dataclass(frozen=True, slots=True)
class Let(Expr):
    name: str
    bound: Expr
    body: Expr


@dataclass(frozen=True, slots=True)
class Emit(Expr):
    value: Expr


@dataclass(frozen=True, slots=True)
class Seq(Expr):
    first: Expr
    second: Expr


@dataclass(frozen=True, slots=True)
class UnitValue:
    pass


UNIT = UnitValue()
Value: TypeAlias = int | bool | UnitValue
TypeEnvironment: TypeAlias = tuple[tuple[str, Type], ...]
ValueEnvironment: TypeAlias = tuple[tuple[str, Value], ...]


@dataclass(frozen=True, slots=True)
class Judgment:
    type: Type
    potential_effects: frozenset[Effect]
    visited_nodes: int


@dataclass(frozen=True, slots=True)
class RunResult:
    type: Type
    potential_effects: frozenset[Effect]
    value: Value
    outputs: tuple[int, ...]
    steps: int


class SemanticError(Exception):
    """A stable language error, independent of paths, clocks, and addresses."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


_NODE_TYPES = (IntLit, BoolLit, Var, Add, Sub, Eq, If, Let, Emit, Seq)


def _validate_name(name: object) -> str:
    if type(name) is not str:
        raise SemanticError("S002", "binding name must be an exact string")
    if not 1 <= len(name) <= MAX_NAME_BYTES:
        raise SemanticError(
            "S002",
            "binding name must be 1..24 ASCII bytes matching [A-Za-z_][A-Za-z0-9_]*",
        )
    encoded = name.encode("ascii", errors="strict") if name.isascii() else b""
    valid = (
        (encoded[0:1].isalpha() or encoded[0:1] == b"_")
        and all(bytes((byte,)).isalnum() or byte == 95 for byte in encoded[1:])
    )
    if not valid:
        raise SemanticError(
            "S002",
            "binding name must be 1..24 ASCII bytes matching [A-Za-z_][A-Za-z0-9_]*",
        )
    return name


def _require_exact_node(expr: object) -> Expr:
    if type(expr) not in _NODE_TYPES:
        raise SemanticError("S001", "value is not a supported Lumen AST node")
    return expr


def _lookup_type(environment: TypeEnvironment, name: str) -> Type:
    for candidate, value in reversed(environment):
        if candidate == name:
            return value
    raise SemanticError("S003", f"unbound name: {name}")


def _lookup_value(environment: ValueEnvironment, name: str) -> Value:
    for candidate, value in reversed(environment):
        if candidate == name:
            return value
    raise SemanticError("S003", f"unbound name: {name}")


class _Checker:
    def __init__(self) -> None:
        self.visited = 0
        self.active: set[int] = set()

    def check(self, expr: object, environment: TypeEnvironment, depth: int) -> tuple[Type, frozenset[Effect]]:
        node = _require_exact_node(expr)
        if depth > MAX_AST_DEPTH:
            raise SemanticError("S004", "AST depth exceeds 32")
        if self.visited >= MAX_AST_NODES:
            raise SemanticError("S005", "AST visit count exceeds 256")
        identity = id(node)
        if identity in self.active:
            raise SemanticError("S006", "cyclic AST is not a finite Lumen expression")
        self.visited += 1
        self.active.add(identity)
        try:
            if type(node) is IntLit:
                if type(node.value) is not int or not MIN_INT <= node.value <= MAX_INT:
                    raise SemanticError("S007", "integer literal is outside -1000000..1000000")
                return Type.INT, frozenset()
            if type(node) is BoolLit:
                if type(node.value) is not bool:
                    raise SemanticError("S008", "boolean literal must be an exact boolean")
                return Type.BOOL, frozenset()
            if type(node) is Var:
                name = _validate_name(node.name)
                return _lookup_type(environment, name), frozenset()
            if type(node) in (Add, Sub):
                left_type, left_effects = self.check(node.left, environment, depth + 1)
                right_type, right_effects = self.check(node.right, environment, depth + 1)
                if left_type is not Type.INT or right_type is not Type.INT:
                    raise SemanticError("S009", "arithmetic operands must both have type Int")
                return Type.INT, left_effects | right_effects
            if type(node) is Eq:
                left_type, left_effects = self.check(node.left, environment, depth + 1)
                right_type, right_effects = self.check(node.right, environment, depth + 1)
                if left_type is not right_type or left_type not in (Type.INT, Type.BOOL):
                    raise SemanticError("S010", "equality operands must have the same Int or Bool type")
                return Type.BOOL, left_effects | right_effects
            if type(node) is If:
                condition_type, condition_effects = self.check(node.condition, environment, depth + 1)
                if condition_type is not Type.BOOL:
                    raise SemanticError("S011", "if condition must have type Bool")
                then_type, then_effects = self.check(node.then_branch, environment, depth + 1)
                else_type, else_effects = self.check(node.else_branch, environment, depth + 1)
                if then_type is not else_type:
                    raise SemanticError("S012", "if branches must have the same type")
                return then_type, condition_effects | then_effects | else_effects
            if type(node) is Let:
                name = _validate_name(node.name)
                bound_type, bound_effects = self.check(node.bound, environment, depth + 1)
                if len(environment) >= MAX_ENV_BINDINGS:
                    raise SemanticError("S013", "type environment exceeds 24 bindings")
                body_type, body_effects = self.check(
                    node.body, environment + ((name, bound_type),), depth + 1
                )
                return body_type, bound_effects | body_effects
            if type(node) is Emit:
                value_type, effects = self.check(node.value, environment, depth + 1)
                if value_type is not Type.INT:
                    raise SemanticError("S014", "emit operand must have type Int")
                return Type.UNIT, effects | frozenset((Effect.EMIT,))
            if type(node) is Seq:
                first_type, first_effects = self.check(node.first, environment, depth + 1)
                if first_type is not Type.UNIT:
                    raise SemanticError("S015", "sequence first operand must have type Unit")
                second_type, second_effects = self.check(node.second, environment, depth + 1)
                return second_type, first_effects | second_effects
        finally:
            self.active.remove(identity)
        raise AssertionError("unreachable node type")


def typecheck(expr: object) -> Judgment:
    """Derive the closed expression's type and conservative potential effects."""

    checker = _Checker()
    result_type, effects = checker.check(expr, (), 1)
    return Judgment(result_type, effects, checker.visited)


class _Evaluator:
    def __init__(self, step_budget: int, output_budget: int) -> None:
        self.step_budget = step_budget
        self.output_budget = output_budget
        self.steps = 0
        self.outputs: list[int] = []

    def _tick(self) -> None:
        if self.steps >= self.step_budget:
            raise SemanticError("R001", "evaluation step budget exhausted")
        self.steps += 1

    def evaluate(self, node: Expr, environment: ValueEnvironment) -> Value:
        self._tick()
        if type(node) is IntLit:
            return node.value
        if type(node) is BoolLit:
            return node.value
        if type(node) is Var:
            return _lookup_value(environment, node.name)
        if type(node) in (Add, Sub):
            left = self.evaluate(node.left, environment)
            right = self.evaluate(node.right, environment)
            if type(left) is not int or type(right) is not int:
                raise AssertionError("typechecked arithmetic invariant failed")
            value = left + right if type(node) is Add else left - right
            if not MIN_INT <= value <= MAX_INT:
                raise SemanticError("R002", "arithmetic result is outside -1000000..1000000")
            return value
        if type(node) is Eq:
            left = self.evaluate(node.left, environment)
            right = self.evaluate(node.right, environment)
            return left == right
        if type(node) is If:
            condition = self.evaluate(node.condition, environment)
            if type(condition) is not bool:
                raise AssertionError("typechecked condition invariant failed")
            branch = node.then_branch if condition else node.else_branch
            return self.evaluate(branch, environment)
        if type(node) is Let:
            bound = self.evaluate(node.bound, environment)
            if len(environment) >= MAX_ENV_BINDINGS:
                raise SemanticError("R003", "value environment exceeds 24 bindings")
            return self.evaluate(node.body, environment + ((node.name, bound),))
        if type(node) is Emit:
            value = self.evaluate(node.value, environment)
            if type(value) is not int:
                raise AssertionError("typechecked emit invariant failed")
            if len(self.outputs) >= self.output_budget:
                raise SemanticError("R004", "output budget exhausted")
            self.outputs.append(value)
            return UNIT
        if type(node) is Seq:
            first = self.evaluate(node.first, environment)
            if first != UNIT:
                raise AssertionError("typechecked sequence invariant failed")
            return self.evaluate(node.second, environment)
        raise AssertionError("unsupported node reached evaluator")


def _require_budget(value: object, maximum: int, label: str) -> int:
    if type(value) is not int or not 1 <= value <= maximum:
        raise SemanticError("R005", f"{label} must be an integer in 1..{maximum}")
    return value


def run(expr: object, *, step_budget: int = MAX_STEPS, output_budget: int = MAX_OUTPUTS) -> RunResult:
    """Typecheck and evaluate a closed expression under explicit runtime budgets."""

    checked = typecheck(expr)
    checked_steps = _require_budget(step_budget, MAX_STEPS, "step budget")
    checked_outputs = _require_budget(output_budget, MAX_OUTPUTS, "output budget")
    evaluator = _Evaluator(checked_steps, checked_outputs)
    value = evaluator.evaluate(_require_exact_node(expr), ())
    return RunResult(
        checked.type,
        checked.potential_effects,
        value,
        tuple(evaluator.outputs),
        evaluator.steps,
    )
