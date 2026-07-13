#!/usr/bin/env python3
"""Bounded release and incident lifecycle teaching model for ASS-104.

The model validates deterministic records and transition ordering. It does not
contact downstreams, publish an advisory, revoke a real artifact, validate an
external vulnerability report, or make an Orange release or support claim.
"""

from __future__ import annotations

from dataclasses import dataclass, replace
from hashlib import sha256
import json
import re


MAX_EVENTS = 16
MAX_REVISION = 8
MAX_EVIDENCE_ITEMS = 4
MAX_DOWNSTREAMS = 4
MAX_ID_LENGTH = 32
MAX_TICK = 10_000
MAX_RECOVERY_DRILLS = 2

RELEASE_PHASES = (
    "draft",
    "candidate",
    "supported",
    "contained",
    "withdrawn",
)
INCIDENT_PHASES = (
    "none",
    "received",
    "triaged",
    "contained",
    "advised",
    "remediated",
    "closed",
)
SEVERITIES = ("none", "low", "moderate", "high", "critical")
CLAIM_STATES = ("valid", "suspended", "revised", "withdrawn")
ACTIONS = (
    "promote_candidate",
    "publish_release",
    "intake_report",
    "triage_report",
    "suspend_claims",
    "contain_release",
    "publish_advisory",
    "release_update",
    "record_migration",
    "raise_rollback_floor",
    "notify_downstreams",
    "close_incident",
    "withdraw_release",
    "recovery_drill",
)

_IDENTIFIER = re.compile(r"^[a-z][a-z0-9-]{0,31}$")


class LifecycleError(ValueError):
    """Stable fail-closed lifecycle rejection."""

    def __init__(self, code: str, message: str):
        super().__init__(f"{code}: {message}")
        self.code = code
        self.message = message


@dataclass(frozen=True, slots=True)
class Event:
    sequence: int
    tick: int
    action: str
    evidence: tuple[str, ...]
    detail: str


@dataclass(frozen=True, slots=True)
class TransitionRequest:
    action: str
    tick: int
    evidence: tuple[str, ...]
    severity: str = "none"
    advisory_id: str = ""
    new_revision: int = 0
    downstreams: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class Lifecycle:
    product_id: str
    release_revision: int
    compatible_from: int
    min_installable_revision: int
    support_end_tick: int
    release_phase: str
    incident_phase: str
    severity: str
    claims: str
    advisory_id: str
    migration_recorded: bool
    notified_downstreams: tuple[str, ...]
    recovery_drills: int
    events: tuple[Event, ...]


@dataclass(frozen=True, slots=True)
class Decision:
    allowed: bool
    code: str
    reason: str


def _is_identifier(value: object) -> bool:
    return type(value) is str and _IDENTIFIER.fullmatch(value) is not None


def _require_identifier(value: object, label: str) -> str:
    if not _is_identifier(value):
        raise LifecycleError(
            "I001",
            f"{label} must be 1..{MAX_ID_LENGTH} lowercase ASCII identifier characters",
        )
    return value


def _validate_evidence(evidence: object) -> tuple[str, ...]:
    if (
        type(evidence) is not tuple
        or not 1 <= len(evidence) <= MAX_EVIDENCE_ITEMS
    ):
        raise LifecycleError("P002", "evidence must contain 1 through 4 identifiers")
    for identity in evidence:
        _require_identifier(identity, "evidence identifier")
    if len(set(evidence)) != len(evidence):
        raise LifecycleError("P002", "evidence identifiers must be unique")
    return evidence


def _validate_event(event: object, expected_sequence: int, prior_tick: int) -> Event:
    if type(event) is not Event:
        raise LifecycleError("I010", "events must contain exact Event records")
    if type(event.sequence) is not int or event.sequence != expected_sequence:
        raise LifecycleError("I010", "event sequences must be contiguous from one")
    if (
        type(event.tick) is not int
        or not 0 <= event.tick <= MAX_TICK
        or event.tick <= prior_tick
    ):
        raise LifecycleError("I010", "event ticks must be exact and strictly increasing")
    if type(event.action) is not str or event.action not in ACTIONS:
        raise LifecycleError("I010", "event action is outside the lifecycle vocabulary")
    _validate_evidence(event.evidence)
    if (
        type(event.detail) is not str
        or not 1 <= len(event.detail) <= 64
        or not event.detail.isascii()
        or not event.detail.isprintable()
    ):
        raise LifecycleError("I010", "event detail must be bounded printable ASCII")
    return event


