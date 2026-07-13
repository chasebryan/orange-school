#!/usr/bin/env python3
"""Portable smoke check for the bounded Aster contract model."""

from __future__ import annotations

import os
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Callable


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from contract_model import (  # noqa: E402
    MAX_CASES,
    MAX_FORMULA_DEPTH,
    MAX_FORMULA_NODES,
    MAX_LOOP_STEPS,
    MAX_VALUE,
    Add,
    And,
    BoolLit,
    Contract,
    Current,
    Eq,
    IntLit,
    Le,
    LoopPlan,
    Lt,
    ModelError,
    Not,
    Old,
    Sort,
    State,
    Sub,
    countdown_contract,
    countdown_plan,
    evaluate,
    validate_cases,
    validate_formula,
    verify,
    verify_refinement,
)


class SmokeFailure(RuntimeError):
    pass


def require(condition: bool, message: str) -> None:
    if not condition:
        raise SmokeFailure(message)


def expect_error(
    code: str,
    action: Callable[[], object],
    message: str,
    exact_message: str | None = None,
) -> None:
    try:
        action()
    except ModelError as error:
        require(error.code == code, f"{message}: got {error.code}: {error.message}")
        if exact_message is not None:
            require(error.message == exact_message, f"{message}: message changed")
        return
    raise SmokeFailure(message)


def balanced_true(leaves: int):
    if leaves == 1:
        return BoolLit(True)
    left = leaves // 2
    return And(balanced_true(left), balanced_true(leaves - left))


def unrestricted_contract(postcondition=None) -> Contract:
    return Contract(
        assumption=BoolLit(True),
        precondition=Le(Current("goal"), Current("value")),
        postcondition=postcondition or Eq(Current("value"), Current("goal")),
    )


def check_formulas_and_resource_endpoints() -> None:
    endpoint = balanced_true(32)
    require(validate_formula(endpoint) == (Sort.BOOL, MAX_FORMULA_NODES), "63-node endpoint failed")
    expect_error(
        "F003",
        lambda: validate_formula(Not(endpoint)),
        "smallest constructible 64-node formula was accepted",
        "formula node count exceeds 63",
    )

    depth_endpoint = BoolLit(True)
    for _ in range(MAX_FORMULA_DEPTH - 1):
        depth_endpoint = Not(depth_endpoint)
    require(validate_formula(depth_endpoint)[1] == MAX_FORMULA_DEPTH, "depth-12 endpoint failed")
    expect_error(
        "F002",
        lambda: validate_formula(Not(depth_endpoint)),
        "depth-13 formula was accepted",
        "formula depth exceeds 12",
    )

    case_endpoint = tuple(State(value, 0) for value in range(MAX_CASES))
    require(len(validate_cases(case_endpoint)) == MAX_CASES, "16-case endpoint failed")
    expect_error(
        "C004",
        lambda: validate_cases(case_endpoint + (State(MAX_CASES, 0),)),
        "17-case tuple was accepted",
        "case count exceeds 16",
    )

    require(evaluate(Add(IntLit(MAX_VALUE - 1), IntLit(1)), State(0, 0), State(0, 0)) == MAX_VALUE,
            "arithmetic endpoint failed")
    require(evaluate(Sub(IntLit(-MAX_VALUE + 1), IntLit(1)), State(0, 0), State(0, 0)) == -MAX_VALUE,
            "negative arithmetic endpoint failed")
    expect_error(
        "R001",
        lambda: evaluate(Add(IntLit(MAX_VALUE), IntLit(1)), State(0, 0), State(0, 0)),
        "smallest arithmetic overflow was accepted",
        "formula arithmetic result is outside -32..32",
    )
    expect_error(
        "R001",
        lambda: evaluate(Sub(IntLit(-MAX_VALUE), IntLit(1)), State(0, 0), State(0, 0)),
        "smallest arithmetic underflow was accepted",
    )
    require(validate_formula(IntLit(MAX_VALUE))[0] is Sort.INT, "literal endpoint failed")
    require(validate_formula(IntLit(-MAX_VALUE))[0] is Sort.INT, "negative literal endpoint failed")
    expect_error("F005", lambda: validate_formula(IntLit(MAX_VALUE + 1)), "literal overflow accepted")
    expect_error("F005", lambda: validate_formula(IntLit(-MAX_VALUE - 1)), "literal underflow accepted")
    require(validate_cases((State(MAX_VALUE, -MAX_VALUE),))[0].value == MAX_VALUE,
            "state range endpoint failed")
    expect_error("C002", lambda: validate_cases((State(MAX_VALUE + 1, 0),)), "state one-beyond accepted")
    expect_error("C002", lambda: validate_cases((State(-MAX_VALUE - 1, 0),)), "state underflow accepted")

    idle_contract = Contract(BoolLit(True), BoolLit(True), BoolLit(True))
    for delta in (-8, 8):
        idle = verify(
            idle_contract,
            LoopPlan(BoolLit(False), delta, BoolLit(True), None),
            (State(0, 0),),
            total=False,
        )
        require(idle.status == "PASS", f"delta endpoint {delta} failed")
    for delta in (-9, 9, True):
        expect_error(
            "P002",
            lambda delta=delta: verify(
                idle_contract,
                LoopPlan(BoolLit(False), delta, BoolLit(True), None),
                (State(0, 0),),
                total=False,
            ),
            f"invalid delta {delta!r} was accepted",
        )

    step_endpoint = verify(
        unrestricted_contract(), countdown_plan(), (State(MAX_LOOP_STEPS, 0),), total=True
    )
    require(step_endpoint.total_steps == MAX_LOOP_STEPS, "16-step endpoint failed")
    expect_error(
        "R002",
        lambda: verify(
            unrestricted_contract(), countdown_plan(), (State(MAX_LOOP_STEPS + 1, 0),), total=True
        ),
        "smallest 17-step overflow was accepted",
        "loop step count exceeds 16",
    )


