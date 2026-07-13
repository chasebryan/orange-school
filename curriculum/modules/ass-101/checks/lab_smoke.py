#!/usr/bin/env python3
"""Portable smoke check for the bounded ASS-101 claim model."""

from __future__ import annotations

from dataclasses import replace
import hashlib
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from claim_model import (  # noqa: E402
    MAX_ASSUMPTIONS,
    MAX_CLAIMS,
    MAX_CLOSURE_DEPTH,
    MAX_EVIDENCE,
    MAX_FACTS,
    MAX_REFS,
    MAX_TCB_ENTRIES,
    MAX_TEXT_LENGTH,
    Assumption,
    AssumptionState,
    AssuranceBundle,
    Claim,
    ClaimStatus,
    EvidenceFact,
    EvidenceKind,
    EvidenceRecord,
    EvidenceResult,
    Evaluation,
    ReviewState,
    TrustedComponent,
    canonical_evidence_identity,
    evaluate_bundle,
    make_evidence,
    render_evaluation,
)
from claim_worked import make_bundle  # noqa: E402


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def independent_evidence_identity(record: EvidenceRecord) -> str:
    payload = {
        "artifact_sha256": record.artifact_sha256,
        "assumption_ids": list(record.assumption_ids),
        "facts": [{"key": item.key, "value": item.value} for item in record.facts],
        "kind": record.kind.value,
        "method": record.method,
        "producer": record.producer,
        "result": record.result.value,
        "schema": "ass-101-evidence-v1",
        "subject": record.subject,
        "tcb_ids": list(record.tcb_ids),
    }
    encoded = json.dumps(
        payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def expect_error(error_type: type[BaseException], action, message: str) -> None:
    try:
        action()
    except error_type:
        return
    raise AssertionError(message)


def report(bundle: AssuranceBundle, identifier: str):
    return next(item for item in evaluate_bundle(bundle).reports if item.identifier == identifier)


def simple_evidence(result: EvidenceResult = EvidenceResult.PASS):
    return make_evidence(
        kind=EvidenceKind.TEST,
        producer="endpoint harness",
        subject="finite teaching subject",
        method="evaluate one deterministic case",
        result=result,
        artifact_sha256="a" * 64,
        tcb_ids=("checker",),
    )


def simple_tcb(index: int = 0) -> TrustedComponent:
    return TrustedComponent(
        f"checker-{index}" if index else "checker",
        "executes one finite check",
        f"teaching-{index}",
        f"{index % 16:x}" * 64,
        ReviewState.REVIEWED,
    )


def simple_claim(identifier: str, evidence_id: str, dependency_ids=()) -> Claim:
    return Claim(
        identifier,
        "the finite teaching subject matches its one declared case",
        "finite teaching subject",
        "one exact artifact and one deterministic input",
        ("all other artifacts are excluded",),
        (),
        (evidence_id,),
        dependency_ids,
        ("checker",),
    )


def check_worked_and_identity() -> None:
    bundle = make_bundle()
    evaluation = evaluate_bundle(bundle)
    require(evaluation.status is ClaimStatus.SUPPORTED, "worked bundle should be supported")
    require(evaluation.findings == (), "worked bundle has structural findings")
    require(all(item.status is ClaimStatus.SUPPORTED for item in evaluation.reports),
            "worked claim was not supported")
    record = bundle.evidence[0]
    require(record.identity == canonical_evidence_identity(record), "canonical identity changed")
    require(
        record.identity == independent_evidence_identity(record),
        "canonical identity disagrees with independent reconstruction",
    )
    duplicate = make_evidence(
        kind=record.kind,
        producer=record.producer,
        subject=record.subject,
        method=record.method,
        result=record.result,
        artifact_sha256=record.artifact_sha256,
        assumption_ids=record.assumption_ids,
        tcb_ids=record.tcb_ids,
        facts=record.facts,
    )
    require(duplicate.identity == record.identity, "equal evidence did not get equal identity")
    changed = make_evidence(
        kind=record.kind,
        producer=record.producer,
        subject=record.subject,
        method=record.method,
        result=EvidenceResult.FAIL,
        artifact_sha256=record.artifact_sha256,
        assumption_ids=record.assumption_ids,
        tcb_ids=record.tcb_ids,
        facts=record.facts,
    )
    require(changed.identity != record.identity, "changed evidence kept the old identity")


def check_exact_resource_endpoints() -> None:
    base = make_bundle()
    assumptions = tuple(
        Assumption(
            f"assumption-{index}",
            "endpoint assumption",
            "endpoint owner",
            "endpoint falsifier",
            AssumptionState.CONFIRMED,
        )
        for index in range(MAX_ASSUMPTIONS)
    )
    require(len(replace(base, assumptions=assumptions).assumptions) == MAX_ASSUMPTIONS,
            "assumption endpoint failed")
    expect_error(ValueError, lambda: replace(base, assumptions=assumptions + (assumptions[0],)),
                 "assumption overflow accepted")

    tcbs = tuple(simple_tcb(index + 1) for index in range(MAX_TCB_ENTRIES))
    require(len(replace(base, trusted_components=tcbs).trusted_components) == MAX_TCB_ENTRIES,
            "TCB endpoint failed")
    expect_error(ValueError, lambda: replace(base, trusted_components=tcbs + (tcbs[0],)),
                 "TCB overflow accepted")

    records = tuple(
        make_evidence(
            kind=EvidenceKind.TEST,
            producer="endpoint harness",
            subject=f"endpoint subject {index}",
            method="one deterministic comparison",
            result=EvidenceResult.PASS,
            artifact_sha256=f"{index % 16:x}" * 64,
            tcb_ids=("python-runtime",),
        )
        for index in range(MAX_EVIDENCE)
    )
    require(len(replace(base, evidence=records).evidence) == MAX_EVIDENCE,
            "evidence endpoint failed")
    expect_error(ValueError, lambda: replace(base, evidence=records + (records[0],)),
                 "evidence overflow accepted")

    claims = tuple(
        replace(base.claims[0], identifier=f"endpoint-claim-{index}")
        for index in range(MAX_CLAIMS)
    )
    require(len(replace(base, claims=claims).claims) == MAX_CLAIMS, "claim endpoint failed")
    expect_error(ValueError, lambda: replace(base, claims=claims + (claims[0],)),
                 "claim overflow accepted")

    facts = tuple(EvidenceFact(f"fact-{index:02d}", "endpoint") for index in range(MAX_FACTS))
    endpoint_record = make_evidence(
        kind=EvidenceKind.ANALYSIS,
        producer="endpoint producer",
        subject="endpoint subject",
        method="endpoint method",
        result=EvidenceResult.PASS,
        artifact_sha256="b" * 64,
        tcb_ids=("checker",),
        facts=facts,
    )
    require(len(endpoint_record.facts) == MAX_FACTS, "fact endpoint failed")
    expect_error(
        ValueError,
        lambda: EvidenceRecord(
            endpoint_record.identity,
            endpoint_record.kind,
            endpoint_record.producer,
            endpoint_record.subject,
            endpoint_record.method,
            endpoint_record.result,
            endpoint_record.artifact_sha256,
            (),
            ("checker",),
            facts + (EvidenceFact("overflow", "one beyond"),),
        ),
        "fact overflow accepted",
    )

    exclusions = tuple(f"excluded case {index:02d}" for index in range(MAX_REFS))
    endpoint_claim = replace(base.claims[0], exclusions=exclusions)
    require(len(endpoint_claim.exclusions) == MAX_REFS, "reference endpoint failed")
    expect_error(ValueError, lambda: replace(endpoint_claim, exclusions=exclusions + ("overflow",)),
                 "reference overflow accepted")
    Assumption("text-endpoint", "x" * MAX_TEXT_LENGTH, "owner", "falsifier",
               AssumptionState.CONFIRMED)
    expect_error(ValueError,
                 lambda: Assumption("text-overflow", "x" * (MAX_TEXT_LENGTH + 1),
                                    "owner", "falsifier", AssumptionState.CONFIRMED),
                 "text overflow accepted")


def chain_bundle(edges: int) -> AssuranceBundle:
    evidence = simple_evidence()
    claims = []
    for index in range(edges + 1):
        dependency = () if index == 0 else (f"chain-{index - 1}",)
        claims.append(simple_claim(f"chain-{index}", evidence.identity, dependency))
    return AssuranceBundle("closure endpoint", (), (simple_tcb(),), (evidence,), tuple(claims))


def check_closure_and_adversarial_records() -> None:
    endpoint = evaluate_bundle(chain_bundle(MAX_CLOSURE_DEPTH))
    require(endpoint.status is ClaimStatus.SUPPORTED, "closure depth-8 endpoint failed")
    require(
        len(endpoint.reports[-1].dependency_closure) == MAX_CLOSURE_DEPTH,
        "closure endpoint count changed",
    )
    overflow = evaluate_bundle(chain_bundle(MAX_CLOSURE_DEPTH + 1))
    require(overflow.status is ClaimStatus.INVALID, "closure depth-9 overflow accepted")
    require(any(item.code == "closure-depth-exceeded" for item in overflow.findings),
            "closure depth finding missing")

    base = make_bundle()
    first, second = base.claims[:2]
    cyclic = replace(
        base,
        claims=(
            replace(first, dependency_ids=(second.identifier,)),
            replace(second, dependency_ids=(first.identifier,)),
        ) + base.claims[2:],
    )
    cycle_result = evaluate_bundle(cyclic)
    require(cycle_result.status is ClaimStatus.INVALID, "dependency cycle accepted")
    require(any(item.code == "dependency-cycle" for item in cycle_result.findings),
            "cycle finding missing")

    unknown = replace(base.claims[0], dependency_ids=("missing-claim",))
    unknown_result = evaluate_bundle(replace(base, claims=(unknown,) + base.claims[1:]))
    require(any(item.code == "unknown-dependency" for item in unknown_result.findings),
            "unknown dependency accepted")

    tampered = replace(base.evidence[0], identity="sha256:" + "f" * 64)
    tampered_claims = tuple(
        replace(item, evidence_ids=(tampered.identity,))
        if item.identifier == "profile-claim"
        else item
        for item in base.claims
    )
    tampered_result = evaluate_bundle(
        replace(base, evidence=(tampered,) + base.evidence[1:], claims=tampered_claims)
    )
    require(tampered_result.status is ClaimStatus.INVALID, "tampered identity accepted")
    require(any(item.code == "evidence-identity-mismatch" for item in tampered_result.findings),
            "identity mismatch finding missing")

    missing_tcb = replace(base.claims[2], tcb_ids=("python-runtime",))
    closure_result = evaluate_bundle(replace(base, claims=base.claims[:2] + (missing_tcb,)))
    require(closure_result.status is ClaimStatus.INVALID, "incomplete TCB closure accepted")
    require(any(item.code == "tcb-closure-missing" for item in closure_result.findings),
            "TCB closure finding missing")


def check_fail_closed_statuses_and_noncomposition() -> None:
    evidence_pass = simple_evidence(EvidenceResult.PASS)
    evidence_fail = simple_evidence(EvidenceResult.FAIL)
    evidence_unknown = simple_evidence(EvidenceResult.INCONCLUSIVE)
    tcb = simple_tcb()
    passed = simple_claim("component-a", evidence_pass.identity)
    passed_b = simple_claim("component-b", evidence_pass.identity)
    composite = Claim(
        "composite",
        "the two finite components interact correctly",
        "component-a plus component-b",
        "one declared composition",
        ("all other compositions are excluded",),
        (),
        (),
        ("component-a", "component-b"),
        ("checker",),
    )
    noncomposing = AssuranceBundle(
        "non-composition case", (), (tcb,), (evidence_pass,), (passed, passed_b, composite)
    )
    composite_report = report(noncomposing, "composite")
    require(composite_report.status is ClaimStatus.UNSUPPORTED,
            "supported parts composed without direct evidence")
    require(composite_report.reasons ==
            ("no direct evidence; dependencies do not compose automatically",),
            "non-composition reason changed")

    failed = AssuranceBundle(
        "failed evidence", (), (tcb,), (evidence_fail,),
        (simple_claim("failed-claim", evidence_fail.identity),),
    )
    require(report(failed, "failed-claim").status is ClaimStatus.REFUTED,
            "failed direct evidence did not refute the claim")
    inconclusive = AssuranceBundle(
        "inconclusive evidence", (), (tcb,), (evidence_unknown,),
        (simple_claim("unknown-claim", evidence_unknown.identity),),
    )
    require(report(inconclusive, "unknown-claim").status is ClaimStatus.UNSUPPORTED,
            "inconclusive evidence supported a claim")

    assumption = Assumption(
        "environment-fixed", "the finite environment is fixed", "owner",
        "environment changes", AssumptionState.UNVERIFIED,
    )
    evidence_with_assumption = make_evidence(
        kind=EvidenceKind.TEST,
        producer="endpoint harness",
        subject="finite teaching subject",
        method="one deterministic case",
        result=EvidenceResult.PASS,
        artifact_sha256="c" * 64,
        assumption_ids=("environment-fixed",),
        tcb_ids=("checker",),
    )
    assumption_claim = replace(
        simple_claim("assumption-claim", evidence_with_assumption.identity),
        assumption_ids=("environment-fixed",),
    )
    assumption_bundle = AssuranceBundle(
        "unverified assumption", (assumption,), (tcb,),
        (evidence_with_assumption,), (assumption_claim,),
    )
    require(report(assumption_bundle, "assumption-claim").status is ClaimStatus.UNSUPPORTED,
            "unverified assumption supported a claim")

    unreviewed = replace(tcb, review_state=ReviewState.UNREVIEWED)
    tcb_bundle = AssuranceBundle(
        "unreviewed TCB", (), (unreviewed,), (evidence_pass,), (passed,)
    )
    require(report(tcb_bundle, "component-a").status is ClaimStatus.UNSUPPORTED,
            "unreviewed TCB supported a claim")


def check_deliberate_cli_failures_and_restored_passes() -> None:
    environment = dict(os.environ)
    environment.update({"PYTHONDONTWRITEBYTECODE": "1", "PYTHONHASHSEED": "0"})
    cases = (
        ("pass", 0, "overall: SUPPORTED"),
        ("failed-integration", 4, "claim profile-claim: REFUTED"),
        ("missing-integration", 3, "dependencies do not compose automatically"),
        ("unreviewed-runtime", 3, "a trusted component is not reviewed"),
    )
    with tempfile.TemporaryDirectory(prefix="ass-101-smoke-") as temporary:
        for scenario, expected_status, expected_text in cases:
            result = subprocess.run(
                [sys.executable, "-B", str(EXAMPLES / "claim_worked.py"), scenario],
                cwd=temporary,
                env=environment,
                text=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=8,
                check=False,
            )
            require(result.returncode == expected_status,
                    f"scenario {scenario} status was {result.returncode}, expected {expected_status}")
            require(result.stderr == "", f"scenario {scenario} wrote stderr: {result.stderr}")
            require(expected_text in result.stdout, f"scenario {scenario} exact result changed")
        restored = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "claim_worked.py"), "pass"],
            cwd=temporary,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=8,
            check=False,
        )
        require(restored.returncode == 0 and "overall: SUPPORTED" in restored.stdout,
                "restored pass failed")
        evidence_path = Path(temporary) / "restored.stdout"
        evidence_path.write_text(restored.stdout, encoding="utf-8")
        require(evidence_path.read_text(encoding="utf-8") == restored.stdout,
                "temporary evidence changed")