def _validate_history_consistency(value: Lifecycle) -> None:
    """Replay retained action metadata and compare it with the snapshot.

    Evidence identifiers remain references to separately trusted artifacts,
    but the state, revision, notification count, and action details cannot
    contradict the retained transition sequence.
    """

    release_phase = "draft"
    incident_phase = "none"
    severity = "none"
    claims = "valid"
    advisory_id = ""
    revision = value.compatible_from
    floor = value.compatible_from
    migration_recorded = False
    notification_count = 0
    recovery_drills = 0

    def inconsistent() -> None:
        raise LifecycleError("I012", "event history is inconsistent with lifecycle snapshot")

    for event in value.events:
        if event.action == "promote_candidate":
            if release_phase != "draft" or incident_phase != "none" or event.detail != "release=candidate":
                inconsistent()
            release_phase = "candidate"
        elif event.action == "publish_release":
            if release_phase != "candidate" or incident_phase != "none" or event.detail != "release=supported":
                inconsistent()
            release_phase = "supported"
        elif event.action == "intake_report":
            if release_phase != "supported" or incident_phase != "none" or event.detail != "incident=received":
                inconsistent()
            incident_phase = "received"
        elif event.action == "triage_report":
            if release_phase != "supported" or incident_phase != "received" or not event.detail.startswith("severity="):
                inconsistent()
            candidate_severity = event.detail.removeprefix("severity=")
            if candidate_severity not in SEVERITIES[1:]:
                inconsistent()
            severity = candidate_severity
            incident_phase = "triaged"
        elif event.action == "suspend_claims":
            if incident_phase != "triaged" or claims != "valid" or event.detail != "claims=suspended":
                inconsistent()
            claims = "suspended"
        elif event.action == "contain_release":
            if release_phase != "supported" or incident_phase != "triaged" or claims != "suspended" or event.detail != "release=contained":
                inconsistent()
            release_phase = "contained"
            incident_phase = "contained"
        elif event.action == "publish_advisory":
            if release_phase != "contained" or incident_phase != "contained" or not event.detail.startswith("advisory="):
                inconsistent()
            candidate_advisory = event.detail.removeprefix("advisory=")
            if not _is_identifier(candidate_advisory):
                inconsistent()
            advisory_id = candidate_advisory
            incident_phase = "advised"
        elif event.action == "release_update":
            if release_phase != "contained" or incident_phase != "advised" or not event.detail.startswith("revision="):
                inconsistent()
            raw_revision = event.detail.removeprefix("revision=")
            if not raw_revision.isascii() or not raw_revision.isdecimal():
                inconsistent()
            candidate_revision = int(raw_revision)
            if (
                raw_revision != str(candidate_revision)
                or candidate_revision != revision + 1
                or candidate_revision > MAX_REVISION
            ):
                inconsistent()
            revision = candidate_revision
            release_phase = "supported"
            incident_phase = "remediated"
            claims = "revised"
            migration_recorded = False
        elif event.action == "record_migration":
            if release_phase != "supported" or incident_phase != "remediated" or claims != "revised" or migration_recorded or event.detail != "migration=recorded":
                inconsistent()
            migration_recorded = True
        elif event.action == "raise_rollback_floor":
            if release_phase != "supported" or incident_phase != "remediated" or not migration_recorded or floor >= revision or event.detail != f"floor={revision}":
                inconsistent()
            floor = revision
        elif event.action == "notify_downstreams":
            if incident_phase != "remediated" or release_phase not in ("supported", "withdrawn") or not event.detail.startswith("notified="):
                inconsistent()
            raw_count = event.detail.removeprefix("notified=")
            if not raw_count.isascii() or not raw_count.isdecimal():
                inconsistent()
            retained = int(raw_count)
            if raw_count != str(retained) or not 1 <= retained <= MAX_DOWNSTREAMS:
                inconsistent()
            notification_count += retained
            if notification_count > MAX_DOWNSTREAMS:
                inconsistent()
        elif event.action == "close_incident":
            if incident_phase != "remediated" or not notification_count or event.detail != "incident=closed":
                inconsistent()
            if release_phase == "supported" and not (
                claims == "revised" and migration_recorded and floor == revision
            ):
                inconsistent()
            if release_phase not in ("supported", "withdrawn"):
                inconsistent()
            incident_phase = "closed"
        elif event.action == "withdraw_release":
            if release_phase != "contained" or incident_phase != "advised" or claims != "suspended" or event.detail != "release=withdrawn":
                inconsistent()
            release_phase = "withdrawn"
            incident_phase = "remediated"
            claims = "withdrawn"
            migration_recorded = False
        elif event.action == "recovery_drill":
            if incident_phase != "closed" or event.detail != f"drill={recovery_drills + 1}" or recovery_drills >= MAX_RECOVERY_DRILLS:
                inconsistent()
            recovery_drills += 1
        else:
            inconsistent()

    actual = (
        value.release_phase,
        value.incident_phase,
        value.severity,
        value.claims,
        value.advisory_id,
        value.release_revision,
        value.min_installable_revision,
        value.migration_recorded,
        len(value.notified_downstreams),
        value.recovery_drills,
    )
    replayed = (
        release_phase,
        incident_phase,
        severity,
        claims,
        advisory_id,
        revision,
        floor,
        migration_recorded,
        notification_count,
        recovery_drills,
    )
    if actual != replayed:
        inconsistent()