def check_correctness_assumptions_and_counterexamples() -> None:
    contract = countdown_contract()
    plan = countdown_plan()
    cases = tuple(State(value, 0) for value in range(16))
    total = verify(contract, plan, cases, total=True)
    partial = verify(contract, LoopPlan(plan.guard, plan.delta, plan.invariant, None), cases, total=False)
    require(total.status == "PASS" and total.considered == 16, "total-correctness cases failed")
    require(partial.status == "PASS" and partial.total_steps == total.total_steps,
            "partial-correctness check disagreed")
    expect_error(
        "P003",
        lambda: verify(contract, LoopPlan(plan.guard, plan.delta, plan.invariant, None), cases, total=True),
        "total check accepted a missing variant",
    )
    expect_error(
        "C006",
        lambda: verify(contract, plan, (State(-1, 0),), total=True),
        "vacuous proof was accepted",
        "assumptions and precondition select no cases",
    )

    assumed = Contract(
        assumption=Le(IntLit(0), Current("value")),
        precondition=Le(Current("goal"), Current("value")),
        postcondition=Eq(Current("value"), Current("goal")),
    )
    assumption_result = verify(assumed, plan, (State(-1, 0), State(2, 0)), total=True)
    require(assumption_result.considered == 1 and assumption_result.excluded == 1,
            "explicit assumption accounting changed")

    bad_post = verify(
        unrestricted_contract(Eq(Current("value"), IntLit(1))),
        plan,
        (State(2, 0),),
        total=True,
    )
    require(
        bad_post.status == "FAIL"
        and bad_post.counterexample is not None
        and bad_post.counterexample.phase == "postcondition"
        and bad_post.counterexample.initial == State(2, 0)
        and bad_post.counterexample.current == State(0, 0),
        "postcondition counterexample lost its witness",
    )

    bad_initial_invariant = LoopPlan(plan.guard, -1, Lt(Current("goal"), Current("value")), plan.variant)
    initial_failure = verify(unrestricted_contract(), bad_initial_invariant, (State(0, 0),), total=True)
    require(initial_failure.counterexample is not None and
            initial_failure.counterexample.phase == "invariant-initialization",
            "initial invariant failure was not reported")

    bad_preservation = LoopPlan(
        plan.guard,
        -1,
        Le(Add(Current("goal"), IntLit(1)), Current("value")),
        plan.variant,
    )
    preservation = verify(unrestricted_contract(), bad_preservation, (State(1, 0),), total=True)
    require(preservation.counterexample is not None and
            preservation.counterexample.phase == "invariant-preservation",
            "invariant-preservation counterexample missing")

    nondecreasing = LoopPlan(plan.guard, 1, BoolLit(True), plan.variant)
    variant = verify(unrestricted_contract(), nondecreasing, (State(1, 0),), total=True)
    require(variant.counterexample is not None and variant.counterexample.phase == "variant-decrease",
            "nondecreasing variant was accepted")

    expect_error(
        "R003",
        lambda: verify(
            Contract(BoolLit(True), BoolLit(True), BoolLit(True)),
            LoopPlan(BoolLit(True), 1, BoolLit(True), None),
            (State(MAX_VALUE, 0),),
            total=False,
        ),
        "state update overflow was accepted",
    )


