#!/usr/bin/env python3
"""Bounded executable contracts for the independent Aster teaching model."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import TypeAlias


MAX_FORMULA_NODES = 63
MAX_FORMULA_DEPTH = 12
MAX_CASES = 16
MAX_LOOP_STEPS = 16
MIN_VALUE = -32
MAX_VALUE = 32


class Sort(Enum):
    INT = "Int"
    BOOL = "Bool"


class Formula:
    """Marker class; only the exact frozen node classes below are accepted."""


@dataclass(frozen=True, slots=True)
class IntLit(Formula):
    value: int


@dataclass(frozen=True, slots=True)
class BoolLit(Formula):
    value: bool


@dataclass(frozen=True, slots=True)
class Current(Formula):
    field: str


@dataclass(frozen=True, slots=True)
class Old(Formula):
    field: str


@dataclass(frozen=True, slots=True)
class Add(Formula):
    left: Formula
    right: Formula


@dataclass(frozen=True, slots=True)
class Sub(Formula):
    left: Formula
    right: Formula


@dataclass(frozen=True, slots=True)
class Eq(Formula):
    left: Formula
    right: Formula


@dataclass(frozen=True, slots=True)
class Lt(Formula):
    left: Formula
    right: Formula


@dataclass(frozen=True, slots=True)
class Le(Formula):
    left: Formula
    right: Formula


@dataclass(frozen=True, slots=True)
class And(Formula):
    left: Formula
    right: Formula


@dataclass(frozen=True, slots=True)
class Or(Formula):
    left: Formula
    right: Formula


@dataclass(frozen=True, slots=True)
class Not(Formula):
    value: Formula


_FORMULA_TYPES = (
    IntLit,
    BoolLit,
    Current,
    Old,
    Add,
    Sub,
    Eq,
    Lt,
    Le,
    And,
    Or,
    Not,
)


@dataclass(frozen=True, slots=True)
class State:
    value: int
    goal: int


@dataclass(frozen=True, slots=True)
class Contract:
    assumption: Formula
    precondition: Formula
    postcondition: Formula


@dataclass(frozen=True, slots=True)
class LoopPlan:
    guard: Formula
    delta: int
    invariant: Formula
    variant: Formula | None


@dataclass(frozen=True, slots=True)
class Counterexample:
    phase: str
    initial: State
    current: State
    steps: int
    detail: str


@dataclass(frozen=True, slots=True)
class CheckResult:
    status: str
    mode: str
    considered: int
    excluded: int
    total_steps: int
    counterexample: Counterexample | None
    final_states: tuple[State, ...] = ()


Value: TypeAlias = int | bool


class ModelError(Exception):
    """Stable malformed-input or resource error."""

    def __init__(self, code: str, message: str) -> None:
        self.code = code
        self.message = message
        super().__init__(f"{code}: {message}")


def _children(formula: Formula) -> tuple[object, ...]:
    if type(formula) in (Add, Sub, Eq, Lt, Le, And, Or):
        return (formula.left, formula.right)
    if type(formula) is Not:
        return (formula.value,)
    return ()


class _FormulaChecker:
    def __init__(self) -> None:
        self.nodes = 0
        self.active: set[int] = set()

    def visit(self, candidate: object, depth: int) -> Sort:
        if type(candidate) not in _FORMULA_TYPES:
            raise ModelError("F001", "value is not a supported Aster formula node")
        formula = candidate
        if depth > MAX_FORMULA_DEPTH:
            raise ModelError("F002", "formula depth exceeds 12")
        if self.nodes >= MAX_FORMULA_NODES:
            raise ModelError("F003", "formula node count exceeds 63")
        identity = id(formula)
        if identity in self.active:
            raise ModelError("F004", "cyclic formula is not finite")
        self.nodes += 1
        self.active.add(identity)
        try:
            if type(formula) is IntLit:
                if type(formula.value) is not int or not MIN_VALUE <= formula.value <= MAX_VALUE:
                    raise ModelError("F005", "integer literal is outside -32..32")
                return Sort.INT
            if type(formula) is BoolLit:
                if type(formula.value) is not bool:
                    raise ModelError("F006", "Boolean literal must be an exact Boolean")
                return Sort.BOOL
            if type(formula) in (Current, Old):
                if type(formula.field) is not str or formula.field not in ("value", "goal"):
                    raise ModelError("F007", "state field must be exactly value or goal")
                return Sort.INT
            if type(formula) in (Add, Sub):
                sorts = tuple(self.visit(child, depth + 1) for child in _children(formula))
                if sorts != (Sort.INT, Sort.INT):
                    raise ModelError("F008", "arithmetic operands must have sort Int")
                return Sort.INT
            if type(formula) is Eq:
                left = self.visit(formula.left, depth + 1)
                right = self.visit(formula.right, depth + 1)
                if left is not right:
                    raise ModelError("F009", "equality operands must have the same sort")
                return Sort.BOOL
            if type(formula) in (Lt, Le):
                sorts = tuple(self.visit(child, depth + 1) for child in _children(formula))
                if sorts != (Sort.INT, Sort.INT):
                    raise ModelError("F010", "ordered comparison operands must have sort Int")
                return Sort.BOOL
            if type(formula) in (And, Or):
                sorts = tuple(self.visit(child, depth + 1) for child in _children(formula))
                if sorts != (Sort.BOOL, Sort.BOOL):
                    raise ModelError("F011", "logical operands must have sort Bool")
                return Sort.BOOL
            if type(formula) is Not:
                if self.visit(formula.value, depth + 1) is not Sort.BOOL:
                    raise ModelError("F012", "not operand must have sort Bool")
                return Sort.BOOL
        finally:
            self.active.remove(identity)
        raise AssertionError("unreachable formula node")


def validate_formula(formula: object, expected: Sort | None = None) -> tuple[Sort, int]:
    checker = _FormulaChecker()
    sort = checker.visit(formula, 1)
    if expected is not None and sort is not expected:
        raise ModelError("F013", f"formula must have sort {expected.value}")
    return sort, checker.nodes


def _validate_state(candidate: object) -> State:
    if type(candidate) is not State:
        raise ModelError("C001", "each case must be an exact Aster State")
    if (
        type(candidate.value) is not int
        or type(candidate.goal) is not int
        or not MIN_VALUE <= candidate.value <= MAX_VALUE
        or not MIN_VALUE <= candidate.goal <= MAX_VALUE
    ):
        raise ModelError("C002", "state fields must be exact integers in -32..32")
    return candidate


def validate_cases(cases: object) -> tuple[State, ...]:
    if type(cases) is not tuple:
        raise ModelError("C003", "cases must be an immutable tuple")
    if len(cases) > MAX_CASES:
        raise ModelError("C004", "case count exceeds 16")
    return tuple(_validate_state(case) for case in cases)


def _validate_contract(contract: object) -> Contract:
    if type(contract) is not Contract:
        raise ModelError("C005", "contract must be an exact Aster Contract")
    validate_formula(contract.assumption, Sort.BOOL)
    validate_formula(contract.precondition, Sort.BOOL)
    validate_formula(contract.postcondition, Sort.BOOL)
    return contract


def _validate_plan(plan: object, total: bool) -> LoopPlan:
    if type(plan) is not LoopPlan:
        raise ModelError("P001", "plan must be an exact Aster LoopPlan")
    validate_formula(plan.guard, Sort.BOOL)
    validate_formula(plan.invariant, Sort.BOOL)
    if type(plan.delta) is not int or not -8 <= plan.delta <= 8:
        raise ModelError("P002", "loop delta must be an exact integer in -8..8")
    if plan.variant is not None:
        validate_formula(plan.variant, Sort.INT)
    if total and plan.variant is None:
        raise ModelError("P003", "total-correctness checking requires an integer variant")
    return plan


def evaluate(formula: Formula, current: State, old: State) -> Value:
    """Evaluate one already validated formula in a current/initial state pair."""

    if type(formula) is IntLit:
        return formula.value
    if type(formula) is BoolLit:
        return formula.value
    if type(formula) is Current:
        return getattr(current, formula.field)
    if type(formula) is Old:
        return getattr(old, formula.field)
    if type(formula) in (Add, Sub):
        left = evaluate(formula.left, current, old)
        right = evaluate(formula.right, current, old)
        assert type(left) is int and type(right) is int
        result = left + right if type(formula) is Add else left - right
        if not MIN_VALUE <= result <= MAX_VALUE:
            raise ModelError("R001", "formula arithmetic result is outside -32..32")
        return result
    if type(formula) is Eq:
        return evaluate(formula.left, current, old) == evaluate(formula.right, current, old)
    if type(formula) is Lt:
        return evaluate(formula.left, current, old) < evaluate(formula.right, current, old)
    if type(formula) is Le:
        return evaluate(formula.left, current, old) <= evaluate(formula.right, current, old)
    if type(formula) is And:
        return bool(evaluate(formula.left, current, old)) and bool(
            evaluate(formula.right, current, old)
        )
    if type(formula) is Or:
        return bool(evaluate(formula.left, current, old)) or bool(
            evaluate(formula.right, current, old)
        )
    if type(formula) is Not:
        return not bool(evaluate(formula.value, current, old))
    raise AssertionError("formula must be validated before evaluation")


def _failure(
    mode: str,
    considered: int,
    excluded: int,
    total_steps: int,
    phase: str,
    initial: State,
    current: State,
    steps: int,
    detail: str,
) -> CheckResult:
    return CheckResult(
        "FAIL",
        mode,
        considered,
        excluded,
        total_steps,
        Counterexample(phase, initial, current, steps, detail),
    )


def _run_case(plan: LoopPlan, initial: State, total: bool) -> tuple[State, int, Counterexample | None]:
    current = initial
    steps = 0
    if evaluate(plan.invariant, current, initial) is not True:
        return current, steps, Counterexample(
            "invariant-initialization", initial, current, steps, "invariant is false initially"
        )
    while evaluate(plan.guard, current, initial) is True:
        if steps >= MAX_LOOP_STEPS:
            raise ModelError("R002", "loop step count exceeds 16")
        previous_variant: int | None = None
        if total:
            assert plan.variant is not None
            candidate = evaluate(plan.variant, current, initial)
            assert type(candidate) is int
            previous_variant = candidate
            if candidate < 0:
                return current, steps, Counterexample(
                    "variant-nonnegative", initial, current, steps, "variant is negative while guard is true"
                )
        next_value = current.value + plan.delta
        if not MIN_VALUE <= next_value <= MAX_VALUE:
            raise ModelError("R003", "loop update leaves the state range -32..32")
        current = State(next_value, current.goal)
        steps += 1
        if evaluate(plan.invariant, current, initial) is not True:
            return current, steps, Counterexample(
                "invariant-preservation", initial, current, steps, "body does not preserve invariant"
            )
        if total:
            assert previous_variant is not None and plan.variant is not None
            next_variant = evaluate(plan.variant, current, initial)
            assert type(next_variant) is int
            if next_variant >= previous_variant:
                return current, steps, Counterexample(
                    "variant-decrease", initial, current, steps, "variant did not strictly decrease"
                )
            if evaluate(plan.guard, current, initial) is True and next_variant < 0:
                return current, steps, Counterexample(
                    "variant-nonnegative", initial, current, steps, "variant is negative while guard remains true"
                )
    return current, steps, None


def verify(
    contract: object,
    plan: object,
    cases: object,
    *,
    total: bool,
) -> CheckResult:
    """Check partial or total correctness over an explicit finite case tuple."""

    checked_contract = _validate_contract(contract)
    checked_plan = _validate_plan(plan, total)
    checked_cases = validate_cases(cases)
    mode = "total" if total else "partial"
    considered = 0
    excluded = 0
    total_steps = 0
    final_states: list[State] = []
    for initial in checked_cases:
        if evaluate(checked_contract.assumption, initial, initial) is not True:
            excluded += 1
            continue
        if evaluate(checked_contract.precondition, initial, initial) is not True:
            excluded += 1
            continue
        considered += 1
        final, steps, counterexample = _run_case(checked_plan, initial, total)
        total_steps += steps
        if counterexample is not None:
            return CheckResult(
                "FAIL", mode, considered, excluded, total_steps, counterexample
            )
        if evaluate(checked_contract.postcondition, final, initial) is not True:
            return _failure(
                mode,
                considered,
                excluded,
                total_steps,
                "postcondition",
                initial,
                final,
                steps,
                "postcondition is false on the final state",
            )
        final_states.append(final)
    if considered == 0:
        raise ModelError("C006", "assumptions and precondition select no cases")
    return CheckResult(
        "PASS", mode, considered, excluded, total_steps, None, tuple(final_states)
    )


def verify_refinement(
    abstract: object,
    concrete: object,
    plan: object,
    cases: object,
) -> CheckResult:
    """Check no stronger concrete domain and abstract-post preservation."""

    abstract_contract = _validate_contract(abstract)
    concrete_contract = _validate_contract(concrete)
    checked_plan = _validate_plan(plan, True)
    checked_cases = validate_cases(cases)
    considered = 0
    excluded = 0
    total_steps = 0
    final_states: list[State] = []
    for initial in checked_cases:
        if (
            evaluate(abstract_contract.assumption, initial, initial) is not True
            or evaluate(abstract_contract.precondition, initial, initial) is not True
        ):
            excluded += 1
            continue
        considered += 1
        if (
            evaluate(concrete_contract.assumption, initial, initial) is not True
            or evaluate(concrete_contract.precondition, initial, initial) is not True
        ):
            return _failure(
                "refinement",
                considered,
                excluded,
                total_steps,
                "stronger-precondition",
                initial,
                initial,
                0,
                "concrete domain excludes an abstractly permitted state",
            )
        final, steps, counterexample = _run_case(checked_plan, initial, True)
        total_steps += steps
        if counterexample is not None:
            return CheckResult(
                "FAIL", "refinement", considered, excluded, total_steps, counterexample
            )
        if evaluate(concrete_contract.postcondition, final, initial) is not True:
            return _failure(
                "refinement", considered, excluded, total_steps, "concrete-postcondition",
                initial, final, steps, "concrete postcondition is false"
            )
        if evaluate(abstract_contract.postcondition, final, initial) is not True:
            return _failure(
                "refinement", considered, excluded, total_steps, "abstract-postcondition",
                initial, final, steps, "concrete result violates the abstract postcondition"
            )
        final_states.append(final)
    if considered == 0:
        raise ModelError("C006", "abstract assumptions and precondition select no cases")
    return CheckResult(
        "PASS",
        "refinement",
        considered,
        excluded,
        total_steps,
        None,
        tuple(final_states),
    )


def countdown_contract() -> Contract:
    return Contract(
        assumption=And(Le(IntLit(0), Current("goal")), Le(Current("value"), IntLit(16))),
        precondition=Le(Current("goal"), Current("value")),
        postcondition=Eq(Current("value"), Current("goal")),
    )


def countdown_plan() -> LoopPlan:
    return LoopPlan(
        guard=Lt(Current("goal"), Current("value")),
        delta=-1,
        invariant=And(
            Le(Current("goal"), Current("value")),
            Eq(Current("goal"), Old("goal")),
        ),
        variant=Sub(Current("value"), Current("goal")),
    )