def validate_lifecycle(value: object) -> Lifecycle:
    """Validate a complete immutable snapshot before use or serialization."""

    if type(value) is not Lifecycle:
        raise LifecycleError("L001", "unsupported lifecycle object")
    _require_identifier(value.product_id, "product identifier")
    revisions = (
        value.release_revision,
        value.compatible_from,
        value.min_installable_revision,
    )
    if any(type(revision) is not int for revision in revisions) or not (
        1
        <= value.compatible_from
        <= value.min_installable_revision
        <= value.release_revision
        <= MAX_REVISION
    ):
        raise LifecycleError("I002", "revision fields must satisfy 1 <= compatible <= floor <= current <= 8")
    if type(value.support_end_tick) is not int or not 1 <= value.support_end_tick <= MAX_TICK:
        raise LifecycleError("I003", "support end tick must be an exact integer from 1 through 10000")
    if type(value.release_phase) is not str or value.release_phase not in RELEASE_PHASES:
        raise LifecycleError("I004", "release phase is outside the lifecycle vocabulary")
    if type(value.incident_phase) is not str or value.incident_phase not in INCIDENT_PHASES:
        raise LifecycleError("I004", "incident phase is outside the lifecycle vocabulary")
    if type(value.severity) is not str or value.severity not in SEVERITIES:
        raise LifecycleError("I005", "severity is outside the lifecycle vocabulary")
    if type(value.claims) is not str or value.claims not in CLAIM_STATES:
        raise LifecycleError("I006", "claim state is outside the lifecycle vocabulary")
    if type(value.advisory_id) is not str or (
        value.advisory_id != "" and not _is_identifier(value.advisory_id)
    ):
        raise LifecycleError("I007", "advisory identifier is empty or a canonical identifier")
    if type(value.migration_recorded) is not bool:
        raise LifecycleError("I011", "migration marker must be an exact Boolean")
    if type(value.notified_downstreams) is not tuple or len(value.notified_downstreams) > MAX_DOWNSTREAMS:
        raise LifecycleError("I008", "downstream notification set exceeds four identifiers")
    for identity in value.notified_downstreams:
        _require_identifier(identity, "downstream identifier")
    if len(set(value.notified_downstreams)) != len(value.notified_downstreams):
        raise LifecycleError("I008", "downstream notification identifiers must be unique")
    if (
        type(value.recovery_drills) is not int
        or not 0 <= value.recovery_drills <= MAX_RECOVERY_DRILLS
    ):
        raise LifecycleError("I009", "recovery drill count must be an exact integer from 0 through 2")
    if type(value.events) is not tuple or len(value.events) > MAX_EVENTS:
        raise LifecycleError("I010", "event history must be a tuple of at most 16 records")
    prior_tick = -1
    for sequence, event in enumerate(value.events, start=1):
        checked_event = _validate_event(event, sequence, prior_tick)
        prior_tick = checked_event.tick

    if value.release_phase in ("draft", "candidate") and value.incident_phase != "none":
        raise LifecycleError("I011", "unpublished release cannot carry an incident")
    if value.release_phase == "contained" and value.incident_phase not in ("contained", "advised"):
        raise LifecycleError("I011", "contained release requires a contained or advised incident")
    if value.incident_phase in ("contained", "advised") and value.release_phase != "contained":
        raise LifecycleError("I011", "contained or advised incident requires a contained release")
    if value.release_phase == "withdrawn" and (
        value.incident_phase not in ("remediated", "closed") or value.claims != "withdrawn"
    ):
        raise LifecycleError("I011", "withdrawn release requires withdrawn claims and remediation")
    if value.claims == "withdrawn" and value.release_phase != "withdrawn":
        raise LifecycleError("I011", "withdrawn claims require a withdrawn release")
    if value.incident_phase == "none" and (
        value.severity != "none" or value.claims != "valid" or value.advisory_id != ""
    ):
        raise LifecycleError("I011", "no-incident state requires valid claims and no advisory")
    if value.incident_phase == "received" and value.severity != "none":
        raise LifecycleError("I011", "untriaged report cannot carry a severity")
    if value.incident_phase == "received" and value.claims != "valid":
        raise LifecycleError("I011", "received report requires the prior valid claim state")
    if value.incident_phase == "triaged" and value.claims not in ("valid", "suspended"):
        raise LifecycleError("I011", "triaged incident requires valid or suspended claims")
    if value.incident_phase not in ("none", "received") and value.severity == "none":
        raise LifecycleError("I011", "triaged incident requires a severity")
    if value.incident_phase in ("contained", "advised") and value.claims != "suspended":
        raise LifecycleError("I011", "containment requires suspended claims")
    if value.incident_phase in ("advised", "remediated", "closed") and value.advisory_id == "":
        raise LifecycleError("I011", "advised or later incident requires an advisory identifier")
    if value.incident_phase in ("none", "received", "triaged", "contained") and value.advisory_id != "":
        raise LifecycleError("I011", "advisory identifier appears before advisory publication")
    if value.incident_phase in ("remediated", "closed") and value.claims not in ("revised", "withdrawn"):
        raise LifecycleError("I011", "remediation requires revised or withdrawn claims")
    if value.migration_recorded and value.claims != "revised":
        raise LifecycleError("I011", "migration evidence requires a revised release claim")
    if value.notified_downstreams and value.incident_phase not in ("remediated", "closed"):
        raise LifecycleError("I011", "notifications require remediation or closure")
    if value.recovery_drills and value.incident_phase != "closed":
        raise LifecycleError("I011", "recovery drills require a closed incident")
    if value.incident_phase == "closed":
        if not value.notified_downstreams:
            raise LifecycleError("I011", "closed incident requires downstream notification evidence")
        if value.release_phase == "supported" and not (
            value.claims == "revised"
            and value.migration_recorded
            and value.min_installable_revision == value.release_revision
        ):
            raise LifecycleError("I011", "closed updated release requires migration and rollback evidence")
    _validate_history_consistency(value)
    return value


