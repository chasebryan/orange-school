#!/usr/bin/env python3
"""Worked evidence-closure bundle for an independent packet codec."""

from __future__ import annotations

from dataclasses import replace
import sys

from claim_model import (
    Assumption,
    AssumptionState,
    AssuranceBundle,
    Claim,
    EvidenceFact,
    EvidenceKind,
    EvidenceResult,
    ReviewState,
    TrustedComponent,
    evaluate_bundle,
    make_evidence,
    render_evaluation,
)


ZERO_DIGEST = "0" * 64
ONE_DIGEST = "1" * 64
TWO_DIGEST = "2" * 64
THREE_DIGEST = "3" * 64


def make_bundle() -> AssuranceBundle:
    assumptions = (
        Assumption(
            "profile-fixed",
            "the assessed codec profile is packet-codec-v1 with a 1024-byte input cap",
            "codec owner",
            "profile identifier or input cap differs from the recorded assessment",
            AssumptionState.CONFIRMED,
        ),
        Assumption(
            "vectors-authoritative",
            "the frozen vector manifest is the selected source for this exercise",
            "assessment owner",
            "manifest provenance or selected revision cannot be reproduced",
            AssumptionState.CONFIRMED,
        ),
    )
    trusted = (
        TrustedComponent(
            "python-runtime",
            "executes the deterministic vector harness and claim checker",
            "CPython 3.11 teaching envelope",
            ZERO_DIGEST,
            ReviewState.REVIEWED,
        ),
        TrustedComponent(
            "vector-manifest",
            "defines the finite codec inputs and expected bytes",
            "packet-codec-v1 frozen manifest",
            ONE_DIGEST,
            ReviewState.REVIEWED,
        ),
    )
    vectors = make_evidence(
        kind=EvidenceKind.TEST,
        producer="offline vector harness",
        subject="packet-codec-v1 encode and decode functions",
        method="compare 24 frozen cases and reject five malformed records",
        result=EvidenceResult.PASS,
        artifact_sha256=TWO_DIGEST,
        assumption_ids=("profile-fixed", "vectors-authoritative"),
        tcb_ids=("python-runtime", "vector-manifest"),
        facts=(
            EvidenceFact("invalid-cases", "5"),
            EvidenceFact("valid-cases", "24"),
        ),
    )
    inspection = make_evidence(
        kind=EvidenceKind.INSPECTION,
        producer="bounded review worksheet",
        subject="packet-codec-v1 length checks",
        method="trace each length read to a dominating 1024-byte bound check",
        result=EvidenceResult.PASS,
        artifact_sha256=THREE_DIGEST,
        assumption_ids=("profile-fixed",),
        tcb_ids=("python-runtime",),
        facts=(EvidenceFact("reviewed-sites", "3"),),
    )
    integration = make_evidence(
        kind=EvidenceKind.TEST,
        producer="offline round-trip harness",
        subject="packet-codec-v1 bounded profile integration",
        method="encode then decode every frozen valid case under the exact profile",
        result=EvidenceResult.PASS,
        artifact_sha256="4" * 64,
        assumption_ids=("profile-fixed", "vectors-authoritative"),
        tcb_ids=("python-runtime", "vector-manifest"),
        facts=(EvidenceFact("round-trips", "24"),),
    )
    claims = (
        Claim(
            "bounds-claim",
            "all three decoded length fields are rejected above the declared profile cap",
            "packet-codec-v1 length checks",
            "three inspected length reads in artifact digest 3333... under the 1024-byte profile",
            ("allocator behavior and memory safety are excluded", "other codec profiles are excluded"),
            ("profile-fixed",),
            (inspection.identity,),
            (),
            ("python-runtime",),
        ),
        Claim(
            "vector-claim",
            "the recorded codec artifact matches every expected result in the frozen manifest",
            "packet-codec-v1 encode and decode functions",
            "24 valid and five invalid frozen manifest cases",
            ("inputs absent from the manifest are excluded", "semantic equivalence to another codec is excluded"),
            ("profile-fixed", "vectors-authoritative"),
            (vectors.identity,),
            (),
            ("python-runtime", "vector-manifest"),
        ),
        Claim(
            "profile-claim",
            "the recorded bounded profile passes its declared vector, bound, and round-trip obligations",
            "packet-codec-v1 bounded profile",
            "exact recorded artifacts, profile, harnesses, and finite manifest",
            ("general correctness is excluded", "security and production approval are excluded"),
            ("profile-fixed", "vectors-authoritative"),
            (integration.identity,),
            ("bounds-claim", "vector-claim"),
            ("python-runtime", "vector-manifest"),
        ),
    )
    return AssuranceBundle(
        "packet codec assurance teaching bundle",
        assumptions,
        trusted,
        (integration, inspection, vectors),
        claims,
    )


def scenario_bundle(scenario: str) -> AssuranceBundle:
    bundle = make_bundle()
    if scenario == "pass":
        return bundle
    if scenario == "failed-integration":
        original = bundle.evidence[0]
        failed = make_evidence(
            kind=original.kind,
            producer=original.producer,
            subject=original.subject,
            method=original.method,
            result=EvidenceResult.FAIL,
            artifact_sha256=original.artifact_sha256,
            assumption_ids=original.assumption_ids,
            tcb_ids=original.tcb_ids,
            facts=original.facts,
        )
        claims = tuple(
            replace(claim, evidence_ids=(failed.identity,))
            if claim.identifier == "profile-claim"
            else claim
            for claim in bundle.claims
        )
        return replace(bundle, evidence=(failed,) + bundle.evidence[1:], claims=claims)
    if scenario == "missing-integration":
        claims = tuple(
            replace(claim, evidence_ids=())
            if claim.identifier == "profile-claim"
            else claim
            for claim in bundle.claims
        )
        return replace(bundle, claims=claims)
    if scenario == "unreviewed-runtime":
        trusted = tuple(
            replace(component, review_state=ReviewState.UNREVIEWED)
            if component.identifier == "python-runtime"
            else component
            for component in bundle.trusted_components
        )
        return replace(bundle, trusted_components=trusted)
    raise ValueError(
        "scenario must be pass, failed-integration, missing-integration, or unreviewed-runtime"
    )


def main(argv: tuple[str, ...] | None = None) -> int:
    arguments = tuple(sys.argv[1:] if argv is None else argv)
    if len(arguments) > 1:
        print("usage: claim_worked.py [scenario]", file=sys.stderr)
        return 64
    scenario = arguments[0] if arguments else "pass"
    try:
        bundle = scenario_bundle(scenario)
    except ValueError as error:
        print(f"claim_worked: {error}", file=sys.stderr)
        return 64
    evaluation = evaluate_bundle(bundle)
    print(render_evaluation(bundle, evaluation))
    return {
        "SUPPORTED": 0,
        "UNSUPPORTED": 3,
        "REFUTED": 4,
        "INVALID": 5,
    }[evaluation.status.value]


if __name__ == "__main__":
    raise SystemExit(main())