def check_refinement_and_independent_oracle() -> None:
    concrete = countdown_contract()
    plan = countdown_plan()
    abstract = Contract(
        assumption=concrete.assumption,
        precondition=BoolLit(True),
        postcondition=Le(Current("value"), Current("goal")),
    )
    cases = tuple(State(value, 0) for value in range(16))
    refinement = verify_refinement(abstract, concrete, plan, cases)
    require(refinement.status == "PASS", "valid refinement failed")

    stronger = Contract(
        assumption=concrete.assumption,
        precondition=Lt(Current("goal"), Current("value")),
        postcondition=concrete.postcondition,
    )
    failed = verify_refinement(abstract, stronger, plan, cases)
    require(failed.counterexample is not None and failed.counterexample.phase == "stronger-precondition",
            "stronger concrete precondition was accepted")

    # Independent arithmetic oracle for the declared countdown overlap. It does
    # not call verify, _run_case, evaluate, or any production transition path.
    expected_steps = sum(range(16))
    expected_finals = tuple(State(0, 0) for _ in range(16))
    require(refinement.total_steps == expected_steps, "independent step oracle disagreed")
    require(
        refinement.final_states == expected_finals,
        "checker-produced final states disagree with the independent oracle",
    )


def check_invalid_inputs_cycle_and_deliberate_failure() -> None:
    expect_error("F001", lambda: validate_formula(True), "host Boolean was accepted as formula")
    expect_error("F005", lambda: validate_formula(IntLit(True)), "Boolean integer literal accepted")
    expect_error("F006", lambda: validate_formula(BoolLit(1)), "integer Boolean literal accepted")
    expect_error("F007", lambda: validate_formula(Current("missing")), "unknown field accepted")
    expect_error("F008", lambda: validate_formula(Add(BoolLit(True), IntLit(1))), "bad addition accepted")
    expect_error("F009", lambda: validate_formula(Eq(BoolLit(True), IntLit(1))), "mixed equality accepted")
    expect_error("F010", lambda: validate_formula(Le(BoolLit(True), IntLit(1))), "bad order accepted")
    expect_error("F011", lambda: validate_formula(And(BoolLit(True), IntLit(1))), "bad and accepted")
    expect_error("F012", lambda: validate_formula(Not(IntLit(1))), "bad not accepted")
    expect_error("C003", lambda: validate_cases([State(0, 0)]), "mutable case list accepted")
    expect_error("C002", lambda: validate_cases((State(True, 0),)), "Boolean state field accepted")

    cyclic = Not(BoolLit(True))
    object.__setattr__(cyclic, "value", cyclic)
    expect_error("F004", lambda: validate_formula(cyclic), "cyclic formula accepted")

    environment = dict(os.environ)
    environment.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"})
    with tempfile.TemporaryDirectory(prefix="frm-101-smoke-") as temporary_value:
        temporary = Path(temporary_value)
        worked = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "contract_worked.py")],
            cwd=temporary,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
        expected = (
            "correctness: PASS (total)\n"
            "cases: 8 considered, 0 excluded\n"
            "loop steps: 28\n"
            "refinement: PASS\n"
        )
        require(worked.returncode == 0, f"worked example failed: {worked.stderr}")
        require(worked.stdout == expected and worked.stderr == "", "worked output changed")

        probe = temporary / "probe.py"
        source_prefix = (
            "import sys\n"
            f"sys.path.insert(0, {str(EXAMPLES)!r})\n"
            "from contract_model import State, countdown_contract, countdown_plan, verify\n"
            "r = verify(countdown_contract(), countdown_plan(), tuple(State(v, 0) for v in range(8)), total=True)\n"
        )
        probe.write_text(source_prefix + "assert r.total_steps == 29\n", encoding="utf-8")
        failing = subprocess.run(
            [sys.executable, "-B", str(probe)], cwd=temporary, env=environment,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8, check=False
        )
        require(failing.returncode != 0 and "AssertionError" in failing.stderr,
                "deliberately wrong expectation did not fail observably")
        probe.write_text(source_prefix + "assert r.total_steps == 28\n", encoding="utf-8")
        restored = subprocess.run(
            [sys.executable, "-B", str(probe)], cwd=temporary, env=environment,
            text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=8, check=False
        )
        require(restored.returncode == 0 and restored.stdout == "" and restored.stderr == "",
                "restored expectation did not pass cleanly")


def main() -> int:
    check_formulas_and_resource_endpoints()
    check_correctness_assumptions_and_counterexamples()
    check_refinement_and_independent_oracle()
    check_invalid_inputs_cycle_and_deliberate_failure()
    print("frm-101 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (ModelError, SmokeFailure) as error:
        print(f"frm-101 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