def new_lifecycle(
    product_id: str,
    *,
    release_revision: int = 1,
    support_end_tick: int = MAX_TICK,
) -> Lifecycle:
    """Start tracking a release revision without claiming earlier history."""

    snapshot = Lifecycle(
        product_id,
        release_revision,
        release_revision,
        release_revision,
        support_end_tick,
        "draft",
        "none",
        "none",
        "valid",
        "",
        False,
        (),
        0,
        (),
    )
    return validate_lifecycle(snapshot)


def _validate_request(value: object) -> TransitionRequest:
    if type(value) is not TransitionRequest:
        raise LifecycleError("P001", "unsupported transition request")
    if type(value.action) is not str or value.action not in ACTIONS:
        raise LifecycleError("T001", "transition action is outside the lifecycle vocabulary")
    if type(value.tick) is not int or not 0 <= value.tick <= MAX_TICK:
        raise LifecycleError("T002", "transition tick must be an exact integer from 0 through 10000")
    _validate_evidence(value.evidence)
    if type(value.severity) is not str or value.severity not in SEVERITIES:
        raise LifecycleError("P003", "transition payload fields are invalid")
    if type(value.advisory_id) is not str:
        raise LifecycleError("P003", "transition payload fields are invalid")
    if type(value.new_revision) is not int:
        raise LifecycleError("P003", "transition payload fields are invalid")
    if type(value.downstreams) is not tuple:
        raise LifecycleError("P003", "transition payload fields are invalid")
    if len(value.downstreams) > MAX_DOWNSTREAMS:
        raise LifecycleError("B003", "one notification request exceeds four downstreams")
    for identity in value.downstreams:
        _require_identifier(identity, "downstream identifier")
    return value


