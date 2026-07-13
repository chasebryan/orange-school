#!/usr/bin/env python3
"""Run one deterministic Lumen semantics example."""

from semantics import Add, BoolLit, Effect, Emit, If, IntLit, Let, Seq, Var, run


program = Let(
    "base",
    Add(IntLit(20), IntLit(1)),
    Seq(
        Emit(Var("base")),
        If(
            BoolLit(False),
            Seq(Emit(IntLit(999)), IntLit(0)),
            Add(Var("base"), IntLit(1)),
        ),
    ),
)
result = run(program)
effects = ",".join(sorted(effect.value for effect in result.potential_effects))
print(f"type: {result.type.value}")
print(f"potential effects: {effects}")
print(f"value: {result.value}")
print(f"outputs: {result.outputs}")
print(f"steps: {result.steps}")

assert result.potential_effects == frozenset((Effect.EMIT,))
