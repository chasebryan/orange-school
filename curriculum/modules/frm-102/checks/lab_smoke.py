#!/usr/bin/env python3
"""Portable smoke checks for the bounded teaching proof kernel."""

from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
EXAMPLES = HERE.parent / "examples"
sys.path.insert(0, str(EXAMPLES))

from proof_kernel import (  # noqa: E402
    MAX_AXIOMS,
    And,
    AndElimLeft,
    AndElimRight,
    AndIntro,
    Atom,
    Axiom,
    AxiomSpec,
    Binding,
    Bottom,
    ExFalso,
    Hyp,
    Imp,
    ImpElim,
    ImpIntro,
    Kernel,
    MAX_FORMULA_NODES,
    ProofError,
    validate_formula,
)


def expect(code: str, action) -> None:
    try:
        action()
    except ProofError as exc:
        assert exc.code == code, (exc.code, exc.message)
        assert str(exc) == f"{exc.code}: {exc.message}"
    else:
        raise AssertionError(f"expected {code}")


A = Atom("A")
B = Atom("B")
C = Atom("C")


# Every rule, closed proof replay, and deterministic evidence.
kernel = Kernel()
projection = ImpIntro("ab", And(A, B), AndElimLeft(Hyp("ab")))
theorem = kernel.check(projection, Imp(And(A, B), A))
assert theorem.axioms_used == ()
assert theorem == kernel.check(projection, Imp(And(A, B), A))

swap = ImpIntro(
    "ab",
    And(A, B),
    AndIntro(AndElimRight(Hyp("ab")), AndElimLeft(Hyp("ab"))),
)
assert kernel.check(swap).conclusion == Imp(And(A, B), And(B, A))

apply_identity = ImpElim(ImpIntro("x", A, Hyp("x")), Hyp("given"))
assert kernel.check(apply_identity, A, (Binding("given", A),)).conclusion == A
assert kernel.check(ExFalso(C, Hyp("impossible")), C, (Binding("impossible", Bottom()),)).conclusion == C

# Axioms are selected by an immutable registry and only used entries are listed.
trusted = Kernel((AxiomSpec("ready", A), AxiomSpec("unused", B)))
trusted_result = trusted.check(Axiom("ready"), A)
assert trusted_result.axioms_used == ("ready",)
assert tuple(item.name for item in trusted.axiom_inventory) == ("ready", "unused")
expect("P007", lambda: trusted.check(Axiom("missing")))

# Rule failures and malformed host objects are rejected stably.
expect("P002", lambda: kernel.check(Hyp("free")))
expect("P003", lambda: kernel.check(AndElimLeft(ImpIntro("x", A, Hyp("x")))))
expect("P004", lambda: kernel.check(ImpElim(Hyp("a"), Hyp("a")), assumptions=(Binding("a", A),)))
expect(
    "P005",
    lambda: kernel.check(
        ImpElim(ImpIntro("x", A, Hyp("x")), Hyp("b")),
        assumptions=(Binding("b", B),),
    ),
)
expect("P006", lambda: kernel.check(ExFalso(C, Hyp("a")), assumptions=(Binding("a", A),)))
expect("P008", lambda: kernel.check(projection, Imp(And(A, B), B)))
expect("P001", lambda: kernel.check(object()))
expect("F001", lambda: validate_formula(object()))
expect("F002", lambda: validate_formula(Atom("not-ascii-é")))

# Cycles created by bypassing frozen dataclasses still fail before recursion.
cyclic_proof = AndElimLeft(Hyp("a"))
object.__setattr__(cyclic_proof, "pair", cyclic_proof)
expect("P011", lambda: kernel.check(cyclic_proof, assumptions=(Binding("a", A),)))
cyclic_formula = And(A, B)
object.__setattr__(cyclic_formula, "left", cyclic_formula)
expect("F004", lambda: validate_formula(cyclic_formula))