def _plain_payload(request: TransitionRequest) -> None:
    if (
        request.severity != "none"
        or request.advisory_id != ""
        or request.new_revision != 0
        or request.downstreams != ()
    ):
        raise LifecycleError("P003", "transition payload fields are invalid")


def _specific_payload(request: TransitionRequest, field: str) -> None:
    allowed = {
        "severity": request.severity != "none" and request.advisory_id == "" and request.new_revision == 0 and request.downstreams == (),
        "advisory": request.severity == "none" and request.advisory_id != "" and request.new_revision == 0 and request.downstreams == (),
        "revision": request.severity == "none" and request.advisory_id == "" and request.new_revision != 0 and request.downstreams == (),
        "downstreams": request.severity == "none" and request.advisory_id == "" and request.new_revision == 0 and request.downstreams != (),
    }
    if not allowed[field]:
        raise LifecycleError("P003", "transition payload fields are invalid")


def _require_state(condition: bool, message: str) -> None:
    if not condition:
        raise LifecycleError("S001", message)


def _record(
    snapshot: Lifecycle,
    request: TransitionRequest,
    detail: str,
    **updates: object,
) -> Lifecycle:
    if len(snapshot.events) >= MAX_EVENTS:
        raise LifecycleError("B001", "event limit reached before the next retention")
    prior_tick = snapshot.events[-1].tick if snapshot.events else -1
    if request.tick <= prior_tick:
        raise LifecycleError("T003", "transition tick must be greater than the previous event tick")
    event = Event(
        len(snapshot.events) + 1,
        request.tick,
        request.action,
        request.evidence,
        detail,
    )
    result = replace(snapshot, events=snapshot.events + (event,), **updates)
    return validate_lifecycle(result)


