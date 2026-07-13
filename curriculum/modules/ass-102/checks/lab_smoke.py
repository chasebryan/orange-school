#!/usr/bin/env python3
"""Portable smoke check for the bounded ASS-102 Gauntlet model."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from adversary_model import (  # noqa: E402
    MAX_CASES,
    MAX_INPUT_BYTES,
    MAX_FINDINGS,
    MAX_MINIMIZE_EVALUATIONS,
    MAX_REFS,
    MAX_RELATIONS,
    MAX_RUN_EVALUATIONS,
    MAX_TEXT,
    MAX_THREATS,
    Case,
    Corpus,
    Finding,
    Outcome,
    Relation,
    RelationExpectation,
    SubjectKind,
    Threat,
    corpus_identity,
    minimize_counterexample,
    run_suite,
)
from adversary_worked import (  # noqa: E402
    correct_target,
    leading_zero_mutant,
    make_corpus,
    reference_system,
)


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect_error(error: type[BaseException], exact: str, action) -> None:
    try:
        action()
    except error as caught:
        require(str(caught) == exact, f"diagnostic changed: {caught!s}")
        return
    raise AssertionError(f"expected {error.__name__}: {exact}")


def endpoint_threats(count: int = MAX_THREATS) -> tuple[Threat, ...]:
    return tuple(
        Threat(f"t-{index}", SubjectKind.PARSER, "x", "y") for index in range(count)
    )


def endpoint_cases(count: int = MAX_CASES) -> tuple[Case, ...]:
    return tuple(
        Case(f"e-{index:02d}", SubjectKind.PARSER, b"P:0", "endpoint", ("t-0",))
        for index in range(count)
    )


def endpoint_relations(count: int = MAX_RELATIONS) -> tuple[Relation, ...]:
    return tuple(
        Relation(
            f"r-{index:02d}",
            "e-00",
            "e-01",
            RelationExpectation.SAME,
        )
        for index in range(count)
    )


def endpoint_oracle(data: bytes) -> Outcome:
    return Outcome(True, "ok", data.hex() or "empty")


def endpoint_target(data: bytes) -> Outcome:
    return Outcome(True, "ok", data.hex() or "empty")


def independent_corpus_identity(corpus: Corpus) -> str:
    """Reconstruct the documented canonical schema without production helpers."""
    payload = {
        "cases": [
            {
                "data_hex": item.data.hex(),
                "id": item.identifier,
                "kind": item.kind.value,
                "operator": item.operator,
                "origin": item.origin,
                "parent_id": item.parent_id,
                "threat_ids": list(item.threat_ids),
            }
            for item in corpus.cases
        ],
        "name": corpus.name,
        "relations": [
            {
                "expectation": item.expectation.value,
                "followup_id": item.followup_id,
                "id": item.identifier,
                "source_id": item.source_id,
            }
            for item in corpus.relations
        ],
        "schema": "ass-102-corpus-v1",
        "threats": [
            {
                "hypothesis": item.hypothesis,
                "id": item.identifier,
                "kind": item.kind.value,
                "oracle_basis": item.oracle_basis,
            }
            for item in corpus.threats
        ],
    }
    encoded = json.dumps(
        payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def check_worked_normal_and_mutant() -> None:
    corpus = make_corpus()
    report = run_suite(corpus, oracle=reference_system, target=correct_target)
    require(report.passed, "worked correct target failed")
    require(report.findings == (), "worked correct target has findings")
    require(len(report.observations) == 18, "worked case count changed")
    require(len(report.exercised_threats) == 5, "not every threat was exercised")
    require({case.kind for case in corpus.cases} == set(SubjectKind), "a subject kind is absent")
    require(report.corpus_identity == corpus_identity(corpus), "corpus identity changed in run")

    mutant = run_suite(corpus, oracle=reference_system, target=leading_zero_mutant)
    require(not mutant.passed, "leading-zero mutant survived")
    require(
        any(
            finding.code == "differential-mismatch" and finding.location == "p-leading-zero"
            for finding in mutant.findings
        ),
        "mutant differential counterexample changed",
    )
    require(
        any(
            finding.code == "metamorphic-violation" and finding.location == "canonical-decimal"
            for finding in mutant.findings
        ),
        "mutant metamorphic counterexample changed",
    )

    minimized = minimize_counterexample(
        b"P:07", lambda data: reference_system(data) != leading_zero_mutant(data)
    )
    require(minimized.data == b"P:07", "counterexample minimum changed")
    require(minimized.evaluations == 5 and minimized.one_minimal, "minimum evidence changed")


def check_identity_and_invalid_boundaries() -> None:
    corpus = make_corpus()
    require(
        corpus_identity(corpus) == independent_corpus_identity(corpus),
        "canonical identity disagrees with independent reconstruction",
    )
    changed_case = replace(corpus.cases[0], data=corpus.cases[0].data + b"x")
    changed = replace(corpus, cases=(changed_case,) + corpus.cases[1:])
    require(corpus_identity(changed) != corpus_identity(corpus), "changed bytes kept corpus identity")
    expect_error(TypeError, "corpus must be Corpus", lambda: corpus_identity("bad"))

    Case("input-endpoint", SubjectKind.PARSER, b"x" * MAX_INPUT_BYTES, "endpoint", ("t-0",))
    expect_error(
        ValueError,
        f"case data exceeds {MAX_INPUT_BYTES} bytes",
        lambda: Case(
            "input-overflow",
            SubjectKind.PARSER,
            b"x" * (MAX_INPUT_BYTES + 1),
            "endpoint",
            ("t-0",),
        ),
    )
    expect_error(
        TypeError,
        "case data must be bytes",
        lambda: Case("mutable-input", SubjectKind.PARSER, bytearray(b"x"), "endpoint", ("t-0",)),
    )
    expect_error(
        ValueError,
        "case threat_ids must be sorted and unique",
        lambda: Case("duplicate-ref", SubjectKind.PARSER, b"x", "endpoint", ("t-0", "t-0")),
    )
    expect_error(
        ValueError,
        "case parent_id and operator must be present together",
        lambda: Case("bad-parent", SubjectKind.PARSER, b"x", "endpoint", ("t-0",), "seed"),
    )


def check_exact_collection_endpoints() -> None:
    threats = endpoint_threats()
    cases = endpoint_cases()
    relations = endpoint_relations()
    corpus = Corpus("run-endpoint", threats, cases, relations)
    require(len(corpus.threats) == MAX_THREATS, "threat endpoint failed")
    require(len(corpus.cases) == MAX_CASES, "case endpoint failed")
    require(len(corpus.relations) == MAX_RELATIONS, "relation endpoint failed")
    report = run_suite(corpus, oracle=endpoint_oracle, target=endpoint_target)
    require(report.passed, "maximum static corpus failed")
    require(report.evaluations == MAX_RUN_EVALUATIONS == 64, "run evaluation endpoint changed")

    finding_cases = tuple(
        Case(f"f-{index:02d}", SubjectKind.PARSER, bytes((index,)), "endpoint", ("t-0",))
        for index in range(MAX_CASES)
    )
    finding_relations = tuple(
        Relation(f"fr-{index:02d}", "f-00", "f-01", RelationExpectation.SAME)
        for index in range(MAX_RELATIONS)
    )

    def noisy_oracle(data: bytes) -> Outcome:
        if data[0] >= 2:
            raise RuntimeError("bounded")
        return Outcome(data[0] == 0, "oracle", "left" if data[0] == 0 else "")

    def noisy_target(data: bytes) -> Outcome:
        if data[0] >= 2:
            raise SystemExit(0)
        return Outcome(data[0] == 1, "target", "right" if data[0] == 1 else "")

    finding_endpoint = run_suite(
        Corpus("finding-endpoint", (threats[0],), finding_cases, finding_relations),
        oracle=noisy_oracle,
        target=noisy_target,
    )
    require(len(finding_endpoint.findings) == MAX_FINDINGS == 94, "finding endpoint changed")

    expect_error(
        ValueError,
        f"corpus threats count must be in 1..{MAX_THREATS}",
        lambda: Corpus("threat-overflow", endpoint_threats(MAX_THREATS + 1), (cases[0],), ()),
    )
    expect_error(
        ValueError,
        f"corpus cases count must be in 1..{MAX_CASES}",
        lambda: Corpus(
            "case-overflow",
            (threats[0],),
            cases + (Case("e-32", SubjectKind.PARSER, b"P:0", "endpoint", ("t-0",)),),
            (),
        ),
    )
    expect_error(
        ValueError,
        f"corpus relations count must be in 0..{MAX_RELATIONS}",
        lambda: Corpus(
            "relation-overflow",
            (threats[0],),
            cases,
            relations
            + (Relation("r-16", "e-00", "e-01", RelationExpectation.SAME),),
        ),
    )

    Case("ref-endpoint", SubjectKind.PARSER, b"x", "endpoint", tuple(f"t-{i}" for i in range(MAX_REFS)))
    expect_error(
        ValueError,
        f"case threat_ids count must be in 1..{MAX_REFS}",
        lambda: Case(
            "ref-overflow",
            SubjectKind.PARSER,
            b"x",
            "endpoint",
            tuple(f"t-{i}" for i in range(MAX_REFS + 1)),
        ),
    )
    Threat("text-endpoint", SubjectKind.PARSER, "x" * MAX_TEXT, "y")
    expect_error(
        ValueError,
        f"threat hypothesis length must be in 1..{MAX_TEXT}",
        lambda: Threat("text-overflow", SubjectKind.PARSER, "x" * (MAX_TEXT + 1), "y"),
    )


def check_harness_fail_closed_paths() -> None:
    one = Corpus(
        "fail-closed",
        (Threat("t-0", SubjectKind.PARSER, "x", "y"),),
        (Case("e-00", SubjectKind.PARSER, b"P:0", "endpoint", ("t-0",)),),
        (),
    )

    def raising_target(data: bytes) -> Outcome:
        raise RuntimeError("target detail must not become a pass")

    def wrong_type(data: bytes):
        return "accepted"

    def exits_successfully(data: bytes) -> Outcome:
        raise SystemExit(0)

    exception_report = run_suite(one, oracle=endpoint_oracle, target=raising_target)
    require(
        exception_report.findings == (Finding("target-exception", "e-00", "RuntimeError"),),
        "target exception diagnostic changed",
    )
    type_report = run_suite(one, oracle=endpoint_oracle, target=wrong_type)
    require(
        type_report.findings == (Finding("target-outcome-type", "e-00", "str"),),
        "target type diagnostic changed",
    )
    exit_report = run_suite(one, oracle=endpoint_oracle, target=exits_successfully)
    require(
        exit_report.findings == (Finding("target-exception", "e-00", "SystemExit"),),
        "SystemExit escaped the fail-closed target boundary",
    )
    expect_error(
        ValueError,
        "oracle and target must be different callables",
        lambda: run_suite(one, oracle=endpoint_oracle, target=endpoint_oracle),
    )
    expect_error(
        ValueError,
        "case e-00 references unknown threat t-0",
        lambda: Corpus(
            "unknown-threat",
            (Threat("other", SubjectKind.PARSER, "x", "y"),),
            one.cases,
            (),
        ),
    )
    expect_error(
        ValueError,
        "case wrong-kind kind does not match every referenced threat",
        lambda: Corpus(
            "wrong-threat-kind",
            one.threats,
            (Case("wrong-kind", SubjectKind.POLICY, b"x", "endpoint", ("t-0",)),),
            (),
        ),
    )
    expect_error(
        ValueError,
        "case child-kind kind does not match parent parent-kind",
        lambda: Corpus(
            "wrong-parent-kind",
            (
                Threat("parser-threat", SubjectKind.PARSER, "x", "y"),
                Threat("policy-threat", SubjectKind.POLICY, "x", "y"),
            ),
            (
                Case(
                    "child-kind",
                    SubjectKind.POLICY,
                    b"x",
                    "mutation",
                    ("policy-threat",),
                    "parent-kind",
                    "derive",
                ),
                Case("parent-kind", SubjectKind.PARSER, b"x", "endpoint", ("parser-threat",)),
            ),
            (),
        ),
    )
    expect_error(
        ValueError,
        "relation bad references unknown followup",
        lambda: Corpus(
            "unknown-relation",
            one.threats,
            one.cases,
            (Relation("bad", "e-00", "missing", RelationExpectation.SAME),),
        ),
    )
    cycle_cases = (
        Case("cycle-a", SubjectKind.PARSER, b"x", "mutation", ("t-0",), "cycle-b", "derive"),
        Case("cycle-b", SubjectKind.PARSER, b"x", "mutation", ("t-0",), "cycle-a", "derive"),
    )
    expect_error(
        ValueError,
        "case lineage cycle at cycle-a",
        lambda: Corpus("lineage-cycle", one.threats, cycle_cases, ()),
    )

    minimum_endpoint = minimize_counterexample(
        b"x" * (MAX_INPUT_BYTES - 1), lambda data: True
    )
    require(
        minimum_endpoint.data == b""
        and minimum_endpoint.evaluations == MAX_MINIMIZE_EVALUATIONS
        and minimum_endpoint.one_minimal,
        "minimizer endpoint changed",
    )
    expect_error(
        ValueError,
        f"max_evaluations must be in 1..{MAX_MINIMIZE_EVALUATIONS}",
        lambda: minimize_counterexample(
            b"x", lambda data: True, max_evaluations=MAX_MINIMIZE_EVALUATIONS + 1
        ),
    )
    expect_error(
        ValueError,
        "initial input is not a counterexample",
        lambda: minimize_counterexample(b"x", lambda data: False),
    )
    expect_error(
        TypeError,
        "minimizer predicate must return an exact bool",
        lambda: minimize_counterexample(b"x", lambda data: 1),
    )

    relation_cases = (
        Case("reject-followup", SubjectKind.PARSER, b"f", "endpoint", ("t-0",)),
        Case("reject-source", SubjectKind.PARSER, b"s", "endpoint", ("t-0",)),
    )

    def rejects_one(data: bytes) -> Outcome:
        return Outcome(False, "rejected", "")

    def rejects_two(data: bytes) -> Outcome:
        return Outcome(False, "rejected", "")

    rejected_report = run_suite(
        Corpus(
            "rejected-source",
            one.threats,
            relation_cases,
            (
                Relation(
                    "rejected-relation",
                    "reject-source",
                    "reject-followup",
                    RelationExpectation.FOLLOWUP_REJECTS,
                ),
            ),
        ),
        oracle=rejects_one,
        target=rejects_two,
    )
    require(
        {finding.code for finding in rejected_report.findings}
        == {"oracle-relation-violation", "metamorphic-violation"},
        "rejected source incorrectly satisfied followup-rejects",
    )


def run_worked(mode: str, seed: str) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    env["PYTHONHASHSEED"] = seed
    return subprocess.run(
        [sys.executable, "-B", str(EXAMPLES / "adversary_worked.py"), mode],
        cwd=MODULE_ROOT,
        env=env,
        check=False,
        text=True,
        capture_output=True,
        timeout=10,
    )


def check_deliberate_failure_and_restoration() -> None:
    first = run_worked("pass", "0")
    failed = run_worked("mutant", "0")
    minimized = run_worked("minimize", "0")
    restored = run_worked("pass", "29")
    require(first.returncode == 0 and first.stderr == "", "initial pass process failed")
    require(failed.returncode == 4 and failed.stderr == "", "mutant did not fail with status 4")
    require(minimized.returncode == 4 and minimized.stderr == "", "minimum run status changed")
    require(restored.returncode == 0 and restored.stderr == "", "restored pass failed")
    require(first.stdout == restored.stdout, "hash-seed replay changed pass report")
    require("differential-mismatch at p-leading-zero" in failed.stdout, "failure evidence missing")
    require("minimized-hex: 503a3037" in minimized.stdout, "minimum evidence missing")
    require(first.stdout.endswith("release claim.\n"), "calibrated limitation missing")


def main() -> int:
    if sys.version_info < (3, 11):
        raise RuntimeError("ass-102 smoke requires Python 3.11 or newer")
    check_worked_normal_and_mutant()
    check_identity_and_invalid_boundaries()
    check_exact_collection_endpoints()
    check_harness_fail_closed_paths()
    check_deliberate_failure_and_restoration()
    print("ass-102 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
