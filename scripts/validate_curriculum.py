#!/usr/bin/env python3
"""Validate the Orange School curriculum catalog and released material."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import defaultdict, deque
from pathlib import Path
from typing import Any
from urllib.parse import unquote


MODULE_ID_RE = re.compile(r"^[a-z]{3}-[0-9]{3}$")
SHA_RE = re.compile(r"^[0-9a-f]{40}$")
FORBIDDEN_PLACEHOLDER_RE = re.compile(r"\b(?:TODO|TBD|FIXME)\b")
MARKDOWN_LINK_RE = re.compile(r"!?\[[^\]]*\]\(([^)]+)\)")
FORBIDDEN_HOST_NETWORK_RE = re.compile(
    r"(?:https?://|ssh://|\bgit@|\b(?:curl|wget|nc|netcat)\b|git\s+(?:fetch|pull)\b|"
    r"\b(?:urllib\.request|http\.client|socket)\b)"
)
ALLOWED_COVERAGE = {"instruction", "practice", "assessment"}
ALLOWED_EXAMPLE_MODES = {
    "check-pass",
    "check-fail",
    "eval-pass",
    "eval-fail",
    "lex-pass",
    "lex-fail",
}
ALLOWED_HOST_RUNNERS = {"bash", "python"}

REQUIRED_FILES: dict[str, tuple[str, ...]] = {
    "lesson.md": (
        "## Learning objectives",
        "## Prerequisites",
        "## Lesson",
        "## Worked example",
        "## Check your understanding",
        "## Next step",
        "## Sources",
    ),
    "lab.md": (
        "## Goal",
        "## Setup",
        "## Tasks",
        "## Verification",
        "## Reflection",
    ),
    "assessment.md": (
        "## Instructions",
        "## Knowledge check",
        "## Independent task",
        "## Completion criteria",
    ),
    "rubric.md": (
        "## Rubric",
        "## Critical criteria",
        "## Scoring",
        "## Feedback and retry",
    ),
}


def _duplicates(values: list[str]) -> set[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return duplicates


def _safe_relative_path(value: Any) -> bool:
    if not isinstance(value, str) or not value:
        return False
    path = Path(value)
    return not path.is_absolute() and ".." not in path.parts


def _ids(items: Any, label: str, errors: list[str]) -> list[str]:
    if not isinstance(items, list):
        errors.append(f"{label} must be a list")
        return []
    values: list[str] = []
    for index, item in enumerate(items):
        if not isinstance(item, dict) or not isinstance(item.get("id"), str):
            errors.append(f"{label}[{index}] must have a string id")
            continue
        values.append(item["id"])
    for duplicate in sorted(_duplicates(values)):
        errors.append(f"duplicate {label} id: {duplicate}")
    return values


def load_catalog(root: Path) -> dict[str, Any]:
    catalog_path = root / "curriculum" / "catalog.json"
    try:
        value = json.loads(catalog_path.read_text(encoding="utf-8"))
    except FileNotFoundError as error:
        raise ValueError(f"missing catalog: {catalog_path}") from error
    except json.JSONDecodeError as error:
        raise ValueError(f"invalid JSON in {catalog_path}: {error}") from error
    if not isinstance(value, dict):
        raise ValueError("curriculum/catalog.json must contain one JSON object")
    return value


def validate_catalog(
    catalog: dict[str, Any], root: Path, *, check_materials: bool = True
) -> list[str]:
    errors: list[str] = []

    if catalog.get("schema_version") != 1:
        errors.append("schema_version must equal 1")
    if catalog.get("repository_url") != "https://github.com/chasebryan/orange-school":
        errors.append(
            "repository_url must equal https://github.com/chasebryan/orange-school"
        )
    curriculum_version = catalog.get("curriculum_version")
    if not isinstance(curriculum_version, str) or not re.fullmatch(
        r"[0-9]+\.[0-9]+\.[0-9]+(?:-[0-9A-Za-z.-]+)?", curriculum_version
    ):
        errors.append("curriculum_version must be a semantic version string")
    pass_percent = catalog.get("module_pass_percent")
    if not isinstance(pass_percent, int) or not 0 < pass_percent <= 100:
        errors.append("module_pass_percent must be an integer from 1 through 100")

    host_envelope = catalog.get("host_validation_envelope")
    if not isinstance(host_envelope, dict):
        errors.append("host_validation_envelope must be an object")
    else:
        expected_host_values = {
            "python_minimum": "3.11",
            "bash_minimum": "5.1",
            "git_minimum": "2.39",
            "c_standard": "C17",
            "rust_toolchain": "1.96.1",
            "network_required_for_checks": False,
        }
        for key, expected in expected_host_values.items():
            if host_envelope.get(key) != expected:
                errors.append(f"host_validation_envelope.{key} must equal {expected!r}")
        if not isinstance(host_envelope.get("claim"), str) or not host_envelope["claim"].strip():
            errors.append("host_validation_envelope.claim must be nonempty")

    orange_source = catalog.get("orange_source")
    source_ids: set[str] = set()
    if not isinstance(orange_source, dict):
        errors.append("orange_source must be an object")
    else:
        revision = orange_source.get("revision")
        if not isinstance(revision, str) or not SHA_RE.fullmatch(revision):
            errors.append("orange_source.revision must be a lowercase 40-character SHA")
        revision_context = orange_source.get("revision_context")
        if not isinstance(revision_context, str) or not revision_context.strip():
            errors.append("orange_source.revision_context must be nonempty")
        if orange_source.get("language_edition") != "2026":
            errors.append("orange_source.language_edition must equal 2026")
        stage_sets: dict[str, set[str]] = {}
        for field in ("implemented_stages", "active_stages", "pending_stages"):
            values = orange_source.get(field)
            if not isinstance(values, list) or not values or not all(
                isinstance(value, str) and re.fullmatch(r"S[1-8]", value)
                for value in values
            ):
                errors.append(f"orange_source.{field} must be a nonempty S1-S8 list")
                stage_sets[field] = set()
                continue
            for duplicate in sorted(_duplicates(values)):
                errors.append(f"orange_source.{field} repeats {duplicate}")
            stage_sets[field] = set(values)
        if set().union(*stage_sets.values()) != {f"S{number}" for number in range(1, 9)}:
            errors.append("Orange stage states must cover exactly S1 through S8")
        if sum(len(values) for values in stage_sets.values()) != len(
            set().union(*stage_sets.values())
        ):
            errors.append("Orange stage states must be disjoint")
        slices = orange_source.get("implemented_slices")
        if not isinstance(slices, list) or not slices or not all(
            isinstance(value, str) and re.fullmatch(r"S[1-8][a-z]", value)
            for value in slices
        ):
            errors.append("orange_source.implemented_slices must be a nonempty stage-slice list")
        elif "S3a" not in slices:
            errors.append("orange_source.implemented_slices must include S3a")
        source_values = _ids(orange_source.get("sources"), "source", errors)
        source_ids = set(source_values)
        for source in orange_source.get("sources", []):
            if not isinstance(source, dict) or "id" not in source:
                continue
            if not _safe_relative_path(source.get("path")):
                errors.append(f"source {source['id']} has an unsafe or missing path")
            if source.get("status") not in {
                "normative",
                "directed",
                "implemented",
                "proposed",
            }:
                errors.append(f"source {source['id']} has an invalid status")

    status_ids = set(catalog.get("statuses", {}).keys())
    if status_ids != {"released", "planned", "blocked"}:
        errors.append("statuses must define exactly released, planned, and blocked")
    maturity_ids = set(catalog.get("source_maturities", {}).keys())
    if maturity_ids != {"general", "implemented", "ratified", "proposed"}:
        errors.append(
            "source_maturities must define exactly general, implemented, ratified, and proposed"
        )

    role_values = _ids(catalog.get("roles"), "role", errors)
    role_ids = set(role_values)
    expected_roles = {f"P-{number:02d}" for number in range(1, 6)}
    if role_ids != expected_roles:
        errors.append("roles must contain exactly P-01 through P-05")

    journey_values = _ids(catalog.get("journeys"), "journey", errors)
    journey_ids = set(journey_values)
    expected_journeys = {f"J-{number:02d}" for number in range(1, 9)}
    if journey_ids != expected_journeys:
        errors.append("journeys must contain exactly J-01 through J-08")

    stage_values = _ids(catalog.get("stages"), "stage", errors)
    stage_ids = set(stage_values)
    stage_orders: dict[str, int] = {}
    if isinstance(catalog.get("stages"), list):
        orders: list[int] = []
        for stage in catalog["stages"]:
            if not isinstance(stage, dict) or not isinstance(stage.get("id"), str):
                continue
            order = stage.get("order")
            if not isinstance(order, int):
                errors.append(f"stage {stage['id']} order must be an integer")
                continue
            orders.append(order)
            stage_orders[stage["id"]] = order
            if not isinstance(stage.get("title"), str) or not stage["title"].strip():
                errors.append(f"stage {stage['id']} must have a title")
        if sorted(orders) != list(range(len(orders))):
            errors.append("stage orders must be unique and contiguous from zero")

    competency_values = _ids(catalog.get("competencies"), "competency", errors)
    competency_ids = set(competency_values)
    for competency in catalog.get("competencies", []):
        if not isinstance(competency, dict) or "id" not in competency:
            continue
        if not isinstance(competency.get("description"), str) or not competency[
            "description"
        ].strip():
            errors.append(f"competency {competency['id']} must have a description")
        if competency.get("domain") not in stage_ids | {"orange", "specialization"}:
            errors.append(f"competency {competency['id']} has an unknown domain")

    modules = catalog.get("modules")
    module_values = _ids(modules, "module", errors)
    module_ids = set(module_values)
    module_by_id = {
        module["id"]: module
        for module in modules or []
        if isinstance(module, dict) and isinstance(module.get("id"), str)
    }
    entry_module = catalog.get("entry_module")
    if entry_module not in module_ids:
        errors.append("entry_module must reference an existing module")

    outcome_ids: list[str] = []
    example_ids: list[str] = []
    host_check_ids: list[str] = []
    mapped_competencies: defaultdict[str, set[str]] = defaultdict(set)
    mapped_journeys: defaultdict[str, set[str]] = defaultdict(set)
    mapped_roles: defaultdict[str, set[str]] = defaultdict(set)
    adjacency: defaultdict[str, list[str]] = defaultdict(list)
    indegree = {module_id: 0 for module_id in module_ids}

    required_module_fields = {
        "id",
        "title",
        "stage",
        "status",
        "source_maturity",
        "prerequisites",
        "estimated_hours",
        "summary",
        "competencies",
        "journeys",
        "roles",
    }

    for module_id, module in module_by_id.items():
        missing_fields = sorted(required_module_fields - set(module))
        if missing_fields:
            errors.append(f"module {module_id} missing fields: {', '.join(missing_fields)}")
        if not MODULE_ID_RE.fullmatch(module_id):
            errors.append(f"module id has invalid format: {module_id}")
        if not isinstance(module.get("title"), str) or not module["title"].strip():
            errors.append(f"module {module_id} must have a title")
        if not isinstance(module.get("summary"), str) or not module["summary"].strip():
            errors.append(f"module {module_id} must have a summary")
        if module.get("stage") not in stage_ids:
            errors.append(f"module {module_id} references unknown stage {module.get('stage')}")
        if module.get("status") not in status_ids:
            errors.append(f"module {module_id} has invalid status {module.get('status')}")
        if module.get("source_maturity") not in maturity_ids:
            errors.append(
                f"module {module_id} has invalid source_maturity {module.get('source_maturity')}"
            )
        hours = module.get("estimated_hours")
        if not isinstance(hours, (int, float)) or isinstance(hours, bool) or hours <= 0:
            errors.append(f"module {module_id} estimated_hours must be positive")

        prerequisites = module.get("prerequisites")
        if not isinstance(prerequisites, list) or not all(
            isinstance(value, str) for value in prerequisites
        ):
            errors.append(f"module {module_id} prerequisites must be a string list")
            prerequisites = []
        for duplicate in sorted(_duplicates(prerequisites)):
            errors.append(f"module {module_id} repeats prerequisite {duplicate}")
        for prerequisite in prerequisites:
            if prerequisite not in module_ids:
                errors.append(f"module {module_id} has unknown prerequisite {prerequisite}")
                continue
            adjacency[prerequisite].append(module_id)
            indegree[module_id] += 1
            prerequisite_module = module_by_id[prerequisite]
            module_order = stage_orders.get(module.get("stage"))
            prerequisite_order = stage_orders.get(prerequisite_module.get("stage"))
            if (
                module_order is not None
                and prerequisite_order is not None
                and prerequisite_order > module_order
            ):
                errors.append(
                    f"module {module_id} depends on later-stage module {prerequisite}"
                )

        status = module.get("status")
        maturity = module.get("source_maturity")
        if status == "released" and maturity not in {"general", "implemented"}:
            errors.append(
                f"released module {module_id} cannot have {maturity} source maturity"
            )
        if status == "released":
            for prerequisite in prerequisites:
                prerequisite_module = module_by_id.get(prerequisite)
                if prerequisite_module and prerequisite_module.get("status") != "released":
                    errors.append(
                        f"released module {module_id} has unreleased prerequisite {prerequisite}"
                    )
        if status == "blocked":
            blockers = module.get("blocked_by")
            if not isinstance(blockers, list) or not blockers or not all(
                isinstance(value, str) and value.strip() for value in blockers
            ):
                errors.append(f"blocked module {module_id} must have nonempty blocked_by")
        elif "blocked_by" in module:
            errors.append(f"non-blocked module {module_id} must not define blocked_by")

        source_refs = module.get("source_refs", [])
        if not isinstance(source_refs, list) or not all(
            isinstance(value, str) for value in source_refs
        ):
            errors.append(f"module {module_id} source_refs must be a string list")
            source_refs = []
        for source_ref in source_refs:
            if source_ref not in source_ids:
                errors.append(f"module {module_id} references unknown source {source_ref}")
        if maturity != "general" and not source_refs:
            errors.append(f"Orange-specific module {module_id} must cite source_refs")

        competency_mappings = module.get("competencies")
        if not isinstance(competency_mappings, list) or not competency_mappings:
            errors.append(f"module {module_id} must map at least one competency")
            competency_mappings = []
        local_competency_ids: list[str] = []
        for mapping in competency_mappings:
            if not isinstance(mapping, dict) or not isinstance(mapping.get("id"), str):
                errors.append(f"module {module_id} has malformed competency mapping")
                continue
            competency_id = mapping["id"]
            local_competency_ids.append(competency_id)
            if competency_id not in competency_ids:
                errors.append(f"module {module_id} maps unknown competency {competency_id}")
            coverage = mapping.get("coverage")
            if not isinstance(coverage, list) or set(coverage) != ALLOWED_COVERAGE:
                errors.append(
                    f"module {module_id} competency {competency_id} must map instruction, practice, and assessment"
                )
            mapped_competencies[competency_id].add(module_id)
        for duplicate in sorted(_duplicates(local_competency_ids)):
            errors.append(f"module {module_id} repeats competency {duplicate}")

        for field, valid_ids, mapped in (
            ("journeys", journey_ids, mapped_journeys),
            ("roles", role_ids, mapped_roles),
        ):
            values = module.get(field)
            if not isinstance(values, list) or not all(isinstance(value, str) for value in values):
                errors.append(f"module {module_id} {field} must be a string list")
                continue
            for duplicate in sorted(_duplicates(values)):
                errors.append(f"module {module_id} repeats {field[:-1]} {duplicate}")
            for value in values:
                if value not in valid_ids:
                    errors.append(f"module {module_id} references unknown {field[:-1]} {value}")
                mapped[value].add(module_id)

        outcomes = module.get("outcomes", [])
        if status == "released" and (not isinstance(outcomes, list) or not outcomes):
            errors.append(f"released module {module_id} must define outcomes")
            outcomes = []
        if not isinstance(outcomes, list):
            errors.append(f"module {module_id} outcomes must be a list when present")
            outcomes = []
        local_outcomes: list[str] = []
        for outcome in outcomes:
            if not isinstance(outcome, dict) or not isinstance(outcome.get("id"), str):
                errors.append(f"module {module_id} has malformed outcome")
                continue
            outcome_id = outcome["id"]
            local_outcomes.append(outcome_id)
            outcome_ids.append(outcome_id)
            if not isinstance(outcome.get("text"), str) or not outcome["text"].strip():
                errors.append(f"outcome {outcome_id} must have text")
        for duplicate in sorted(_duplicates(local_outcomes)):
            errors.append(f"module {module_id} repeats outcome {duplicate}")

        examples = module.get("examples", [])
        if status == "released" and not isinstance(examples, list):
            errors.append(f"released module {module_id} examples must be a list")
            examples = []
        if examples and not isinstance(examples, list):
            errors.append(f"module {module_id} examples must be a list")
            examples = []
        for example in examples:
            if not isinstance(example, dict) or not isinstance(example.get("id"), str):
                errors.append(f"module {module_id} has malformed example")
                continue
            example_id = example["id"]
            example_ids.append(example_id)
            mode = example.get("mode")
            if mode not in ALLOWED_EXAMPLE_MODES:
                errors.append(f"example {example_id} has invalid mode {mode}")
            path_value = example.get("path")
            if not _safe_relative_path(path_value):
                errors.append(f"example {example_id} has an unsafe or missing path")
            if isinstance(mode, str) and mode.endswith("-fail") and not isinstance(
                example.get("stderr_contains"), str
            ):
                errors.append(f"failing example {example_id} must define stderr_contains")
            stdout_file = example.get("stdout_file")
            if stdout_file is not None and not _safe_relative_path(stdout_file):
                errors.append(f"example {example_id} has an unsafe stdout_file")

        host_checks = module.get("host_checks", [])
        if not isinstance(host_checks, list):
            errors.append(f"module {module_id} host_checks must be a list when present")
            host_checks = []
        if (
            status == "released"
            and maturity == "general"
            and module.get("stage") != "orientation"
            and not host_checks
        ):
            errors.append(
                f"released general module {module_id} must register a host check"
            )
        for host_check in host_checks:
            if not isinstance(host_check, dict) or not isinstance(host_check.get("id"), str):
                errors.append(f"module {module_id} has malformed host check")
                continue
            host_check_id = host_check["id"]
            host_check_ids.append(host_check_id)
            runner = host_check.get("runner")
            if runner not in ALLOWED_HOST_RUNNERS:
                errors.append(f"host check {host_check_id} has invalid runner {runner}")
            host_path = host_check.get("path")
            if not _safe_relative_path(host_path):
                errors.append(f"host check {host_check_id} has an unsafe or missing path")
            elif not host_path.startswith(
                f"curriculum/modules/{module_id}/checks/lab_smoke."
            ):
                errors.append(
                    f"host check {host_check_id} must use the module checks/lab_smoke path"
                )
            elif runner == "bash" and not host_path.endswith(".sh"):
                errors.append(f"bash host check {host_check_id} must use a .sh file")
            elif runner == "python" and not host_path.endswith(".py"):
                errors.append(f"python host check {host_check_id} must use a .py file")

        if status == "released" and check_materials:
            _validate_released_material(
                root, module_id, module, local_outcomes, errors
            )

    for duplicate in sorted(_duplicates(outcome_ids)):
        errors.append(f"duplicate outcome id: {duplicate}")
    for duplicate in sorted(_duplicates(example_ids)):
        errors.append(f"duplicate example id: {duplicate}")
    for duplicate in sorted(_duplicates(host_check_ids)):
        errors.append(f"duplicate host check id: {duplicate}")

    for competency_id in sorted(competency_ids - set(mapped_competencies)):
        errors.append(f"competency {competency_id} is not mapped by any module")
    for journey_id in sorted(journey_ids - set(mapped_journeys)):
        errors.append(f"journey {journey_id} is not mapped by any module")
    for role_id in sorted(role_ids - set(mapped_roles)):
        errors.append(f"role {role_id} is not mapped by any module")

    _validate_graph(module_ids, entry_module, adjacency, indegree, errors)
    _validate_tracks(catalog, module_by_id, role_ids, errors)
    if check_materials:
        for generated in sorted((root / "curriculum").rglob("*")):
            if generated.name == "__pycache__" or generated.suffix == ".pyc":
                errors.append(
                    f"generated Python artifact must not be stored in curriculum: "
                    f"{generated.relative_to(root)}"
                )
        _validate_internal_links(root, errors)
        _validate_status_document(catalog, root, errors)
        workflow = root / ".github" / "workflows" / "ci.yml"
        revision = catalog.get("orange_source", {}).get("revision")
        if not workflow.is_file():
            errors.append("missing .github/workflows/ci.yml")
        elif isinstance(revision, str) and revision not in workflow.read_text(encoding="utf-8"):
            errors.append("CI workflow does not pin the catalog Orange revision")
    return errors


def _validate_status_document(
    catalog: dict[str, Any], root: Path, errors: list[str]
) -> None:
    path = root / "docs" / "current-status.md"
    if not path.is_file():
        errors.append("missing docs/current-status.md")
        return
    text = path.read_text(encoding="utf-8")
    normalized_text = " ".join(text.split())
    summary = completion_summary(catalog)
    expected_version = f"Curriculum version `{catalog.get('curriculum_version')}`"
    expected_modules = (
        f"The catalog contains {summary['modules']} modules: {summary['released']} released, "
        f"{summary['planned']} planned, and {summary['blocked']} blocked."
    )
    expected_checks = (
        f"{summary['host_checks']} host-language smoke checks and "
        f"{summary['orange_examples']} pinned Orange examples pass."
    )
    for expected, label in (
        (expected_version, "curriculum version"),
        (expected_modules, "module status counts"),
        (expected_checks, "executable evidence counts"),
    ):
        if " ".join(expected.split()) not in normalized_text:
            errors.append(f"docs/current-status.md does not match catalog {label}")


def _validate_released_material(
    root: Path,
    module_id: str,
    module: dict[str, Any],
    outcome_ids: list[str],
    errors: list[str],
) -> None:
    material_value = module.get("material")
    if not _safe_relative_path(material_value):
        errors.append(f"released module {module_id} has an unsafe or missing material path")
        return
    expected_material = f"curriculum/modules/{module_id}"
    if material_value != expected_material:
        errors.append(
            f"released module {module_id} material must be {expected_material}"
        )
    material = root / material_value
    if not material.is_dir():
        errors.append(f"released module {module_id} material directory is missing")
        return

    contents: dict[str, str] = {}
    for filename, headings in REQUIRED_FILES.items():
        path = material / filename
        if not path.is_file():
            errors.append(f"released module {module_id} missing {filename}")
            continue
        text = path.read_text(encoding="utf-8")
        contents[filename] = text
        if not text.startswith("# "):
            errors.append(f"released module {module_id} {filename} must start with an H1")
        lines = set(text.splitlines())
        for heading in headings:
            if heading not in lines:
                errors.append(
                    f"released module {module_id} {filename} missing heading {heading}"
                )
        match = FORBIDDEN_PLACEHOLDER_RE.search(text)
        if match:
            errors.append(
                f"released module {module_id} {filename} contains placeholder {match.group(0)}"
            )

    lesson = contents.get("lesson.md", "")
    assessment = contents.get("assessment.md", "")
    rubric = contents.get("rubric.md", "")
    for outcome_id in outcome_ids:
        if outcome_id not in lesson:
            errors.append(f"outcome {outcome_id} is absent from lesson.md")
        if outcome_id not in assessment:
            errors.append(f"outcome {outcome_id} is absent from assessment.md")
    if rubric:
        if "100" not in rubric:
            errors.append(f"released module {module_id} rubric.md must define a 100-point scale")
        if not re.search(r"80\s*(?:/\s*100|%)", rubric):
            errors.append(f"released module {module_id} rubric.md must define the 80-point threshold")
        if "critical" not in rubric.lower():
            errors.append(f"released module {module_id} rubric.md must define critical criteria")

    for code_path in sorted(material.rglob("*")):
        if not code_path.is_file() or code_path.suffix not in {".py", ".sh", ".c", ".h", ".rs"}:
            continue
        if FORBIDDEN_HOST_NETWORK_RE.search(code_path.read_text(encoding="utf-8")):
            errors.append(
                f"released module {module_id} code references a network operation: "
                f"{code_path.relative_to(root)}"
            )

    for example in module.get("examples", []):
        if not isinstance(example, dict) or not _safe_relative_path(example.get("path")):
            continue
        example_path = root / example["path"]
        if not example_path.is_file():
            errors.append(f"example {example.get('id', '<unknown>')} file is missing")
            continue
        try:
            example_path.relative_to(material)
        except ValueError:
            errors.append(
                f"example {example.get('id', '<unknown>')} must be inside module {module_id}"
            )
        stdout_file = example.get("stdout_file")
        if _safe_relative_path(stdout_file):
            stdout_path = root / stdout_file
            if not stdout_path.is_file():
                errors.append(f"example {example.get('id', '<unknown>')} stdout_file is missing")
            else:
                try:
                    stdout_path.relative_to(material)
                except ValueError:
                    errors.append(
                        f"example {example.get('id', '<unknown>')} stdout_file must be inside module {module_id}"
                    )

    for host_check in module.get("host_checks", []):
        if not isinstance(host_check, dict) or not _safe_relative_path(host_check.get("path")):
            continue
        host_path = root / host_check["path"]
        if not host_path.is_file():
            errors.append(f"host check {host_check.get('id', '<unknown>')} file is missing")
            continue
        host_text = host_path.read_text(encoding="utf-8")
        if FORBIDDEN_HOST_NETWORK_RE.search(host_text):
            errors.append(
                f"host check {host_check.get('id', '<unknown>')} references a network operation"
            )
        try:
            host_path.relative_to(material)
        except ValueError:
            errors.append(
                f"host check {host_check.get('id', '<unknown>')} must be inside module {module_id}"
            )


def _validate_graph(
    module_ids: set[str],
    entry_module: Any,
    adjacency: defaultdict[str, list[str]],
    indegree: dict[str, int],
    errors: list[str],
) -> None:
    work_indegree = dict(indegree)
    queue = deque(sorted(module_id for module_id, degree in work_indegree.items() if degree == 0))
    visited: list[str] = []
    while queue:
        module_id = queue.popleft()
        visited.append(module_id)
        for dependent in sorted(adjacency[module_id]):
            work_indegree[dependent] -= 1
            if work_indegree[dependent] == 0:
                queue.append(dependent)
    if len(visited) != len(module_ids):
        cycle_nodes = sorted(module_ids - set(visited))
        errors.append(f"prerequisite graph contains a cycle involving: {', '.join(cycle_nodes)}")

    if entry_module not in module_ids:
        return
    reachable = {entry_module}
    queue = deque([entry_module])
    while queue:
        module_id = queue.popleft()
        for dependent in adjacency[module_id]:
            if dependent not in reachable:
                reachable.add(dependent)
                queue.append(dependent)
    for module_id in sorted(module_ids - reachable):
        errors.append(f"module {module_id} is unreachable from {entry_module}")


def _validate_internal_links(root: Path, errors: list[str]) -> None:
    ignored_parts = {
        ".git",
        ".agents",
        ".codex",
        ".orange-source",
        "__pycache__",
    }
    for markdown in sorted(root.rglob("*.md")):
        try:
            relative_markdown = markdown.relative_to(root)
        except ValueError:
            continue
        if ignored_parts.intersection(relative_markdown.parts):
            continue
        text = markdown.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK_RE.findall(text):
            target = raw_target.strip()
            if target.startswith("<") and ">" in target:
                target = target[1 : target.index(">")]
            elif " " in target:
                target = target.split(" ", 1)[0]
            if not target or target.startswith("#"):
                continue
            if re.match(r"^[A-Za-z][A-Za-z0-9+.-]*:", target):
                continue
            path_text = unquote(target.split("#", 1)[0])
            if not path_text:
                continue
            linked = (markdown.parent / path_text).resolve()
            try:
                linked.relative_to(root)
            except ValueError:
                errors.append(
                    f"internal link escapes repository: {relative_markdown} -> {raw_target}"
                )
                continue
            if not linked.exists():
                errors.append(
                    f"broken internal link: {relative_markdown} -> {raw_target}"
                )


def _validate_tracks(
    catalog: dict[str, Any],
    module_by_id: dict[str, dict[str, Any]],
    role_ids: set[str],
    errors: list[str],
) -> None:
    track_values = _ids(catalog.get("tracks"), "track", errors)
    track_ids = set(track_values)
    track_by_id = {
        track["id"]: track
        for track in catalog.get("tracks", [])
        if isinstance(track, dict) and isinstance(track.get("id"), str)
    }

    for track_id, track in track_by_id.items():
        if track.get("status") not in {"released", "planned", "blocked"}:
            errors.append(f"track {track_id} has invalid status")
        if track.get("kind") not in {"sampler", "core", "specialization"}:
            errors.append(f"track {track_id} has invalid kind")
        modules = track.get("modules")
        if not isinstance(modules, list) or not modules or not all(
            isinstance(value, str) for value in modules
        ):
            errors.append(f"track {track_id} modules must be a nonempty string list")
            modules = []
        for duplicate in sorted(_duplicates(modules)):
            errors.append(f"track {track_id} repeats module {duplicate}")
        for module_id in modules:
            if module_id not in module_by_id:
                errors.append(f"track {track_id} references unknown module {module_id}")
        roles = track.get("roles")
        if not isinstance(roles, list) or not all(isinstance(value, str) for value in roles):
            errors.append(f"track {track_id} roles must be a string list")
            roles = []
        for role_id in roles:
            if role_id not in role_ids:
                errors.append(f"track {track_id} references unknown role {role_id}")
        inherited = track.get("inherits")
        if inherited is not None and inherited not in track_ids:
            errors.append(f"track {track_id} inherits unknown track {inherited}")
        resolved = _resolve_track_modules(track_id, track_by_id, errors)
        for duplicate in sorted(_duplicates(resolved)):
            errors.append(f"track {track_id} repeats inherited module {duplicate}")
        position = {module_id: index for index, module_id in enumerate(resolved)}
        for module_id in resolved:
            module = module_by_id.get(module_id)
            if not module:
                continue
            for prerequisite in module.get("prerequisites", []):
                if prerequisite not in position:
                    errors.append(
                        f"track {track_id} omits prerequisite {prerequisite} for {module_id}"
                    )
                elif position[prerequisite] >= position[module_id]:
                    errors.append(
                        f"track {track_id} places prerequisite {prerequisite} after {module_id}"
                    )
        if track.get("status") == "released":
            for module_id in resolved:
                module = module_by_id.get(module_id)
                if module and module.get("status") != "released":
                    errors.append(
                        f"released track {track_id} contains unreleased module {module_id}"
                    )

    for track_id in track_ids:
        _resolve_track_modules(track_id, track_by_id, errors)

    specializations = [
        track for track in track_by_id.values() if track.get("kind") == "specialization"
    ]
    if len(specializations) != 5:
        errors.append("there must be exactly five specialization tracks")
    specialized_roles: list[str] = []
    for track in specializations:
        track_id = track["id"]
        roles = track.get("roles", [])
        if len(roles) != 1:
            errors.append(f"specialization track {track_id} must serve exactly one role")
        else:
            specialized_roles.append(roles[0])
        if track.get("inherits") != "professional-core":
            errors.append(f"specialization track {track_id} must inherit professional-core")
        capstone = track.get("capstone")
        modules = track.get("modules", [])
        if capstone not in module_by_id:
            errors.append(f"specialization track {track_id} has unknown capstone")
        if not modules or modules[-1] != capstone:
            errors.append(f"specialization track {track_id} capstone must be its final module")
        module = module_by_id.get(capstone)
        if module and roles and set(module.get("roles", [])) != set(roles):
            errors.append(f"specialization track {track_id} capstone role does not match")
        if module:
            if module.get("pass_percent") != catalog.get("module_pass_percent"):
                errors.append(
                    f"specialization track {track_id} capstone must declare the global pass threshold"
                )
            critical = module.get("critical_criteria")
            if (
                not isinstance(critical, list)
                or len(critical) < 3
                or not all(isinstance(value, str) and value.strip() for value in critical)
            ):
                errors.append(
                    f"specialization track {track_id} capstone must declare at least three critical criteria"
                )
    if set(specialized_roles) != role_ids or len(specialized_roles) != len(role_ids):
        errors.append("specialization tracks must cover each role exactly once")


def _resolve_track_modules(
    track_id: str,
    track_by_id: dict[str, dict[str, Any]],
    errors: list[str],
    stack: tuple[str, ...] = (),
) -> list[str]:
    if track_id in stack:
        errors.append(f"track inheritance contains a cycle involving {track_id}")
        return []
    track = track_by_id.get(track_id)
    if not track:
        return []
    result: list[str] = []
    inherited = track.get("inherits")
    if isinstance(inherited, str):
        result.extend(_resolve_track_modules(inherited, track_by_id, errors, stack + (track_id,)))
    modules = track.get("modules")
    if isinstance(modules, list):
        result.extend(value for value in modules if isinstance(value, str))
    return result


def completion_summary(catalog: dict[str, Any]) -> dict[str, Any]:
    modules = catalog.get("modules", [])
    by_status: defaultdict[str, int] = defaultdict(int)
    for module in modules:
        if isinstance(module, dict):
            by_status[str(module.get("status"))] += 1
    released_modules = [
        module
        for module in modules
        if isinstance(module, dict) and module.get("status") == "released"
    ]
    return {
        "modules": len(modules),
        "released": by_status["released"],
        "planned": by_status["planned"],
        "blocked": by_status["blocked"],
        "competencies": len(catalog.get("competencies", [])),
        "journeys": len(catalog.get("journeys", [])),
        "roles": len(catalog.get("roles", [])),
        "host_checks": sum(len(module.get("host_checks", [])) for module in released_modules),
        "orange_examples": sum(len(module.get("examples", [])) for module in released_modules),
        "professionally_complete": bool(modules)
        and all(
            isinstance(module, dict) and module.get("status") == "released"
            for module in modules
        ),
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--format", choices=("text", "json"), default="text")
    parser.add_argument("--require-professional-complete", action="store_true")
    args = parser.parse_args(argv)
    root = args.root.resolve()
    try:
        catalog = load_catalog(root)
    except ValueError as error:
        if args.format == "json":
            print(json.dumps({"ok": False, "errors": [str(error)]}, indent=2))
        else:
            print(f"curriculum validation failed: {error}", file=sys.stderr)
        return 1

    errors = validate_catalog(catalog, root)
    summary = completion_summary(catalog)
    if args.require_professional_complete and not summary["professionally_complete"]:
        errors.append("professional completion was required but unreleased modules remain")

    if args.format == "json":
        print(json.dumps({"ok": not errors, "summary": summary, "errors": errors}, indent=2))
    elif errors:
        print("curriculum validation failed:", file=sys.stderr)
        for error in errors:
            print(f"- {error}", file=sys.stderr)
    else:
        print(
            "curriculum validation passed: "
            f"{summary['modules']} modules "
            f"({summary['released']} released, {summary['planned']} planned, "
            f"{summary['blocked']} blocked), {summary['competencies']} competencies, "
            f"{summary['journeys']} journeys, {summary['roles']} roles, "
            f"{summary['host_checks']} host checks, {summary['orange_examples']} Orange examples"
        )
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
