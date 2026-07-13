#!/usr/bin/env python3
"""Portable boundary and adversarial evidence for ASS-104."""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import subprocess
import sys
import tempfile


sys.dont_write_bytecode = True
MODULE_ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = MODULE_ROOT / "examples"
sys.path.insert(0, str(EXAMPLES))

from lifecycle_model import (  # noqa: E402
    Event,
    LifecycleError,
    MAX_DOWNSTREAMS,
    MAX_EVENTS,
    MAX_EVIDENCE_ITEMS,
    MAX_ID_LENGTH,
    MAX_REVISION,
    MAX_TICK,
    TransitionRequest,
    canonical_record,
    endpoint_scenario,
    installation_decision,
    new_lifecycle,
    record_digest,
    support_decision,
    transition,
    validate_lifecycle,
)


class SpoofedAction:
    def __eq__(self, other: object) -> bool:
        return other == "publish_release"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AssertionError(message)


def expect(code: str, message: str, action) -> None:
    try:
        action()
    except LifecycleError as error:
        require(error.code == code, f"expected {code}, got {error.code}")
        require(error.message == message, f"message changed: {error.message!r}")
        require(str(error) == f"{code}: {message}", "rendered diagnostic changed")
        return
    raise AssertionError(f"expected {code}")


def request(action: str, tick: int, evidence: str, **payload: object) -> TransitionRequest:
    return TransitionRequest(action, tick, (evidence,), **payload)


def publish_base(product: str = "harbor"):
    state = new_lifecycle(product, release_revision=3, support_end_tick=90)
    state = transition(state, request("promote_candidate", 1, "candidate-proof"))
    return transition(state, request("publish_release", 2, "release-proof"))


def check_endpoint_and_canonical_record() -> None:
    state = endpoint_scenario()
    require(len(state.product_id) == MAX_ID_LENGTH, "identifier endpoint changed")
    require(state.release_revision == MAX_REVISION, "revision endpoint changed")
    require(state.min_installable_revision == MAX_REVISION, "rollback floor endpoint changed")
    require(len(state.events) == MAX_EVENTS, "event endpoint changed")
    require(state.events[-1].tick == MAX_TICK, "tick endpoint changed")
    require(len(state.events[0].evidence) == MAX_EVIDENCE_ITEMS, "evidence endpoint changed")
    require(len(state.notified_downstreams) == MAX_DOWNSTREAMS, "downstream endpoint changed")
    require(state.release_phase == "supported" and state.incident_phase == "closed", "final phases changed")
    require(state.claims == "revised" and state.migration_recorded, "recovery obligations changed")
    require(state.recovery_drills == 1, "recovery drill changed")

    first = canonical_record(state)
    second = canonical_record(state)
    require(first == second, "canonical rendering is not deterministic")
    require(record_digest(state) == record_digest(state), "record digest is not deterministic")
    require(first.startswith('{"advisory_id":"adv-2026-104"'), "canonical key ordering changed")

    require(installation_decision(state, 7).code == "rollback", "rollback was not denied")
    require(installation_decision(state, 8).allowed, "current revision was not allowed")
    require(support_decision(state, 9_999).allowed, "support endpoint was excluded")
    require(support_decision(state, MAX_TICK).code == "expired", "support expiry changed")

    expect(
        "B001",
        "event limit reached before the next retention",
        lambda: transition(state, request("recovery_drill", MAX_TICK, "extra-drill")),
    )
    expect(
        "T002",
        "transition tick must be an exact integer from 0 through 10000",
        lambda: transition(state, request("recovery_drill", MAX_TICK + 1, "extra-drill")),
    )


def check_illegal_transitions_and_restoration() -> None:
    state = new_lifecycle("harbor", release_revision=3, support_end_tick=90)
    expect(
        "S001",
        "publication requires a candidate without an incident",
        lambda: transition(state, request("publish_release", 1, "release-proof")),
    )
    state = transition(state, request("promote_candidate", 1, "candidate-proof"))
    require(support_decision(state, 1).code == "unpublished", "candidate became supported")
    state = transition(state, request("publish_release", 2, "release-proof"))
    require(state.release_phase == "supported", "publication restoration failed")

    state = transition(state, request("intake_report", 3, "report-proof"))
    state = transition(
        state,
        request("triage_report", 4, "triage-proof", severity="high"),
    )
    expect(
        "S002",
        "claims must be suspended before containment",
        lambda: transition(state, request("contain_release", 5, "containment-proof")),
    )
    state = transition(state, request("suspend_claims", 5, "claim-proof"))
    state = transition(state, request("contain_release", 6, "containment-proof"))
    require(state.release_phase == "contained", "containment restoration failed")

    expect(
        "S001",
        "release update requires a published advisory",
        lambda: transition(state, request("release_update", 7, "update-proof", new_revision=4)),
    )
    state = transition(
        state,
        request("publish_advisory", 7, "advisory-proof", advisory_id="adv-harbor-1"),
    )
    state = transition(state, request("release_update", 8, "update-proof", new_revision=4))
    state = transition(
        state,
        request("notify_downstreams", 9, "notice-proof", downstreams=("harbor-user",)),
    )
    expect(
        "S003",
        "updated release closure requires migration evidence and rollback prevention",
        lambda: transition(state, request("close_incident", 10, "closure-proof")),
    )
    state = transition(state, request("record_migration", 10, "migration-proof"))
    state = transition(state, request("raise_rollback_floor", 11, "rollback-proof"))
    state = transition(state, request("close_incident", 12, "closure-proof"))
    state = transition(state, request("recovery_drill", 13, "recovery-proof"))
    require(state.incident_phase == "closed" and state.recovery_drills == 1, "closure restoration failed")