def check_invalid_host_shapes() -> None:
    expect_error(TypeError, lambda: evaluate_bundle("not a bundle"), "non-bundle accepted")
    expect_error(TypeError, lambda: replace(make_bundle(), claims=list(make_bundle().claims)),
                 "mutable claim list accepted")
    expect_error(TypeError,
                 lambda: Assumption("bad-state", "statement", "owner", "falsifier", "confirmed"),
                 "raw assumption state accepted")
    expect_error(ValueError,
                 lambda: TrustedComponent("bad-digest", "role", "version", "0" * 63,
                                          ReviewState.REVIEWED),
                 "short digest accepted")
    expect_error(ValueError,
                 lambda: replace(make_bundle().claims[0], exclusions=("z", "a")),
                 "noncanonical exclusions accepted")
    bundle = make_bundle()
    expect_error(
        ValueError,
        lambda: Evaluation((), ()),
        "empty forged evaluation was accepted",
    )
    expect_error(
        TypeError,
        lambda: Evaluation([], []),
        "mutable forged evaluation was accepted",
    )
    foreign_bundle = replace(
        bundle,
        claims=(replace(bundle.claims[0], evidence_ids=()),) + bundle.claims[1:],
    )
    expect_error(
        ValueError,
        lambda: render_evaluation(bundle, evaluate_bundle(foreign_bundle)),
        "evaluation from another bundle was rendered",
    )


def main() -> int:
    check_worked_and_identity()
    check_exact_resource_endpoints()
    check_closure_and_adversarial_records()
    check_fail_closed_statuses_and_noncomposition()
    check_deliberate_cli_failures_and_restored_passes()
    check_invalid_host_shapes()
    print("ass-101 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except Exception as error:
        print(f"ass-101 lab smoke: FAIL: {error}", file=sys.stderr)
        raise SystemExit(1)
