#!/usr/bin/env python3
"""Smoke-check the bounded CRY-101 security-requirements evaluator."""

from __future__ import annotations

from dataclasses import replace
import subprocess
import sys
import tempfile
from pathlib import Path


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from security_requirements import (  # noqa: E402
    MAX_ASSETS,
    MAX_TEXT_LENGTH,
    Asset,
    AttackerCapability,
    AttackerModel,
    MaterialKind,
    MaterialProperty,
    MaterialRequirement,
    SecurityGoal,
    ThreatModel,
    evaluate_model,
    render_evaluation,
)
from worked_case import make_model  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_error(error_type: type[BaseException], action, message: str) -> None:
    try:
        action()
    except error_type:
        return
    raise AssertionError(message)


def finding_codes(model: ThreatModel) -> set[str]:
    return {finding.code for finding in evaluate_model(model).findings}


def check_complete_model() -> None:
    model = make_model()
    evaluation = evaluate_model(model)
    require(evaluation.structurally_complete, "worked model should be structurally complete")
    require(evaluation.findings == (), "complete model unexpectedly has findings")
    rendered = render_evaluation(model, evaluation)
    require("review status: STRUCTURALLY-COMPLETE" in rendered, "complete status is missing")
    require("not a cryptographic security proof" in rendered, "security limitation is missing")
    require("findings: 0" in rendered, "finding count is wrong")


def check_incomplete_models() -> None:
    model = make_model()

    missing_freshness = replace(model, requirements=model.requirements[:-1])
    codes = finding_codes(missing_freshness)
    require("uncovered-goal" in codes, "missing asset goal was not found")
    require("unaddressed-capability" in codes, "unused attacker capability was not found")

    bad_nonce = replace(
        model.materials[1],
        properties=frozenset({MaterialProperty.PUBLIC}),
    )
    codes = finding_codes(replace(model, materials=(model.materials[0], bad_nonce, model.materials[2])))
    require("missing-nonce-uniqueness" in codes, "nonce reuse requirement was not found")

    contradictory_key = replace(
        model.materials[0],
        properties=frozenset(
            {
                MaterialProperty.SECRET,
                MaterialProperty.PUBLIC,
                MaterialProperty.UNPREDICTABLE,
            }
        ),
    )
    codes = finding_codes(
        replace(model, materials=(contradictory_key, model.materials[1], model.materials[2]))
    )
    require(
        "contradictory-material-properties" in codes,
        "contradictory material declaration was not found",
    )

    unknown_assumption = replace(
        model.requirements[0], assumption_ids=("not-declared",)
    )
    codes = finding_codes(
        replace(model, requirements=(unknown_assumption,) + model.requirements[1:])
    )
    require("unknown-assumption" in codes, "unknown assumption reference was not found")


def check_shape_boundaries_and_invalid_inputs() -> None:
    model = make_model()
    maximum_assets = tuple(
        Asset(
            f"asset-{index}",
            "bounded asset used to exercise the declared collection limit",
            frozenset({SecurityGoal.CONFIDENTIALITY}),
        )
        for index in range(MAX_ASSETS)
    )
    bounded = replace(model, assets=maximum_assets)
    require(len(bounded.assets) == MAX_ASSETS, "maximum asset count was rejected")

    expect_error(
        ValueError,
        lambda: replace(
            model,
            assets=maximum_assets
            + (
                Asset(
                    "one-too-many",
                    "asset beyond the declared bound",
                    frozenset({SecurityGoal.CONFIDENTIALITY}),
                ),
            ),
        ),
        "asset count above the bound was accepted",
    )
    Asset(
        "text-boundary",
        "x" * MAX_TEXT_LENGTH,
        frozenset({SecurityGoal.INTEGRITY}),
    )
    expect_error(
        ValueError,
        lambda: Asset(
            "text-too-long",
            "x" * (MAX_TEXT_LENGTH + 1),
            frozenset({SecurityGoal.INTEGRITY}),
        ),
        "text above the bound was accepted",
    )
    expect_error(
        TypeError,
        lambda: Asset(True, "invalid identifier type", frozenset({SecurityGoal.INTEGRITY})),
        "Boolean identifier was accepted",
    )
    expect_error(
        ValueError,
        lambda: Asset("Bad_ID", "invalid identifier form", frozenset({SecurityGoal.INTEGRITY})),
        "invalid identifier form was accepted",
    )
    expect_error(
        TypeError,
        lambda: Asset("wrong-goal", "invalid goal type", frozenset({"integrity"})),
        "raw string goal was accepted",
    )
    expect_error(
        ValueError,
        lambda: AttackerModel(
            frozenset(),
            "bounded adversary",
            ("endpoint compromise excluded",),
        ),
        "empty attacker capability set was accepted",
    )
    expect_error(
        TypeError,
        lambda: replace(model, assets=list(model.assets)),
        "list was accepted where a bounded tuple is required",
    )
    expect_error(
        TypeError,
        lambda: evaluate_model("not a model"),
        "non-model evaluator input was accepted",
    )
    expect_error(
        TypeError,
        lambda: MaterialRequirement(
            "bad-kind",
            "nonce",
            "exercise strict enum validation",
            frozenset({MaterialProperty.PUBLIC}),
            "local test",
            "one test",
            "reject",
        ),
        "raw string material kind was accepted",
    )
    expect_error(
        TypeError,
        lambda: MaterialRequirement(
            "bad-property",
            MaterialKind.NONCE,
            "exercise strict property validation",
            frozenset({"unique-within-scope"}),
            "local test",
            "one test",
            "reject",
        ),
        "raw string material property was accepted",
    )


def check_worked_program() -> None:
    with tempfile.TemporaryDirectory(prefix="cry-101-smoke-") as temporary:
        result = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "worked_case.py")],
            cwd=temporary,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
        require(result.returncode == 0, f"worked example failed: {result.stderr}")
        require(result.stderr == "", "worked example wrote a diagnostic")
        require("model: sealed-export teaching model" in result.stdout, "model name is missing")
        require("findings: 0" in result.stdout, "worked finding count is wrong")
        require(
            "review status: STRUCTURALLY-COMPLETE" in result.stdout,
            "worked review status is missing",
        )
        require("not a cryptographic security proof" in result.stdout, "worked limit is missing")
        evidence = Path(temporary) / "worked.stdout"
        evidence.write_text(result.stdout, encoding="utf-8")
        require(evidence.read_text(encoding="utf-8") == result.stdout, "temporary evidence changed")


def main() -> int:
    check_complete_model()
    check_incomplete_models()
    check_shape_boundaries_and_invalid_inputs()
    check_worked_program()
    print("cry-101 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"cry-101 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