def check_withdrawal_and_policy_boundaries() -> None:
    state = publish_base("quay")
    state = transition(state, request("intake_report", 3, "report-proof"))
    state = transition(state, request("triage_report", 4, "triage-proof", severity="critical"))
    state = transition(state, request("suspend_claims", 5, "claim-proof"))
    state = transition(state, request("contain_release", 6, "containment-proof"))
    state = transition(
        state,
        request("publish_advisory", 7, "advisory-proof", advisory_id="adv-quay-1"),
    )
    state = transition(state, request("withdraw_release", 8, "withdrawal-proof"))
    require(installation_decision(state, 3).code == "withdrawn", "withdrawn install passed")
    require(support_decision(state, 8).code == "withdrawn", "ordinary support survived withdrawal")
    state = transition(
        state,
        request("notify_downstreams", 9, "notice-proof", downstreams=("quay-user",)),
    )
    state = transition(state, request("close_incident", 10, "closure-proof"))
    require(state.incident_phase == "closed", "withdrawal incident did not close")
    state = transition(state, request("recovery_drill", 11, "drill-one"))
    state = transition(state, request("recovery_drill", 12, "drill-two"))
    expect(
        "B004",
        "recovery drill limit reached before retention",
        lambda: transition(state, request("recovery_drill", 13, "drill-three")),
    )


def check_malformed_and_exact_types() -> None:
    expect("L001", "unsupported lifecycle object", lambda: validate_lifecycle(object()))
    expect(
        "I001",
        "product identifier must be 1..32 lowercase ASCII identifier characters",
        lambda: new_lifecycle("UPPER"),
    )
    expect(
        "I001",
        "product identifier must be 1..32 lowercase ASCII identifier characters",
        lambda: new_lifecycle("p" * (MAX_ID_LENGTH + 1)),
    )
    expect(
        "I002",
        "revision fields must satisfy 1 <= compatible <= floor <= current <= 8",
        lambda: new_lifecycle("harbor", release_revision=True),
    )
    state = new_lifecycle("harbor")
    expect(
        "P001",
        "unsupported transition request",
        lambda: transition(state, object()),
    )
    expect(
        "T001",
        "transition action is outside the lifecycle vocabulary",
        lambda: transition(state, TransitionRequest(SpoofedAction(), 1, ("proof",))),
    )
    expect(
        "T002",
        "transition tick must be an exact integer from 0 through 10000",
        lambda: transition(state, TransitionRequest("promote_candidate", True, ("proof",))),
    )
    expect(
        "P002",
        "evidence must contain 1 through 4 identifiers",
        lambda: transition(state, TransitionRequest("promote_candidate", 1, ())),
    )
    expect(
        "P002",
        "evidence must contain 1 through 4 identifiers",
        lambda: transition(state, TransitionRequest("promote_candidate", 1, ("a", "b", "c", "d", "e"))),
    )
    expect(
        "P002",
        "evidence identifiers must be unique",
        lambda: transition(state, TransitionRequest("promote_candidate", 1, ("same", "same"))),
    )
    expect(
        "P003",
        "transition payload fields are invalid",
        lambda: transition(state, TransitionRequest("promote_candidate", 1, ("proof",), severity="high")),
    )
    expect(
        "D001",
        "candidate revision must be an exact integer from 1 through 8",
        lambda: installation_decision(state, False),
    )
    expect(
        "D002",
        "support query tick must be an exact integer from 0 through 10000",
        lambda: support_decision(state, MAX_TICK + 1),
    )

    forged_event = Event(1, 1, "promote_candidate", ("proof",), "release=candidate")
    forged = replace(state, events=(forged_event,), release_phase="draft")
    expect(
        "I012",
        "event history is inconsistent with lifecycle snapshot",
        lambda: validate_lifecycle(forged),
    )
    inconsistent = replace(state, release_phase="withdrawn")
    expect(
        "I011",
        "withdrawn release requires withdrawn claims and remediation",
        lambda: validate_lifecycle(inconsistent),
    )
    inconsistent_claim = replace(
        state,
        release_phase="supported",
        incident_phase="received",
        claims="revised",
    )
    expect(
        "I011",
        "received report requires the prior valid claim state",
        lambda: validate_lifecycle(inconsistent_claim),
    )
    bad_sequence = replace(
        state,
        events=(Event(True, 1, "promote_candidate", ("proof",), "release=candidate"),),
    )
    expect(
        "I010",
        "event sequences must be contiguous from one",
        lambda: validate_lifecycle(bad_sequence),
    )