# Formula depth: an atom is depth 1; each implication adds one.
def deep_formula(depth: int):
    result = A
    for _ in range(depth - 1):
        result = Imp(A, result)
    return result


deep64 = deep_formula(64)
assert kernel.check(Hyp("deep"), deep64, (Binding("deep", deep64),)).conclusion == deep64
expect("F003", lambda: validate_formula(deep_formula(65)))

# Exactly 255 explicit formula visits are feasible at shallow depth. A binary
# wrapper attempts visit 256 before its complete 257-node object is accepted.
def full_formula(level: int):
    if level == 0:
        return A
    return And(full_formula(level - 1), full_formula(level - 1))


formula255 = full_formula(7)
assert MAX_FORMULA_NODES == 255
assert validate_formula(formula255) == formula255
expect("F005", lambda: validate_formula(Imp(A, formula255)))

# Elimination cannot hide an oversized or over-deep synthesized intermediate.
expect(
    "F005",
    lambda: kernel.check(
        AndElimLeft(AndIntro(Hyp("wide_left"), Hyp("wide_right"))),
        assumptions=(
            Binding("wide_left", formula255),
            Binding("wide_right", formula255),
        ),
    ),
)
expect(
    "F003",
    lambda: kernel.check(
        AndElimLeft(AndIntro(Hyp("deep_value"), Hyp("a"))),
        assumptions=(Binding("deep_value", deep64), Binding("a", A)),
    ),
)

# Exactly 255 proof nodes are feasible at shallow depth; the next visit fails.
def full_tree(level: int):
    if level == 0:
        return Hyp("a")
    return AndIntro(full_tree(level - 1), full_tree(level - 1))


tree255 = full_tree(7)
assert kernel.check(tree255, assumptions=(Binding("a", A),)).proof_nodes == 255
expect("P009", lambda: kernel.check(AndElimLeft(tree255), assumptions=(Binding("a", A),)))

# Proof depth 40 and 41 without approaching node or context caps.
def padded_atom(layers: int):
    proof = Hyp("a")
    for _ in range(layers):
        proof = AndElimLeft(AndIntro(proof, Hyp("a")))
    return proof


id_a = ImpIntro("z", A, Hyp("z"))
depth40 = ImpElim(id_a, padded_atom(19))
assert kernel.check(depth40, A, (Binding("a", A),)).conclusion == A
expect(
    "P010",
    lambda: kernel.check(ImpElim(id_a, depth40), A, (Binding("a", A),)),
)

# Context size 32 and 33 are isolated below formula/proof depth limits.
def nested_assumptions(count: int):
    proof = Hyp(f"h{count - 1}")
    for index in reversed(range(count)):
        proof = ImpIntro(f"h{index}", A, proof)
    return proof


assert kernel.check(nested_assumptions(32)).proof_nodes == 33
expect("C001", lambda: kernel.check(nested_assumptions(33)))

# Axiom-registry endpoint and one beyond.
axioms16 = tuple(AxiomSpec(f"ax{index}", A) for index in range(MAX_AXIOMS))
assert len(Kernel(axioms16).axiom_inventory) == 16
expect("A001", lambda: Kernel(axioms16 + (AxiomSpec("overflow", A),)))
expect("A003", lambda: Kernel((AxiomSpec("same", A), AxiomSpec("same", B))))

# Deliberate mutation / recovery: expected proposition, hypothesis, and axiom name.
for broken, code in (
    (lambda: kernel.check(projection, Imp(And(A, B), B)), "P008"),
    (lambda: kernel.check(ImpIntro("x", A, Hyp("y"))), "P002"),
    (lambda: trusted.check(Axiom("unused"), A), "P008"),
):
    expect(code, broken)
assert kernel.check(projection, Imp(And(A, B), A)).conclusion == Imp(And(A, B), A)
assert kernel.check(ImpIntro("x", A, Hyp("x"))).axioms_used == ()
assert trusted.check(Axiom("ready"), A).axioms_used == ("ready",)

print("frm-102 lab smoke: PASS")
