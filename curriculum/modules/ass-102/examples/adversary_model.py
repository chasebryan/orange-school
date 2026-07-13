#!/usr/bin/env python3
"""Bounded deterministic adversarial-testing model for ASS-102.

Gauntlet is an independent Python teaching model.  It is not Orange tooling
and establishes no property of Orange or of an external system.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import hashlib
import json
import re
from typing import Callable


MAX_INPUT_BYTES = 128
MAX_THREATS = 8
MAX_CASES = 32
MAX_RELATIONS = 16
MAX_REFS = 8
MAX_TEXT = 240
MAX_RUN_EVALUATIONS = 64
MAX_MINIMIZE_EVALUATIONS = 128
MAX_FINDINGS = 94

ID_RE = re.compile(r"^[a-z][a-z0-9-]{0,63}$")


class SubjectKind(Enum):
    PARSER = "parser"
    IMPLEMENTATION = "implementation"
    CERTIFICATE = "certificate"
    POLICY = "policy"
    ARTIFACT = "artifact"


class RelationExpectation(Enum):
    SAME = "same"
    DIFFERENT = "different"
    FOLLOWUP_REJECTS = "followup-rejects"


@dataclass(frozen=True, slots=True)
class Outcome:
    accepted: bool
    code: str
    value: str

    def __post_init__(self) -> None:
        if type(self.accepted) is not bool:
            raise TypeError("outcome accepted must be bool")
        _identifier(self.code, "outcome code")
        if type(self.value) is not str:
            raise TypeError("outcome value must be str")
        if len(self.value) > MAX_TEXT:
            raise ValueError(f"outcome value length must be in 0..{MAX_TEXT}")
        if self.accepted and not self.value:
            raise ValueError("accepted outcome value must not be empty")
        if not self.accepted and self.value:
            raise ValueError("rejected outcome value must be empty")


@dataclass(frozen=True, slots=True, order=True)
class Threat:
    identifier: str
    kind: SubjectKind
    hypothesis: str
    oracle_basis: str

    def __post_init__(self) -> None:
        _identifier(self.identifier, "threat identifier")
        if type(self.kind) is not SubjectKind:
            raise TypeError("threat kind must be SubjectKind")
        _text(self.hypothesis, "threat hypothesis")
        _text(self.oracle_basis, "threat oracle_basis")


@dataclass(frozen=True, slots=True)
class Case:
    identifier: str
    kind: SubjectKind
    data: bytes
    origin: str
    threat_ids: tuple[str, ...]
    parent_id: str = ""
    operator: str = ""

    def __post_init__(self) -> None:
        _identifier(self.identifier, "case identifier")
        if type(self.kind) is not SubjectKind:
            raise TypeError("case kind must be SubjectKind")
        if type(self.data) is not bytes:
            raise TypeError("case data must be bytes")
        if len(self.data) > MAX_INPUT_BYTES:
            raise ValueError(f"case data exceeds {MAX_INPUT_BYTES} bytes")
        _identifier(self.origin, "case origin")
        _id_tuple(self.threat_ids, "case threat_ids", minimum=1)
        if self.parent_id:
            _identifier(self.parent_id, "case parent_id")
        if self.operator:
            _identifier(self.operator, "case operator")
        if bool(self.parent_id) != bool(self.operator):
            raise ValueError("case parent_id and operator must be present together")


@dataclass(frozen=True, slots=True, order=True)
class Relation:
    identifier: str
    source_id: str
    followup_id: str
    expectation: RelationExpectation

    def __post_init__(self) -> None:
        _identifier(self.identifier, "relation identifier")
        _identifier(self.source_id, "relation source_id")
        _identifier(self.followup_id, "relation followup_id")
        if self.source_id == self.followup_id:
            raise ValueError("relation endpoints must be different")
        if type(self.expectation) is not RelationExpectation:
            raise TypeError("relation expectation must be RelationExpectation")


@dataclass(frozen=True, slots=True)
class Corpus:
    name: str
    threats: tuple[Threat, ...]
    cases: tuple[Case, ...]
    relations: tuple[Relation, ...]

    def __post_init__(self) -> None:
        _text(self.name, "corpus name")
        _typed_tuple(self.threats, Threat, "corpus threats", MAX_THREATS, minimum=1)
        _typed_tuple(self.cases, Case, "corpus cases", MAX_CASES, minimum=1)
        _typed_tuple(self.relations, Relation, "corpus relations", MAX_RELATIONS)
        _sorted_unique(self.threats, "corpus threats")
        _sorted_unique(self.cases, "corpus cases")
        _sorted_unique(self.relations, "corpus relations")

        threat_ids = {item.identifier for item in self.threats}
        threat_by_id = {item.identifier: item for item in self.threats}
        case_ids = {item.identifier for item in self.cases}
        case_by_id = {item.identifier: item for item in self.cases}
        parents = {item.identifier: item.parent_id for item in self.cases}
        for case in self.cases:
            unknown = set(case.threat_ids) - threat_ids
            if unknown:
                raise ValueError(f"case {case.identifier} references unknown threat {min(unknown)}")
            if any(threat_by_id[item].kind is not case.kind for item in case.threat_ids):
                raise ValueError(
                    f"case {case.identifier} kind does not match every referenced threat"
                )
            if case.parent_id and case.parent_id not in case_ids:
                raise ValueError(f"case {case.identifier} references unknown parent {case.parent_id}")
            if case.parent_id and case_by_id[case.parent_id].kind is not case.kind:
                raise ValueError(
                    f"case {case.identifier} kind does not match parent {case.parent_id}"
                )
            if case.parent_id == case.identifier:
                raise ValueError(f"case {case.identifier} cannot be its own parent")
        for start in sorted(case_ids):
            seen: set[str] = set()
            current = start
            while parents[current]:
                if current in seen:
                    raise ValueError(f"case lineage cycle at {current}")
                seen.add(current)
                current = parents[current]
        for relation in self.relations:
            if relation.source_id not in case_ids:
                raise ValueError(f"relation {relation.identifier} references unknown source")
            if relation.followup_id not in case_ids:
                raise ValueError(f"relation {relation.identifier} references unknown followup")
        evaluations = len(self.cases) + 2 * len(self.relations)
        if evaluations > MAX_RUN_EVALUATIONS:
            raise ValueError(f"corpus run exceeds {MAX_RUN_EVALUATIONS} evaluations")


@dataclass(frozen=True, slots=True, order=True)
class Finding:
    code: str
    location: str
    detail: str


@dataclass(frozen=True, slots=True, order=True)
class Observation:
    case_id: str
    oracle: Outcome
    target: Outcome | None


@dataclass(frozen=True, slots=True)
class Report:
    corpus_identity: str
    observations: tuple[Observation, ...]
    findings: tuple[Finding, ...]
    exercised_threats: tuple[str, ...]
    evaluations: int

    @property
    def passed(self) -> bool:
        return not self.findings

    @property
    def limitation(self) -> str:
        return (
            "The report binds corpus bytes, not oracle or target callable identity. "
            "Finite model observations only; not exhaustive coverage, proof, or an "
            "Orange capability, safety, security, conformance, or release claim."
        )


@dataclass(frozen=True, slots=True)
class Minimized:
    data: bytes
    evaluations: int
    one_minimal: bool


Evaluator = Callable[[bytes], Outcome]


def _identifier(value: object, label: str) -> str:
    if type(value) is not str or ID_RE.fullmatch(value) is None:
        raise ValueError(f"{label} must match {ID_RE.pattern}")
    return value


def _text(value: object, label: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{label} must be str")
    if not value or len(value) > MAX_TEXT:
        raise ValueError(f"{label} length must be in 1..{MAX_TEXT}")
    return value


def _typed_tuple(value: object, item_type: type, label: str, maximum: int, *, minimum: int = 0) -> tuple:
    if type(value) is not tuple:
        raise TypeError(f"{label} must be tuple")
    if not minimum <= len(value) <= maximum:
        raise ValueError(f"{label} count must be in {minimum}..{maximum}")
    if any(type(item) is not item_type for item in value):
        raise TypeError(f"{label} entries must be {item_type.__name__}")
    return value


def _id_tuple(value: object, label: str, *, minimum: int = 0) -> tuple[str, ...]:
    result = _typed_tuple(value, str, label, MAX_REFS, minimum=minimum)
    for item in result:
        _identifier(item, f"{label} entry")
    if tuple(sorted(set(result))) != result:
        raise ValueError(f"{label} must be sorted and unique")
    return result


def _sorted_unique(items: tuple, label: str) -> None:
    identifiers = tuple(item.identifier for item in items)
    if tuple(sorted(set(identifiers))) != identifiers:
        raise ValueError(f"{label} must be sorted by unique identifier")


def corpus_identity(corpus: Corpus) -> str:
    """Return the identity of the exact canonical corpus bytes."""

    if type(corpus) is not Corpus:
        raise TypeError("corpus must be Corpus")
    payload = {
        "cases": [
            {
                "data_hex": case.data.hex(),
                "id": case.identifier,
                "kind": case.kind.value,
                "operator": case.operator,
                "origin": case.origin,
                "parent_id": case.parent_id,
                "threat_ids": list(case.threat_ids),
            }
            for case in corpus.cases
        ],
        "name": corpus.name,
        "relations": [
            {
                "expectation": relation.expectation.value,
                "followup_id": relation.followup_id,
                "id": relation.identifier,
                "source_id": relation.source_id,
            }
            for relation in corpus.relations
        ],
        "schema": "ass-102-corpus-v1",
        "threats": [
            {
                "hypothesis": threat.hypothesis,
                "id": threat.identifier,
                "kind": threat.kind.value,
                "oracle_basis": threat.oracle_basis,
            }
            for threat in corpus.threats
        ],
    }
    encoded = json.dumps(
        payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True
    ).encode("utf-8")
    return "sha256:" + hashlib.sha256(encoded).hexdigest()


def _safe_call(evaluator: Evaluator, data: bytes, side: str, case_id: str) -> tuple[Outcome | None, Finding | None]:
    try:
        value = evaluator(data)
    except BaseException as error:  # The boundary converts an untrusted target failure.
        return None, Finding(f"{side}-exception", case_id, type(error).__name__)
    if type(value) is not Outcome:
        return None, Finding(f"{side}-outcome-type", case_id, type(value).__name__)
    return value, None


def _relation_holds(expectation: RelationExpectation, left: Outcome, right: Outcome) -> bool:
    if expectation is RelationExpectation.SAME:
        return left == right
    if expectation is RelationExpectation.DIFFERENT:
        return left != right
    return left.accepted and not right.accepted


def run_suite(corpus: Corpus, *, oracle: Evaluator, target: Evaluator) -> Report:
    """Compare independent callables over one already-bounded corpus."""

    if type(corpus) is not Corpus:
        raise TypeError("corpus must be Corpus")
    if not callable(oracle) or not callable(target):
        raise TypeError("oracle and target must be callable")
    if oracle is target:
        raise ValueError("oracle and target must be different callables")

    findings: list[Finding] = []
    observations: list[Observation] = []
    by_id: dict[str, tuple[Outcome | None, Outcome | None]] = {}
    evaluations = 0
    for case in corpus.cases:
        oracle_value, oracle_finding = _safe_call(oracle, case.data, "oracle", case.identifier)
        target_value, target_finding = _safe_call(target, case.data, "target", case.identifier)
        evaluations += 1
        if oracle_finding:
            findings.append(oracle_finding)
        if target_finding:
            findings.append(target_finding)
        if oracle_value is not None and target_value is not None and oracle_value != target_value:
            findings.append(Finding("differential-mismatch", case.identifier, "target differs from oracle"))
        if oracle_value is not None:
            observations.append(Observation(case.identifier, oracle_value, target_value))
        by_id[case.identifier] = (oracle_value, target_value)

    for relation in corpus.relations:
        oracle_left, target_left = by_id[relation.source_id]
        oracle_right, target_right = by_id[relation.followup_id]
        evaluations += 2
        if oracle_left is not None and oracle_right is not None and not _relation_holds(
            relation.expectation, oracle_left, oracle_right
        ):
            findings.append(Finding("oracle-relation-violation", relation.identifier, relation.expectation.value))
        if target_left is not None and target_right is not None and not _relation_holds(
            relation.expectation, target_left, target_right
        ):
            findings.append(Finding("metamorphic-violation", relation.identifier, relation.expectation.value))

    if len(findings) > MAX_FINDINGS:
        raise RuntimeError(f"finding count exceeds internal cap {MAX_FINDINGS}")
    exercised = tuple(sorted({threat_id for case in corpus.cases for threat_id in case.threat_ids}))
    return Report(
        corpus_identity(corpus),
        tuple(sorted(observations)),
        tuple(sorted(set(findings))),
        exercised,
        evaluations,
    )


def minimize_counterexample(
    data: bytes,
    predicate: Callable[[bytes], bool],
    *,
    max_evaluations: int = MAX_MINIMIZE_EVALUATIONS,
) -> Minimized:
    """Greedily delete bytes; return whether deletion one-minimality was checked."""

    if type(data) is not bytes:
        raise TypeError("minimizer data must be bytes")
    if len(data) > MAX_INPUT_BYTES:
        raise ValueError(f"minimizer data exceeds {MAX_INPUT_BYTES} bytes")
    if not callable(predicate):
        raise TypeError("minimizer predicate must be callable")
    if type(max_evaluations) is not int or not 1 <= max_evaluations <= MAX_MINIMIZE_EVALUATIONS:
        raise ValueError(f"max_evaluations must be in 1..{MAX_MINIMIZE_EVALUATIONS}")
    initial_result = predicate(data)
    if type(initial_result) is not bool:
        raise TypeError("minimizer predicate must return an exact bool")
    if not initial_result:
        raise ValueError("initial input is not a counterexample")

    current = data
    evaluations = 1
    index = 0
    while index < len(current) and evaluations < max_evaluations:
        candidate = current[:index] + current[index + 1 :]
        evaluations += 1
        candidate_result = predicate(candidate)
        if type(candidate_result) is not bool:
            raise TypeError("minimizer predicate must return an exact bool")
        if candidate_result:
            current = candidate
            index = 0
        else:
            index += 1
    return Minimized(current, evaluations, index >= len(current))


def derive_case(seed: Case, *, identifier: str, data: bytes, operator: str) -> Case:
    """Create a traceable structured mutation without modifying the seed."""

    if type(seed) is not Case:
        raise TypeError("seed must be Case")
    return Case(
        identifier,
        seed.kind,
        data,
        "mutation",
        seed.threat_ids,
        seed.identifier,
        operator,
    )