def transition(lifecycle: object, request: object) -> Lifecycle:
    """Apply one legal deterministic transition, or reject without a new state."""

    snapshot = validate_lifecycle(lifecycle)
    change = _validate_request(request)

    if change.action == "promote_candidate":
        _plain_payload(change)
        _require_state(snapshot.release_phase == "draft" and snapshot.incident_phase == "none", "candidate promotion requires a draft without an incident")
        return _record(snapshot, change, "release=candidate", release_phase="candidate")

    if change.action == "publish_release":
        _plain_payload(change)
        _require_state(snapshot.release_phase == "candidate" and snapshot.incident_phase == "none", "publication requires a candidate without an incident")
        return _record(snapshot, change, "release=supported", release_phase="supported")

    if change.action == "intake_report":
        _plain_payload(change)
        _require_state(snapshot.release_phase == "supported" and snapshot.incident_phase == "none", "report intake requires a supported release without an active incident")
        return _record(snapshot, change, "incident=received", incident_phase="received")

    if change.action == "triage_report":
        _specific_payload(change, "severity")
        _require_state(snapshot.release_phase == "supported" and snapshot.incident_phase == "received", "triage requires a received report")
        return _record(snapshot, change, f"severity={change.severity}", incident_phase="triaged", severity=change.severity)

    if change.action == "suspend_claims":
        _plain_payload(change)
        _require_state(snapshot.incident_phase == "triaged" and snapshot.claims == "valid", "claim suspension requires a triaged incident with valid claims")
        return _record(snapshot, change, "claims=suspended", claims="suspended")

    if change.action == "contain_release":
        _plain_payload(change)
        if snapshot.claims != "suspended":
            raise LifecycleError("S002", "claims must be suspended before containment")
        _require_state(snapshot.release_phase == "supported" and snapshot.incident_phase == "triaged", "containment requires a triaged supported release")
        return _record(snapshot, change, "release=contained", release_phase="contained", incident_phase="contained")

    if change.action == "publish_advisory":
        _specific_payload(change, "advisory")
        _require_identifier(change.advisory_id, "advisory identifier")
        _require_state(snapshot.release_phase == "contained" and snapshot.incident_phase == "contained", "advisory publication requires containment")
        return _record(snapshot, change, f"advisory={change.advisory_id}", incident_phase="advised", advisory_id=change.advisory_id)

    if change.action == "release_update":
        _specific_payload(change, "revision")
        _require_state(snapshot.release_phase == "contained" and snapshot.incident_phase == "advised", "release update requires a published advisory")
        if change.new_revision != snapshot.release_revision + 1 or change.new_revision > MAX_REVISION:
            raise LifecycleError("B002", "update revision must be the next revision within 1 through 8")
        return _record(
            snapshot,
            change,
            f"revision={change.new_revision}",
            release_revision=change.new_revision,
            release_phase="supported",
            incident_phase="remediated",
            claims="revised",
            migration_recorded=False,
        )

    if change.action == "record_migration":
        _plain_payload(change)
        _require_state(snapshot.release_phase == "supported" and snapshot.incident_phase == "remediated" and snapshot.claims == "revised" and not snapshot.migration_recorded, "migration recording requires one revised unrecorded update")
        return _record(snapshot, change, "migration=recorded", migration_recorded=True)

    if change.action == "raise_rollback_floor":
        _plain_payload(change)
        _require_state(snapshot.release_phase == "supported" and snapshot.incident_phase == "remediated" and snapshot.migration_recorded and snapshot.min_installable_revision < snapshot.release_revision, "rollback-floor change requires migration evidence for a newer revision")
        return _record(snapshot, change, f"floor={snapshot.release_revision}", min_installable_revision=snapshot.release_revision)

    if change.action == "notify_downstreams":
        _specific_payload(change, "downstreams")
        _require_state(snapshot.incident_phase == "remediated" and snapshot.release_phase in ("supported", "withdrawn"), "notification requires a remediated update or withdrawal")
        if len(set(change.downstreams)) != len(change.downstreams) or set(change.downstreams) & set(snapshot.notified_downstreams):
            raise LifecycleError("N001", "downstream notification identifiers must be new and unique")
        combined = snapshot.notified_downstreams + change.downstreams
        if len(combined) > MAX_DOWNSTREAMS:
            raise LifecycleError("B003", "downstream notification limit reached before retention")
        return _record(snapshot, change, f"notified={len(change.downstreams)}", notified_downstreams=combined)

    if change.action == "close_incident":
        _plain_payload(change)
        _require_state(snapshot.incident_phase == "remediated" and bool(snapshot.notified_downstreams), "closure requires remediation and downstream notification")
        if snapshot.release_phase == "supported" and not (
            snapshot.claims == "revised"
            and snapshot.migration_recorded
            and snapshot.min_installable_revision == snapshot.release_revision
        ):
            raise LifecycleError("S003", "updated release closure requires migration evidence and rollback prevention")
        _require_state(snapshot.release_phase in ("supported", "withdrawn"), "closure requires an updated or withdrawn release")
        return _record(snapshot, change, "incident=closed", incident_phase="closed")

    if change.action == "withdraw_release":
        _plain_payload(change)
        _require_state(snapshot.release_phase == "contained" and snapshot.incident_phase == "advised" and snapshot.claims == "suspended", "withdrawal requires a contained release, suspended claims, and an advisory")
        return _record(
            snapshot,
            change,
            "release=withdrawn",
            release_phase="withdrawn",
            incident_phase="remediated",
            claims="withdrawn",
            migration_recorded=False,
        )

    if change.action == "recovery_drill":
        _plain_payload(change)
        _require_state(snapshot.incident_phase == "closed", "recovery drill requires a closed incident")
        if snapshot.recovery_drills >= MAX_RECOVERY_DRILLS:
            raise LifecycleError("B004", "recovery drill limit reached before retention")
        return _record(snapshot, change, f"drill={snapshot.recovery_drills + 1}", recovery_drills=snapshot.recovery_drills + 1)

    raise LifecycleError("T001", "transition action is outside the lifecycle vocabulary")


def installation_decision(lifecycle: object, candidate_revision: object) -> Decision:
    """Evaluate local install policy; no installation is performed."""

    snapshot = validate_lifecycle(lifecycle)
    if type(candidate_revision) is not int or not 1 <= candidate_revision <= MAX_REVISION:
        raise LifecycleError("D001", "candidate revision must be an exact integer from 1 through 8")
    if snapshot.release_phase == "withdrawn":
        return Decision(False, "withdrawn", "the tracked release was withdrawn")
    if candidate_revision < snapshot.min_installable_revision:
        return Decision(False, "rollback", "candidate revision is below the rollback floor")
    if candidate_revision < snapshot.compatible_from:
        return Decision(False, "incompatible", "candidate revision is outside the compatibility policy")
    if candidate_revision > snapshot.release_revision:
        return Decision(False, "future", "candidate revision is not represented by this record")
    if snapshot.release_phase != "supported" or snapshot.claims not in ("valid", "revised"):
        return Decision(False, "lifecycle", "release state does not permit installation")
    return Decision(True, "allowed", "candidate revision satisfies this local policy record")


