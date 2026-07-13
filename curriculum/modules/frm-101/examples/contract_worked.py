#!/usr/bin/env python3
"""Run one deterministic Aster total-correctness and refinement check."""

from contract_model import (
    BoolLit,
    Contract,
    Current,
    Le,
    State,
    countdown_contract,
    countdown_plan,
    verify,
    verify_refinement,
)


cases = tuple(State(value, 0) for value in range(8))
concrete = countdown_contract()
plan = countdown_plan()
result = verify(concrete, plan, cases, total=True)
abstract = Contract(
    assumption=concrete.assumption,
    precondition=BoolLit(True),
    postcondition=Le(Current("value"), Current("goal")),
)
refinement = verify_refinement(abstract, concrete, plan, cases)

print(f"correctness: {result.status} ({result.mode})")
print(f"cases: {result.considered} considered, {result.excluded} excluded")
print(f"loop steps: {result.total_steps}")
print(f"refinement: {refinement.status}")
