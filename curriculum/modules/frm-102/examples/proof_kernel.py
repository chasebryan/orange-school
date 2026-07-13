"""A bounded teaching kernel for propositional proof certificates.

This is independent courseware, not an Orange component or a proof of itself.
"""

from __future__ import annotations

from dataclasses import dataclass
import re
from typing import TypeAlias


MAX_PROOF_NODES = 255
MAX_PROOF_DEPTH = 40
MAX_FORMULA_NODES = 255
MAX_FORMULA_DEPTH = 64
MAX_CONTEXT = 32
MAX_AXIOMS = 16

_NAME = re.compile(r"[A-Za-z][A-Za-z0-9_]{0,31}\Z", re.ASCII)


@dataclass(frozen=True)
class Atom:
    name: str


@dataclass(frozen=True)
class Bottom:
    pass


@dataclass(frozen=True)
class And:
    left: "Formula"
    right: "Formula"


@dataclass(frozen=True)
class Imp:
    antecedent: "Formula"
    consequent: "Formula"


Formula: TypeAlias = Atom | Bottom | And | Imp


@dataclass(frozen=True)
class Hyp:
    label: str


@dataclass(frozen=True)
class AndIntro:
    left: "Proof"
    right: "Proof"


@dataclass(frozen=True)
class AndElimLeft:
    pair: "Proof"


@dataclass(frozen=True)
class AndElimRight:
    pair: "Proof"


@dataclass(frozen=True)
class ImpIntro:
    label: str
    antecedent: Formula
    body: "Proof"


@dataclass(frozen=True)
class ImpElim:
    function: "Proof"
    argument: "Proof"


@dataclass(frozen=True)
class ExFalso:
    target: Formula
    absurd: "Proof"


@dataclass(frozen=True)
class Axiom:
    name: str


Proof: TypeAlias = (
    Hyp | AndIntro | AndElimLeft | AndElimRight | ImpIntro | ImpElim | ExFalso | Axiom
)


@dataclass(frozen=True)
class Binding:
    label: str
    proposition: Formula


@dataclass(frozen=True)
class AxiomSpec:
    name: str
    proposition: Formula


@dataclass(frozen=True)
class Theorem:
    conclusion: Formula
    assumptions: tuple[Binding, ...]
    axioms_used: tuple[str, ...]
    proof_nodes: int