def check_duplicates_and_revision_boundary() -> None:
    state = publish_base("harbor")
    state = transition(state, request("intake_report", 3, "report-proof"))
    state = transition(state, request("triage_report", 4, "triage-proof", severity="high"))
    state = transition(state, request("suspend_claims", 5, "claim-proof"))
    state = transition(state, request("contain_release", 6, "containment-proof"))
    state = transition(state, request("publish_advisory", 7, "advisory-proof", advisory_id="adv-harbor-2"))
    expect(
        "B002",
        "update revision must be the next revision within 1 through 8",
        lambda: transition(state, request("release_update", 8, "update-proof", new_revision=5)),
    )
    state = transition(state, request("release_update", 8, "update-proof", new_revision=4))
    expect(
        "B003",
        "one notification request exceeds four downstreams",
        lambda: transition(
            state,
            request(
                "notify_downstreams",
                9,
                "oversize-notice-proof",
                downstreams=("bad space", "bad space", "bad space", "bad space", "bad space"),
            ),
        ),
    )
    state = transition(state, request("notify_downstreams", 9, "notice-proof", downstreams=("user-a",)))
    expect(
        "N001",
        "downstream notification identifiers must be new and unique",
        lambda: transition(state, request("notify_downstreams", 10, "notice-proof-2", downstreams=("user-a",))),
    )
    expect(
        "B003",
        "downstream notification limit reached before retention",
        lambda: transition(
            state,
            request(
                "notify_downstreams",
                10,
                "notice-proof-3",
                downstreams=("user-b", "user-c", "user-d", "user-e"),
            ),
        ),
    )

    revision_edge = new_lifecycle("revision-edge", release_revision=MAX_REVISION)
    revision_edge = transition(revision_edge, request("promote_candidate", 1, "candidate-proof"))
    revision_edge = transition(revision_edge, request("publish_release", 2, "release-proof"))
    revision_edge = transition(revision_edge, request("intake_report", 3, "report-proof"))
    revision_edge = transition(revision_edge, request("triage_report", 4, "triage-proof", severity="high"))
    revision_edge = transition(revision_edge, request("suspend_claims", 5, "claim-proof"))
    revision_edge = transition(revision_edge, request("contain_release", 6, "containment-proof"))
    revision_edge = transition(
        revision_edge,
        request("publish_advisory", 7, "advisory-proof", advisory_id="adv-revision-edge"),
    )
    expect(
        "B002",
        "update revision must be the next revision within 1 through 8",
        lambda: transition(
            revision_edge,
            request("release_update", 8, "update-proof", new_revision=MAX_REVISION + 1),
        ),
    )


def check_worked_program() -> None:
    with tempfile.TemporaryDirectory(prefix="ass-104-smoke-") as temporary:
        result = subprocess.run(
            [sys.executable, "-B", str(EXAMPLES / "lifecycle_worked.py")],
            cwd=temporary,
            text=True,
            capture_output=True,
            timeout=10,
            check=False,
        )
        require(result.returncode == 0, f"worked lifecycle failed: {result.stderr}")
        require(result.stderr == "", "worked lifecycle wrote stderr")
        require("final release/incident: supported/closed" in result.stdout, "final state missing")
        require("events/downstreams/drills: 16/4/1" in result.stdout, "endpoint output missing")
        require("rollback revision 7: rollback" in result.stdout, "rollback output missing")
        require("current revision 8: allowed" in result.stdout, "current install output missing")
        require("no advisory was published and no downstream was contacted" in result.stdout, "effect boundary missing")
        require("not an Orange release, compatibility, support, or security claim" in result.stdout, "Orange limit missing")
        require(list(Path(temporary).iterdir()) == [], "worked example created an external artifact")


def main() -> int:
    check_endpoint_and_canonical_record()
    check_illegal_transitions_and_restoration()
    check_withdrawal_and_policy_boundaries()
    check_malformed_and_exact_types()
    check_duplicates_and_revision_boundary()
    check_worked_program()
    print("ass-104 lab smoke: PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
