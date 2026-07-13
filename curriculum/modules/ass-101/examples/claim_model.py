#!/usr/bin/env python3
"""Bounded claim, evidence, and dependency-closure teaching model.

This model checks the internal consistency of finite assurance records.  It
does not prove a claim, validate an external system, or establish any Orange
language, toolchain, security, or release property.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re


MAX_ASSUMPTIONS = 32
MAX_CLAIMS = 32
MAX_CLOSURE_DEPTH = 8
MAX_EVIDENCE = 64
MAX_FACTS = 16
MAX_REFS = 16
MAX_TCB_ENTRIES = 32
MAX_TEXT_LENGTH = 300

IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9-]{0,47}$")
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")
EVIDENCE_ID_RE = re.compile(r"^sha256:[0-9a-f]{64}$")


class EvidenceKind(str, Enum):
    TEST = "test"
    ANALYSIS = "analysis"
    FORMAL = "formal"
    INSPECTION = "inspection"
    PROVENANCE = "provenance"


class EvidenceResult(str, Enum):
    PASS = "pass"
    FAIL = "fail"
    INCONCLUSIVE = "inconclusive"


class AssumptionState(str, Enum):
    CONFIRMED = "confirmed"
    UNVERIFIED = "unverified"
    FALSE = "false"


class ReviewState(str, Enum):
    REVIEWED = "reviewed"
    UNREVIEWED = "unreviewed"
    COMPROMISED = "compromised"


class ClaimStatus(str, Enum):
    SUPPORTED = "SUPPORTED"
    UNSUPPORTED = "UNSUPPORTED"
    REFUTED = "REFUTED"
    INVALID = "INVALID"


def _text(value: object, label: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if not value or value != value.strip():
        raise ValueError(f"{label} must be nonempty with no outer whitespace")
    if len(value) > MAX_TEXT_LENGTH:
        raise ValueError(f"{label} exceeds {MAX_TEXT_LENGTH} characters")
    return value


def _identifier(value: object, label: str) -> str:
    checked = _text(value, label)
    if IDENTIFIER_RE.fullmatch(checked) is None:
        raise ValueError(f"{label} must match {IDENTIFIER_RE.pattern}")
    return checked


def _sha256(value: object, label: str) -> str:
    if type(value) is not str or SHA256_RE.fullmatch(value) is None:
        raise ValueError(f"{label} must be 64 lowercase hexadecimal characters")
    return value


def _typed_tuple(
    value: object,
    item_type: type,
    label: str,
    maximum: int,
    *,
    minimum: int = 0,
) -> tuple:
    if type(value) is not tuple:
        raise TypeError(f"{label} must be a tuple")
    if not minimum <= len(value) <= maximum:
        raise ValueError(f"{label} count must be in {minimum}..{maximum}")
    if any(type(item) is not item_type for item in value):
        raise TypeError(f"{label} entries must be {item_type.__name__}")
    return value


def _id_tuple(value: object, label: str, *, minimum: int = 0) -> tuple[str, ...]:
    checked = _typed_tuple(value, str, label, MAX_REFS, minimum=minimum)
    for item in checked:
        _identifier(item, f"{label} entry")
    if tuple(sorted(set(checked))) != checked:
        raise ValueError(f"{label} must be sorted and unique")
    return checked


@dataclass(frozen=True, slots=True, order=True)
class EvidenceFact:
    key: str
    value: str

    def __post_init__(self) -> None:
        _identifier(self.key, "evidence fact key")
        _text(self.value, "evidence fact value")


@dataclass(frozen=True, slots=True)
class Assumption:
    identifier: str
    statement: str
    owner: str
    falsifier: str
    state: AssumptionState

    def __post_init__(self) -> None:
        _identifier(self.identifier, "assumption identifier")
        _text(self.statement, "assumption statement")
        _text(self.owner, "assumption owner")
        _text(self.falsifier, "assumption falsifier")
        if type(self.state) is not AssumptionState:
            raise TypeError("assumption state must be AssumptionState")


@dataclass(frozen=True, slots=True)
class TrustedComponent:
    identifier: str
    role: str
    version: str
    artifact_sha256: str
    review_state: ReviewState

    def __post_init__(self) -> None:
        _identifier(self.identifier, "trusted component identifier")
        _text(self.role, "trusted component role")
        _text(self.version, "trusted component version")
        _sha256(self.artifact_sha256, "trusted component artifact_sha256")
        if type(self.review_state) is not ReviewState:
            raise TypeError("trusted component review_state must be ReviewState")


@dataclass(frozen=True, slots=True)
class EvidenceRecord:
    identity: str
    kind: EvidenceKind
    producer: str
    subject: str
    method: str
    result: EvidenceResult
    artifact_sha256: str
    assumption_ids: tuple[str, ...]
    tcb_ids: tuple[str, ...]
    facts: tuple[EvidenceFact, ...]

    def __post_init__(self) -> None:
        if type(self.identity) is not str or EVIDENCE_ID_RE.fullmatch(self.identity) is None:
            raise ValueError("evidence identity must be sha256 followed by 64 lowercase hexadecimal characters")
        if type(self.kind) is not EvidenceKind:
            raise TypeError("evidence kind must be EvidenceKind")
        _text(self.producer, "evidence producer")
        _text(self.subject, "evidence subject")
        _text(self.method, "evidence method")
        if type(self.result) is not EvidenceResult:
            raise TypeError("evidence result must be EvidenceResult")
        _sha256(self.artifact_sha256, "evidence artifact_sha256")
        _id_tuple(self.assumption_ids, "evidence assumption_ids")
        _id_tuple(self.tcb_ids, "evidence tcb_ids", minimum=1)
        _typed_tuple(self.facts, EvidenceFact, "evidence facts", MAX_FACTS)
        fact_keys = tuple(fact.key for fact in self.facts)
        if tuple(sorted(set(fact_keys))) != fact_keys:
            raise ValueError("evidence facts must have sorted unique keys")


@dataclass(frozen=True, slots=True)
class Claim:
    identifier: str
    statement: str
    subject: str
    scope: str
    exclusions: tuple[str, ...]
    assumption_ids: tuple[str, ...]
    evidence_ids: tuple[str, ...]
    dependency_ids: tuple[str, ...]
    tcb_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _identifier(self.identifier, "claim identifier")
        _text(self.statement, "claim statement")
        _text(self.subject, "claim subject")
        _text(self.scope, "claim scope")
        _typed_tuple(self.exclusions, str, "claim exclusions", MAX_REFS, minimum=1)
        for exclusion in self.exclusions:
            _text(exclusion, "claim exclusion")
        if tuple(sorted(set(self.exclusions))) != self.exclusions:
            raise ValueError("claim exclusions must be sorted and unique")
        _id_tuple(self.assumption_ids, "claim assumption_ids")
        _typed_tuple(self.evidence_ids, str, "claim evidence_ids", MAX_REFS)
        if tuple(sorted(set(self.evidence_ids))) != self.evidence_ids:
            raise ValueError("claim evidence_ids must be sorted and unique")
        for evidence_id in self.evidence_ids:
            if EVIDENCE_ID_RE.fullmatch(evidence_id) is None:
                raise ValueError("claim evidence_ids entries must be canonical evidence identities")
        _id_tuple(self.dependency_ids, "claim dependency_ids")
        _id_tuple(self.tcb_ids, "claim tcb_ids", minimum=1)


@dataclass(frozen=True, slots=True)
class AssuranceBundle:
    name: str
    assumptions: tuple[Assumption, ...]
    trusted_components: tuple[TrustedComponent, ...]
    evidence: tuple[EvidenceRecord, ...]
    claims: tuple[Claim, ...]

    def __post_init__(self) -> None:
        _text(self.name, "bundle name")
        _typed_tuple(
            self.assumptions, Assumption, "bundle assumptions", MAX_ASSUMPTIONS
        )
        _typed_tuple(
            self.trusted_components,
            TrustedComponent,
            "bundle trusted_components",
            MAX_TCB_ENTRIES,
            minimum=1,
        )
        _typed_tuple(
            self.evidence, EvidenceRecord, "bundle evidence", MAX_EVIDENCE
        )
        _typed_tuple(self.claims, Claim, "bundle claims", MAX_CLAIMS, minimum=1)


@dataclass(frozen=True, slots=True, order=True)
class Finding:
    code: str
    location: str
    message: str


@dataclass(frozen=True, slots=True)
class ClaimReport:
    identifier: str
    status: ClaimStatus
    dependency_closure: tuple[str, ...]
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class Evaluation:
    findings: tuple[Finding, ...]
    reports: tuple[ClaimReport, ...]

    def __post_init__(self) -> None:
        if type(self.findings) is not tuple or any(
            type(item) is not Finding for item in self.findings
        ):
            raise TypeError("evaluation findings must be a tuple of Finding records")
        if type(self.reports) is not tuple or any(
            type(item) is not ClaimReport for item in self.reports
        ):
            raise TypeError("evaluation reports must be a tuple of ClaimReport records")
        if not self.reports:
            raise ValueError("evaluation must contain at least one claim report")

    @property
    def status(self) -> ClaimStatus:
        if self.findings:
            return ClaimStatus.INVALID
        statuses = {report.status for report in self.reports}
        if ClaimStatus.INVALID in statuses:
            return ClaimStatus.INVALID
        if ClaimStatus.REFUTED in statuses:
            return ClaimStatus.REFUTED
        if ClaimStatus.UNSUPPORTED in statuses:
            return ClaimStatus.UNSUPPORTED
        return ClaimStatus.SUPPORTED

    @property
    def limitation(self) -> str:
        return (
            "Bounded record-consistency evidence only; not proof of an external "
            "claim and not an Orange capability, conformance, safety, or release claim."
        )


def _evidence_payload(
    *,
    kind: EvidenceKind,
    producer: str,
    subject: str,
    method: str,
    result: EvidenceResult,
    artifact_sha256: str,
    assumption_ids: tuple[str, ...],
    tcb_ids: tuple[str, ...],
    facts: tuple[EvidenceFact, ...],
) -> dict[str, object]:
    return {
        "artifact_sha256": artifact_sha256,
        "assumption_ids": list(assumption_ids),
        "facts": [{"key": fact.key, "value": fact.value} for fact in facts],
        "kind": kind.value,
        "method": method,
        "producer": producer,
        "result": result.value,
        "schema": "ass-101-evidence-v1",
        "subject": subject,
        "tcb_ids": list(tcb_ids),
    }


def canonical_evidence_identity(record: EvidenceRecord) -> str:
    """Recompute the identity from a canonical UTF-8 JSON representation."""

    if type(record) is not EvidenceRecord:
        raise TypeError("record must be EvidenceRecord")
    payload = _evidence_payload(
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
    encoded = json.dumps(
        payload, ensure_ascii=True, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def make_evidence(
    *,
    kind: EvidenceKind,
    producer: str,
    subject: str,
    method: str,
    result: EvidenceResult,
    artifact_sha256: str,
    assumption_ids: tuple[str, ...] = (),
    tcb_ids: tuple[str, ...],
    facts: tuple[EvidenceFact, ...] = (),
) -> EvidenceRecord:
    """Construct an evidence record with its canonical content identity."""

    placeholder = EvidenceRecord(
        identity="sha256:" + "0" * 64,
        kind=kind,
        producer=producer,
        subject=subject,
        method=method,
        result=result,
        artifact_sha256=artifact_sha256,
        assumption_ids=assumption_ids,
        tcb_ids=tcb_ids,
        facts=facts,
    )
    return EvidenceRecord(
        identity=canonical_evidence_identity(placeholder),
        kind=placeholder.kind,
        producer=placeholder.producer,
        subject=placeholder.subject,
        method=placeholder.method,
        result=placeholder.result,
        artifact_sha256=placeholder.artifact_sha256,
        assumption_ids=placeholder.assumption_ids,
        tcb_ids=placeholder.tcb_ids,
        facts=placeholder.facts,
    )


def _duplicate_ids(items: tuple) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for item in items:
        identifier = item.identifier if hasattr(item, "identifier") else item.identity
        if identifier in seen:
            duplicates.add(identifier)
        seen.add(identifier)
    return duplicates


def evaluate_bundle(bundle: AssuranceBundle) -> Evaluation:
    """Derive deterministic fail-closed claim statuses and stable findings."""

    if type(bundle) is not AssuranceBundle:
        raise TypeError("bundle must be AssuranceBundle")

    findings: list[Finding] = []
    invalid_claims: set[str] = set()
    assumptions = {item.identifier: item for item in bundle.assumptions}
    trusted = {item.identifier: item for item in bundle.trusted_components}
    evidence = {item.identity: item for item in bundle.evidence}
    claims = {item.identifier: item for item in bundle.claims}

    for label, items in (
        ("assumption", bundle.assumptions),
        ("tcb", bundle.trusted_components),
        ("evidence", bundle.evidence),
        ("claim", bundle.claims),
    ):
        for identifier in sorted(_duplicate_ids(items)):
            findings.append(Finding("duplicate-id", f"{label}:{identifier}", "identifier is repeated"))
            if label == "claim":
                invalid_claims.add(identifier)

    for record in bundle.evidence:
        expected = canonical_evidence_identity(record)
        if record.identity != expected:
            findings.append(
                Finding(
                    "evidence-identity-mismatch",
                    f"evidence:{record.identity}",
                    f"canonical identity is {expected}",
                )
            )
        for assumption_id in record.assumption_ids:
            if assumption_id not in assumptions:
                findings.append(Finding("unknown-assumption", f"evidence:{record.identity}", assumption_id))
        for tcb_id in record.tcb_ids:
            if tcb_id not in trusted:
                findings.append(Finding("unknown-tcb", f"evidence:{record.identity}", tcb_id))

    for claim in bundle.claims:
        location = f"claim:{claim.identifier}"
        for assumption_id in claim.assumption_ids:
            if assumption_id not in assumptions:
                findings.append(Finding("unknown-assumption", location, assumption_id))
                invalid_claims.add(claim.identifier)
        for evidence_id in claim.evidence_ids:
            if evidence_id not in evidence:
                findings.append(Finding("unknown-evidence", location, evidence_id))
                invalid_claims.add(claim.identifier)
        for dependency_id in claim.dependency_ids:
            if dependency_id not in claims:
                findings.append(Finding("unknown-dependency", location, dependency_id))
                invalid_claims.add(claim.identifier)
            elif dependency_id == claim.identifier:
                findings.append(Finding("dependency-cycle", location, dependency_id))
                invalid_claims.add(claim.identifier)
        for tcb_id in claim.tcb_ids:
            if tcb_id not in trusted:
                findings.append(Finding("unknown-tcb", location, tcb_id))
                invalid_claims.add(claim.identifier)

    closure_cache: dict[str, tuple[str, ...]] = {}
    closure_depth: dict[str, int] = {}

    def close(identifier: str, path: tuple[str, ...]) -> tuple[tuple[str, ...], int]:
        if identifier in closure_cache:
            return closure_cache[identifier], closure_depth[identifier]
        if identifier in path:
            cycle = path[path.index(identifier):] + (identifier,)
            for member in cycle:
                invalid_claims.add(member)
            findings.append(
                Finding("dependency-cycle", f"claim:{identifier}", " -> ".join(cycle))
            )
            return (), MAX_CLOSURE_DEPTH + 1
        claim = claims[identifier]
        members: set[str] = set()
        maximum_depth = 0
        for dependency_id in claim.dependency_ids:
            if dependency_id not in claims:
                continue
            members.add(dependency_id)
            nested, nested_depth = close(dependency_id, path + (identifier,))
            members.update(nested)
            maximum_depth = max(maximum_depth, 1 + nested_depth)
        result = tuple(sorted(members))
        closure_cache[identifier] = result
        closure_depth[identifier] = maximum_depth
        if maximum_depth > MAX_CLOSURE_DEPTH:
            findings.append(
                Finding(
                    "closure-depth-exceeded",
                    f"claim:{identifier}",
                    f"dependency closure depth {maximum_depth} exceeds {MAX_CLOSURE_DEPTH}",
                )
            )
            invalid_claims.add(identifier)
        return result, maximum_depth

    for identifier in sorted(claims):
        close(identifier, ())

    # Inventory closure is a checkable obligation: a parent inventory includes
    # the TCB and assumptions of direct evidence and all transitive claims.
    for claim in bundle.claims:
        required_tcb: set[str] = set()
        required_assumptions: set[str] = set()
        related_claims = (claim.identifier,) + closure_cache.get(claim.identifier, ())
        for related_id in related_claims:
            related = claims.get(related_id)
            if related is None:
                continue
            required_tcb.update(related.tcb_ids)
            required_assumptions.update(related.assumption_ids)
            for evidence_id in related.evidence_ids:
                record = evidence.get(evidence_id)
                if record is not None:
                    required_tcb.update(record.tcb_ids)
                    required_assumptions.update(record.assumption_ids)
        for missing in sorted(required_tcb - set(claim.tcb_ids)):
            findings.append(Finding("tcb-closure-missing", f"claim:{claim.identifier}", missing))
            invalid_claims.add(claim.identifier)
        for missing in sorted(required_assumptions - set(claim.assumption_ids)):
            findings.append(Finding("assumption-closure-missing", f"claim:{claim.identifier}", missing))
            invalid_claims.add(claim.identifier)

    status_cache: dict[str, tuple[ClaimStatus, tuple[str, ...]]] = {}

    def derive(identifier: str, active: frozenset[str]) -> tuple[ClaimStatus, tuple[str, ...]]:
        if identifier in status_cache:
            return status_cache[identifier]
        if identifier in active or identifier in invalid_claims:
            return ClaimStatus.INVALID, ("record structure or dependency closure is invalid",)
        claim = claims[identifier]
        reasons: list[str] = []
        if not claim.evidence_ids:
            reasons.append("no direct evidence; dependencies do not compose automatically")
        direct_records = [evidence[item] for item in claim.evidence_ids if item in evidence]
        mismatched = [item for item in direct_records if item.identity != canonical_evidence_identity(item)]
        if mismatched:
            status = ClaimStatus.INVALID
            reasons.append("direct evidence identity mismatch")
        elif any(item.result is EvidenceResult.FAIL for item in direct_records):
            status = ClaimStatus.REFUTED
            reasons.append("direct evidence reports fail")
        else:
            status = ClaimStatus.SUPPORTED
            if any(item.result is EvidenceResult.INCONCLUSIVE for item in direct_records):
                status = ClaimStatus.UNSUPPORTED
                reasons.append("direct evidence is inconclusive")
            relevant_assumptions = [assumptions[item] for item in claim.assumption_ids if item in assumptions]
            if any(item.state is not AssumptionState.CONFIRMED for item in relevant_assumptions):
                status = ClaimStatus.UNSUPPORTED
                reasons.append("an assumption is not confirmed")
            relevant_tcb = [trusted[item] for item in claim.tcb_ids if item in trusted]
            if any(item.review_state is not ReviewState.REVIEWED for item in relevant_tcb):
                status = ClaimStatus.UNSUPPORTED
                reasons.append("a trusted component is not reviewed")
            for dependency_id in claim.dependency_ids:
                if dependency_id not in claims:
                    status = ClaimStatus.INVALID
                    continue
                dependency_status, _ = derive(dependency_id, active | {identifier})
                if dependency_status is ClaimStatus.INVALID:
                    status = ClaimStatus.INVALID
                    reasons.append(f"dependency {dependency_id} is invalid")
                elif dependency_status is not ClaimStatus.SUPPORTED and status is ClaimStatus.SUPPORTED:
                    status = ClaimStatus.UNSUPPORTED
                    reasons.append(f"dependency {dependency_id} is {dependency_status.value}")
            if reasons and status is ClaimStatus.SUPPORTED:
                status = ClaimStatus.UNSUPPORTED
        if not reasons:
            reasons.append("all declared direct and transitive support obligations pass")
        result = status, tuple(reasons)
        status_cache[identifier] = result
        return result

    reports = []
    for identifier in sorted(claims):
        status, reasons = derive(identifier, frozenset())
        reports.append(
            ClaimReport(identifier, status, closure_cache.get(identifier, ()), reasons)
        )
    return Evaluation(tuple(sorted(set(findings))), tuple(reports))


def render_evaluation(bundle: AssuranceBundle, evaluation: Evaluation) -> str:
    if type(bundle) is not AssuranceBundle:
        raise TypeError("bundle must be AssuranceBundle")
    if type(evaluation) is not Evaluation:
        raise TypeError("evaluation must be Evaluation")
    if evaluation != evaluate_bundle(bundle):
        raise ValueError("evaluation does not match the supplied bundle")
    lines = [
        f"bundle: {bundle.name}",
        f"claims: {len(bundle.claims)}",
        f"evidence: {len(bundle.evidence)}",
        f"findings: {len(evaluation.findings)}",
    ]
    for report in evaluation.reports:
        closure = ",".join(report.dependency_closure) or "-"
        lines.append(f"claim {report.identifier}: {report.status.value} closure={closure}")
        for reason in report.reasons:
            lines.append(f"  reason: {reason}")
    for finding in evaluation.findings:
        lines.append(f"finding {finding.code} at {finding.location}: {finding.message}")
    lines.extend((f"overall: {evaluation.status.value}", f"limitation: {evaluation.limitation}"))
    return "\n".join(lines)