class ProofError(ValueError):
    """A stable certificate rejection."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


def _valid_name(value: object) -> bool:
    return type(value) is str and _NAME.fullmatch(value) is not None


def validate_formula(formula: object) -> Formula:
    """Validate one explicit formula, including cycles and the depth cap."""

    active: set[int] = set()
    nodes = 0

    def visit(current: object, depth: int) -> Formula:
        nonlocal nodes
        if nodes >= MAX_FORMULA_NODES:
            raise ProofError("F005", "formula node count exceeds 255")
        nodes += 1
        if depth > MAX_FORMULA_DEPTH:
            raise ProofError("F003", "formula depth exceeds 64")
        identity = id(current)
        if identity in active:
            raise ProofError("F004", "cyclic formula")
        active.add(identity)
        try:
            if type(current) is Atom:
                if not _valid_name(current.name):
                    raise ProofError("F002", "invalid atom name")
                return current
            if type(current) is Bottom:
                return current
            if type(current) is And:
                visit(current.left, depth + 1)
                visit(current.right, depth + 1)
                return current
            if type(current) is Imp:
                visit(current.antecedent, depth + 1)
                visit(current.consequent, depth + 1)
                return current
            raise ProofError("F001", "unsupported formula object")
        finally:
            active.remove(identity)

    return visit(formula, 1)


@dataclass(frozen=True)
class Kernel:
    """Replay proof terms under one immutable, explicitly supplied axiom set."""

    def __init__(self, axioms: tuple[AxiomSpec, ...] = ()):
        if type(axioms) is not tuple or len(axioms) > MAX_AXIOMS:
            raise ProofError("A001", "axiom registry must be a tuple of at most 16 entries")
        table: dict[str, Formula] = {}
        for spec in axioms:
            if type(spec) is not AxiomSpec or not _valid_name(spec.name):
                raise ProofError("A002", "invalid axiom specification")
            if spec.name in table:
                raise ProofError("A003", "duplicate axiom name")
            table[spec.name] = validate_formula(spec.proposition)
        object.__setattr__(
            self,
            "_axioms",
            tuple((name, proposition) for name, proposition in table.items()),
        )

    @property
    def axiom_inventory(self) -> tuple[AxiomSpec, ...]:
        return tuple(AxiomSpec(name, proposition) for name, proposition in self._axioms)

    def check(
        self,
        proof: object,
        expected: Formula | None = None,
        assumptions: tuple[Binding, ...] = (),
    ) -> Theorem:
        if type(assumptions) is not tuple or len(assumptions) > MAX_CONTEXT:
            raise ProofError("C001", "assumption context exceeds 32 entries")
        seen_labels: set[str] = set()
        checked_context: list[Binding] = []
        for binding in assumptions:
            if type(binding) is not Binding or not _valid_name(binding.label):
                raise ProofError("C002", "invalid assumption binding")
            if binding.label in seen_labels:
                raise ProofError("C003", "duplicate active assumption label")
            seen_labels.add(binding.label)
            checked_context.append(Binding(binding.label, validate_formula(binding.proposition)))
        checked_expected = None if expected is None else validate_formula(expected)
        axiom_table = dict(self._axioms)
        active: set[int] = set()
        nodes = 0

        def infer(current: object, context: tuple[Binding, ...], depth: int) -> tuple[Formula, frozenset[str]]:
            nonlocal nodes
            if depth > MAX_PROOF_DEPTH:
                raise ProofError("P010", "proof depth exceeds 40")
            if nodes >= MAX_PROOF_NODES:
                raise ProofError("P009", "proof node count exceeds 255")
            nodes += 1
            identity = id(current)
            if identity in active:
                raise ProofError("P011", "cyclic proof object")
            active.add(identity)
            try:
                if type(current) is Hyp:
                    if not _valid_name(current.label):
                        raise ProofError("C002", "invalid assumption label")
                    for binding in reversed(context):
                        if binding.label == current.label:
                            return binding.proposition, frozenset()
                    raise ProofError("P002", "unknown assumption label")

                if type(current) is AndIntro:
                    left, left_axioms = infer(current.left, context, depth + 1)
                    right, right_axioms = infer(current.right, context, depth + 1)
                    conclusion = And(left, right)
                    validate_formula(conclusion)
                    return conclusion, left_axioms | right_axioms

                if type(current) is AndElimLeft:
                    pair, used = infer(current.pair, context, depth + 1)
                    if type(pair) is not And:
                        raise ProofError("P003", "and elimination requires a conjunction")
                    return pair.left, used

                if type(current) is AndElimRight:
                    pair, used = infer(current.pair, context, depth + 1)
                    if type(pair) is not And:
                        raise ProofError("P003", "and elimination requires a conjunction")
                    return pair.right, used

                if type(current) is ImpIntro:
                    if not _valid_name(current.label):
                        raise ProofError("C002", "invalid assumption label")
                    antecedent = validate_formula(current.antecedent)
                    if len(context) >= MAX_CONTEXT:
                        raise ProofError("C001", "assumption context exceeds 32 entries")
                    if any(binding.label == current.label for binding in context):
                        raise ProofError("C003", "duplicate active assumption label")
                    body, used = infer(
                        current.body,
                        context + (Binding(current.label, antecedent),),
                        depth + 1,
                    )
                    conclusion = Imp(antecedent, body)
                    validate_formula(conclusion)
                    return conclusion, used

                if type(current) is ImpElim:
                    function, function_axioms = infer(current.function, context, depth + 1)
                    argument, argument_axioms = infer(current.argument, context, depth + 1)
                    if type(function) is not Imp:
                        raise ProofError("P004", "implication elimination requires an implication")
                    if argument != function.antecedent:
                        raise ProofError("P005", "implication antecedent mismatch")
                    return function.consequent, function_axioms | argument_axioms

                if type(current) is ExFalso:
                    target = validate_formula(current.target)
                    absurd, used = infer(current.absurd, context, depth + 1)
                    if type(absurd) is not Bottom:
                        raise ProofError("P006", "explosion requires bottom")
                    return target, used

                if type(current) is Axiom:
                    if not _valid_name(current.name) or current.name not in axiom_table:
                        raise ProofError("P007", "axiom is not in the trusted registry")
                    return validate_formula(axiom_table[current.name]), frozenset((current.name,))

                raise ProofError("P001", "unsupported proof object")
            finally:
                active.remove(identity)

        conclusion, used = infer(proof, tuple(checked_context), 1)
        validate_formula(conclusion)
        if checked_expected is not None and conclusion != checked_expected:
            raise ProofError("P008", "conclusion does not match expected proposition")
        return Theorem(conclusion, tuple(checked_context), tuple(sorted(used)), nodes)