def support_decision(lifecycle: object, at_tick: object) -> Decision:
    """Evaluate the recorded support window without promising external service."""

    snapshot = validate_lifecycle(lifecycle)
    if type(at_tick) is not int or not 0 <= at_tick <= MAX_TICK:
        raise LifecycleError("D002", "support query tick must be an exact integer from 0 through 10000")
    if snapshot.release_phase == "withdrawn":
        return Decision(False, "withdrawn", "withdrawal supersedes the ordinary support window")
    if snapshot.release_phase in ("draft", "candidate"):
        return Decision(False, "unpublished", "draft or candidate is not a supported release")
    if at_tick > snapshot.support_end_tick:
        return Decision(False, "expired", "recorded support window has ended")
    return Decision(True, "recorded", "tick is inside this local support-policy record")


def canonical_record(lifecycle: object) -> str:
    """Return one deterministic JSON representation after complete validation."""

    snapshot = validate_lifecycle(lifecycle)
    payload = {
        "advisory_id": snapshot.advisory_id,
        "claims": snapshot.claims,
        "compatible_from": snapshot.compatible_from,
        "events": [
            {
                "action": event.action,
                "detail": event.detail,
                "evidence": list(event.evidence),
                "sequence": event.sequence,
                "tick": event.tick,
            }
            for event in snapshot.events
        ],
        "incident_phase": snapshot.incident_phase,
        "migration_recorded": snapshot.migration_recorded,
        "min_installable_revision": snapshot.min_installable_revision,
        "notified_downstreams": list(snapshot.notified_downstreams),
        "product_id": snapshot.product_id,
        "recovery_drills": snapshot.recovery_drills,
        "release_phase": snapshot.release_phase,
        "release_revision": snapshot.release_revision,
        "severity": snapshot.severity,
        "support_end_tick": snapshot.support_end_tick,
    }
    return json.dumps(payload, ensure_ascii=True, sort_keys=True, separators=(",", ":"))


def record_digest(lifecycle: object) -> str:
    return sha256(canonical_record(lifecycle).encode("utf-8")).hexdigest()


def endpoint_scenario() -> Lifecycle:
    """Reach all interacting course caps in one legal deterministic history."""

    state = new_lifecycle("p" * MAX_ID_LENGTH, release_revision=7, support_end_tick=9_999)
    steps = (
        TransitionRequest("promote_candidate", 9_985, ("e" * MAX_ID_LENGTH, "candidate-test", "compat-review", "owner-approval")),
        TransitionRequest("publish_release", 9_986, ("release-manifest",)),
        TransitionRequest("intake_report", 9_987, ("report-104",)),
        TransitionRequest("triage_report", 9_988, ("triage-worksheet",), severity="critical"),
        TransitionRequest("suspend_claims", 9_989, ("claim-review",)),
        TransitionRequest("contain_release", 9_990, ("containment-log",)),
        TransitionRequest("publish_advisory", 9_991, ("advisory-review",), advisory_id="adv-2026-104"),
        TransitionRequest("release_update", 9_992, ("update-tests",), new_revision=8),
        TransitionRequest("record_migration", 9_993, ("migration-test",)),
        TransitionRequest("raise_rollback_floor", 9_994, ("rollback-test",)),
        TransitionRequest("notify_downstreams", 9_995, ("notice-a",), downstreams=("downstream-a",)),
        TransitionRequest("notify_downstreams", 9_996, ("notice-b",), downstreams=("downstream-b",)),
        TransitionRequest("notify_downstreams", 9_997, ("notice-c",), downstreams=("downstream-c",)),
        TransitionRequest("notify_downstreams", 9_998, ("notice-d",), downstreams=("downstream-d",)),
        TransitionRequest("close_incident", 9_999, ("closure-review",)),
        TransitionRequest("recovery_drill", MAX_TICK, ("recovery-replay",)),
    )
    for step in steps:
        state = transition(state, step)
    return state
