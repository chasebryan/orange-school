#!/usr/bin/env python3
"""Bounded structural checks for a cryptographic security-requirements model.

This module does not implement cryptography and does not decide whether a
system is secure.  It checks that a small teaching model is internally
referenced and states several requirements that a human security review needs.
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
import re


MAX_ASSETS = 16
MAX_ASSUMPTIONS = 16
MAX_BOUNDARIES = 16
MAX_MATERIALS = 16
MAX_REQUIREMENTS = 64
MAX_DEPENDENCIES = 16
MAX_TEXT_LENGTH = 400

IDENTIFIER_RE = re.compile(r"^[a-z][a-z0-9-]{0,39}$")


class SecurityGoal(str, Enum):
    CONFIDENTIALITY = "confidentiality"
    INTEGRITY = "integrity"
    AUTHENTICITY = "authenticity"
    FRESHNESS = "freshness"
    AVAILABILITY = "availability"


class AttackerCapability(str, Enum):
    OBSERVE_NETWORK = "observe-network"
    ALTER_NETWORK = "alter-network"
    INJECT_NETWORK = "inject-network"
    REPLAY = "replay"
    READ_STORAGE = "read-storage"
    WRITE_STORAGE = "write-storage"
    ROLLBACK_STATE = "rollback-state"
    COMPROMISE_ENDPOINT = "compromise-endpoint"


class MaterialKind(str, Enum):
    SECRET_KEY = "secret-key"
    NONCE = "nonce"
    RANDOMNESS = "randomness"


class MaterialProperty(str, Enum):
    SECRET = "secret"
    PUBLIC = "public"
    UNPREDICTABLE = "unpredictable"
    UNIQUE_WITHIN_SCOPE = "unique-within-scope"
    AUTHENTIC = "authentic"


def _text(value: object, label: str) -> str:
    if type(value) is not str:
        raise TypeError(f"{label} must be a string")
    if value != value.strip() or not value:
        raise ValueError(f"{label} must be nonempty with no outer whitespace")
    if len(value) > MAX_TEXT_LENGTH:
        raise ValueError(f"{label} exceeds {MAX_TEXT_LENGTH} characters")
    return value


def _identifier(value: object, label: str) -> str:
    checked = _text(value, label)
    if IDENTIFIER_RE.fullmatch(checked) is None:
        raise ValueError(f"{label} must match {IDENTIFIER_RE.pattern}")
    return checked


def _typed_tuple(
    value: object,
    member_type: type,
    label: str,
    minimum: int,
    maximum: int,
) -> tuple:
    if type(value) is not tuple:
        raise TypeError(f"{label} must be a tuple")
    if not minimum <= len(value) <= maximum:
        raise ValueError(f"{label} must contain {minimum} through {maximum} items")
    if any(not isinstance(item, member_type) for item in value):
        raise TypeError(f"every {label} item must be {member_type.__name__}")
    return value


def _text_tuple(
    value: object, label: str, minimum: int = 1, maximum: int = 16
) -> tuple[str, ...]:
    checked = _typed_tuple(value, str, label, minimum, maximum)
    for index, item in enumerate(checked):
        _text(item, f"{label}[{index}]")
    return checked


def _enum_set(value: object, member_type: type[Enum], label: str) -> frozenset:
    if type(value) is not frozenset:
        raise TypeError(f"{label} must be a frozenset")
    if not value:
        raise ValueError(f"{label} must not be empty")
    if any(not isinstance(item, member_type) for item in value):
        raise TypeError(f"every {label} item must be {member_type.__name__}")
    return value


@dataclass(frozen=True, slots=True)
class Asset:
    identifier: str
    description: str
    goals: frozenset[SecurityGoal]

    def __post_init__(self) -> None:
        _identifier(self.identifier, "asset identifier")
        _text(self.description, "asset description")
        _enum_set(self.goals, SecurityGoal, "asset goals")


@dataclass(frozen=True, slots=True)
class AttackerModel:
    capabilities: frozenset[AttackerCapability]
    resource_bound: str
    exclusions: tuple[str, ...]

    def __post_init__(self) -> None:
        _enum_set(self.capabilities, AttackerCapability, "attacker capabilities")
        _text(self.resource_bound, "attacker resource bound")
        _text_tuple(self.exclusions, "attacker exclusions", 1, 16)


@dataclass(frozen=True, slots=True)
class Assumption:
    identifier: str
    statement: str
    owner: str
    falsification_signal: str

    def __post_init__(self) -> None:
        _identifier(self.identifier, "assumption identifier")
        _text(self.statement, "assumption statement")
        _text(self.owner, "assumption owner")
        _text(self.falsification_signal, "assumption falsification signal")


@dataclass(frozen=True, slots=True)
class TrustBoundary:
    identifier: str
    source_zone: str
    destination_zone: str
    crossing_data: str
    enforcement: str
    failure_response: str

    def __post_init__(self) -> None:
        _identifier(self.identifier, "boundary identifier")
        _text(self.source_zone, "boundary source zone")
        _text(self.destination_zone, "boundary destination zone")
        if self.source_zone == self.destination_zone:
            raise ValueError("a trust boundary must connect distinct zones")
        _text(self.crossing_data, "boundary crossing data")
        _text(self.enforcement, "boundary enforcement")
        _text(self.failure_response, "boundary failure response")


@dataclass(frozen=True, slots=True)
class MaterialRequirement:
    identifier: str
    kind: MaterialKind
    purpose: str
    properties: frozenset[MaterialProperty]
    source: str
    scope: str
    failure_response: str

    def __post_init__(self) -> None:
        _identifier(self.identifier, "material identifier")
        if not isinstance(self.kind, MaterialKind):
            raise TypeError("material kind must be MaterialKind")
        _text(self.purpose, "material purpose")
        _enum_set(self.properties, MaterialProperty, "material properties")
        _text(self.source, "material source")
        _text(self.scope, "material scope")
        _text(self.failure_response, "material failure response")


@dataclass(frozen=True, slots=True)
class SecurityRequirement:
    identifier: str
    asset_id: str
    goal: SecurityGoal
    attacker_capability: AttackerCapability
    security_statement: str
    failure_condition: str
    failure_response: str
    evidence_plan: str
    assumption_ids: tuple[str, ...]
    boundary_ids: tuple[str, ...]

    def __post_init__(self) -> None:
        _identifier(self.identifier, "requirement identifier")
        _identifier(self.asset_id, "requirement asset identifier")
        if not isinstance(self.goal, SecurityGoal):
            raise TypeError("requirement goal must be SecurityGoal")
        if not isinstance(self.attacker_capability, AttackerCapability):
            raise TypeError("requirement attacker capability must be AttackerCapability")
        _text(self.security_statement, "requirement security statement")
        _text(self.failure_condition, "requirement failure condition")
        _text(self.failure_response, "requirement failure response")
        _text(self.evidence_plan, "requirement evidence plan")
        for label, identifiers in (
            ("requirement assumption identifiers", self.assumption_ids),
            ("requirement boundary identifiers", self.boundary_ids),
        ):
            _text_tuple(identifiers, label, 1, 16)
            for identifier in identifiers:
                _identifier(identifier, label)


@dataclass(frozen=True, slots=True)
class CompositionDependency:
    identifier: str
    provider: str
    consumer: str
    required_property: str
    assumption_ids: tuple[str, ...]
    failure_response: str

    def __post_init__(self) -> None:
        _identifier(self.identifier, "dependency identifier")
        _text(self.provider, "dependency provider")
        _text(self.consumer, "dependency consumer")
        if self.provider == self.consumer:
            raise ValueError("dependency provider and consumer must differ")
        _text(self.required_property, "dependency required property")
        _text_tuple(self.assumption_ids, "dependency assumption identifiers", 1, 16)
        for identifier in self.assumption_ids:
            _identifier(identifier, "dependency assumption identifier")
        _text(self.failure_response, "dependency failure response")


@dataclass(frozen=True, slots=True)
class ThreatModel:
    name: str
    assets: tuple[Asset, ...]
    attacker: AttackerModel
    assumptions: tuple[Assumption, ...]
    boundaries: tuple[TrustBoundary, ...]
    materials: tuple[MaterialRequirement, ...]
    requirements: tuple[SecurityRequirement, ...]
    dependencies: tuple[CompositionDependency, ...]

    def __post_init__(self) -> None:
        _text(self.name, "model name")
        _typed_tuple(self.assets, Asset, "assets", 1, MAX_ASSETS)
        if not isinstance(self.attacker, AttackerModel):
            raise TypeError("attacker must be AttackerModel")
        _typed_tuple(
            self.assumptions,
            Assumption,
            "assumptions",
            1,
            MAX_ASSUMPTIONS,
        )
        _typed_tuple(
            self.boundaries,
            TrustBoundary,
            "boundaries",
            1,
            MAX_BOUNDARIES,
        )
        _typed_tuple(
            self.materials,
            MaterialRequirement,
            "materials",
            1,
            MAX_MATERIALS,
        )
        _typed_tuple(
            self.requirements,
            SecurityRequirement,
            "requirements",
            1,
            MAX_REQUIREMENTS,
        )
        _typed_tuple(
            self.dependencies,
            CompositionDependency,
            "dependencies",
            1,
            MAX_DEPENDENCIES,
        )


@dataclass(frozen=True, slots=True, order=True)
class Finding:
    code: str
    location: str
    message: str


@dataclass(frozen=True, slots=True)
class Evaluation:
    findings: tuple[Finding, ...]

    @property
    def structurally_complete(self) -> bool:
        return not self.findings

    @property
    def limitation(self) -> str:
        return (
            "Structural completeness only; this is not a cryptographic security "
            "proof, implementation review, or deployment approval."
        )


def _duplicates(items: tuple, attribute: str) -> set[str]:
    seen: set[str] = set()
    repeated: set[str] = set()
    for item in items:
        value = getattr(item, attribute)
        if value in seen:
            repeated.add(value)
        seen.add(value)
    return repeated


def evaluate_model(model: ThreatModel) -> Evaluation:
    """Return deterministic completeness findings for one bounded model."""

    if not isinstance(model, ThreatModel):
        raise TypeError("model must be ThreatModel")
    findings: list[Finding] = []

    collections = (
        ("asset", model.assets),
        ("assumption", model.assumptions),
        ("boundary", model.boundaries),
        ("material", model.materials),
        ("requirement", model.requirements),
        ("dependency", model.dependencies),
    )
    for label, items in collections:
        for identifier in sorted(_duplicates(items, "identifier")):
            findings.append(
                Finding("duplicate-id", f"{label}:{identifier}", "identifier is repeated")
            )

    assets = {asset.identifier: asset for asset in model.assets}
    assumptions = {item.identifier for item in model.assumptions}
    boundaries = {item.identifier for item in model.boundaries}
    referenced_assumptions: set[str] = set()
    referenced_boundaries: set[str] = set()
    covered_capabilities: set[AttackerCapability] = set()
    covered_goals: set[tuple[str, SecurityGoal]] = set()

    for requirement in model.requirements:
        location = f"requirement:{requirement.identifier}"
        asset = assets.get(requirement.asset_id)
        if asset is None:
            findings.append(
                Finding("unknown-asset", location, f"unknown asset {requirement.asset_id}")
            )
        elif requirement.goal not in asset.goals:
            findings.append(
                Finding(
                    "undeclared-goal",
                    location,
                    f"{requirement.goal.value} is not a goal of {asset.identifier}",
                )
            )
        else:
            covered_goals.add((asset.identifier, requirement.goal))

        if requirement.attacker_capability not in model.attacker.capabilities:
            findings.append(
                Finding(
                    "undeclared-capability",
                    location,
                    f"{requirement.attacker_capability.value} is outside the attacker model",
                )
            )
        else:
            covered_capabilities.add(requirement.attacker_capability)

        for identifier in requirement.assumption_ids:
            referenced_assumptions.add(identifier)
            if identifier not in assumptions:
                findings.append(
                    Finding("unknown-assumption", location, f"unknown assumption {identifier}")
                )
        for identifier in requirement.boundary_ids:
            referenced_boundaries.add(identifier)
            if identifier not in boundaries:
                findings.append(
                    Finding("unknown-boundary", location, f"unknown boundary {identifier}")
                )

    for asset in model.assets:
        for goal in asset.goals:
            if (asset.identifier, goal) not in covered_goals:
                findings.append(
                    Finding(
                        "uncovered-goal",
                        f"asset:{asset.identifier}",
                        f"no requirement covers {goal.value}",
                    )
                )

    for capability in model.attacker.capabilities - covered_capabilities:
        findings.append(
            Finding(
                "unaddressed-capability",
                "attacker",
                f"no requirement addresses {capability.value}",
            )
        )

    for material in model.materials:
        location = f"material:{material.identifier}"
        if {
            MaterialProperty.SECRET,
            MaterialProperty.PUBLIC,
        } <= material.properties:
            findings.append(
                Finding(
                    "contradictory-material-properties",
                    location,
                    "material cannot be both secret and public in one use",
                )
            )
        if material.kind is MaterialKind.SECRET_KEY:
            for needed in (MaterialProperty.SECRET, MaterialProperty.UNPREDICTABLE):
                if needed not in material.properties:
                    findings.append(
                        Finding(
                            "missing-key-property",
                            location,
                            f"teaching secret-key use must declare {needed.value}",
                        )
                    )
        elif material.kind is MaterialKind.NONCE:
            if MaterialProperty.UNIQUE_WITHIN_SCOPE not in material.properties:
                findings.append(
                    Finding(
                        "missing-nonce-uniqueness",
                        location,
                        "nonce use must declare uniqueness within its stated scope",
                    )
                )
        elif material.kind is MaterialKind.RANDOMNESS:
            if MaterialProperty.UNPREDICTABLE not in material.properties:
                findings.append(
                    Finding(
                        "missing-randomness-property",
                        location,
                        "security randomness must declare unpredictability",
                    )
                )

    for dependency in model.dependencies:
        location = f"dependency:{dependency.identifier}"
        for identifier in dependency.assumption_ids:
            referenced_assumptions.add(identifier)
            if identifier not in assumptions:
                findings.append(
                    Finding("unknown-assumption", location, f"unknown assumption {identifier}")
                )

    for identifier in assumptions - referenced_assumptions:
        findings.append(
            Finding(
                "unused-assumption",
                f"assumption:{identifier}",
                "assumption is not linked to a requirement or dependency",
            )
        )
    for identifier in boundaries - referenced_boundaries:
        findings.append(
            Finding(
                "unused-boundary",
                f"boundary:{identifier}",
                "boundary is not linked to a requirement",
            )
        )

    return Evaluation(tuple(sorted(findings)))


def render_evaluation(model: ThreatModel, evaluation: Evaluation) -> str:
    """Render stable text for review evidence without making a security claim."""

    if not isinstance(model, ThreatModel):
        raise TypeError("model must be ThreatModel")
    if not isinstance(evaluation, Evaluation):
        raise TypeError("evaluation must be Evaluation")
    lines = [
        f"model: {model.name}",
        f"requirements: {len(model.requirements)}",
        f"findings: {len(evaluation.findings)}",
        "review status: "
        + ("STRUCTURALLY-COMPLETE" if evaluation.structurally_complete else "INCOMPLETE"),
    ]
    lines.extend(
        f"{finding.code} [{finding.location}]: {finding.message}"
        for finding in evaluation.findings
    )
    lines.append(f"limit: {evaluation.limitation}")
    return "\n".join(lines)
