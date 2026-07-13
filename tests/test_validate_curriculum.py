from __future__ import annotations

import copy
import importlib.util
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "validate_curriculum", ROOT / "scripts" / "validate_curriculum.py"
)
assert SPEC and SPEC.loader
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class CurriculumValidationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.catalog = VALIDATOR.load_catalog(ROOT)

    def validate(self, catalog: dict, *, materials: bool = False) -> list[str]:
        return VALIDATOR.validate_catalog(catalog, ROOT, check_materials=materials)

    def test_repository_catalog_and_materials_are_valid(self) -> None:
        self.assertEqual(self.validate(self.catalog, materials=True), [])

    def test_repository_home_is_canonical(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["repository_url"] = "https://example.invalid/orange-school"
        errors = self.validate(catalog)
        self.assertIn(
            "repository_url must equal https://github.com/chasebryan/orange-school",
            errors,
        )

    def test_orange_stage_states_must_be_disjoint(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["orange_source"]["pending_stages"].append("S3")
        errors = self.validate(catalog)
        self.assertIn("Orange stage states must be disjoint", errors)

    def test_orange_stage_states_must_cover_every_stage(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["orange_source"]["pending_stages"].remove("S8")
        errors = self.validate(catalog)
        self.assertIn("Orange stage states must cover exactly S1 through S8", errors)

    def test_eval_example_modes_are_validated(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        module = next(item for item in catalog["modules"] if item["id"] == "org-101")
        module["examples"][0]["mode"] = "eval-fail"
        module["examples"][0]["stderr_contains"] = "expected diagnostic"
        errors = self.validate(catalog)
        self.assertFalse(any("invalid mode eval-fail" in error for error in errors))

    def test_failing_eval_requires_expected_diagnostic(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        module = next(item for item in catalog["modules"] if item["id"] == "org-101")
        module["examples"][0]["mode"] = "eval-fail"
        module["examples"][0].pop("stderr_contains", None)
        errors = self.validate(catalog)
        self.assertTrue(
            any("failing example" in error and "stderr_contains" in error for error in errors)
        )

    def test_unknown_prerequisite_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["modules"][1]["prerequisites"] = ["missing-999"]
        errors = self.validate(catalog)
        self.assertTrue(any("unknown prerequisite missing-999" in error for error in errors))

    def test_cycle_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["modules"][0]["prerequisites"] = ["org-103"]
        errors = self.validate(catalog)
        self.assertTrue(any("contains a cycle" in error for error in errors))

    def test_released_proposed_module_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["modules"][0]["source_maturity"] = "proposed"
        errors = self.validate(catalog)
        self.assertTrue(any("cannot have proposed source maturity" in error for error in errors))

    def test_unreleased_prerequisite_is_rejected_for_released_module(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        module = next(item for item in catalog["modules"] if item["id"] == "org-101")
        module["prerequisites"] = ["org-202"]
        errors = self.validate(catalog)
        self.assertTrue(any("has unreleased prerequisite org-202" in error for error in errors))

    def test_unassessed_outcome_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["modules"][0]["outcomes"][0]["id"] = "ORI-001-MISSING"
        errors = self.validate(catalog, materials=True)
        self.assertTrue(
            any("ORI-001-MISSING is absent from assessment.md" in error for error in errors)
        )

    def test_missing_journey_coverage_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        for module in catalog["modules"]:
            module["journeys"] = [value for value in module["journeys"] if value != "J-04"]
        errors = self.validate(catalog)
        self.assertIn("journey J-04 is not mapped by any module", errors)

    def test_duplicate_specialization_role_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        audit = next(track for track in catalog["tracks"] if track["id"] == "audit")
        audit["roles"] = ["P-04"]
        errors = self.validate(catalog)
        self.assertTrue(
            any("specialization tracks must cover each role exactly once" in error for error in errors)
        )

    def test_released_general_module_requires_host_check(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        module = next(item for item in catalog["modules"] if item["id"] == "cmp-101")
        module["host_checks"] = []
        errors = self.validate(catalog)
        self.assertIn("released general module cmp-101 must register a host check", errors)

    def test_duplicate_host_check_id_is_rejected(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        first = next(item for item in catalog["modules"] if item["id"] == "cmp-101")
        second = next(item for item in catalog["modules"] if item["id"] == "cmp-102")
        second["host_checks"][0]["id"] = first["host_checks"][0]["id"]
        errors = self.validate(catalog)
        self.assertTrue(any("duplicate host check id" in error for error in errors))

    def test_host_check_path_must_stay_inside_module(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        module = next(item for item in catalog["modules"] if item["id"] == "cmp-101")
        module["host_checks"][0]["path"] = "scripts/check_host_examples.py"
        errors = self.validate(catalog, materials=True)
        self.assertTrue(any("must be inside module cmp-101" in error for error in errors))

    def test_capstone_must_declare_pass_threshold(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        capstone = next(item for item in catalog["modules"] if item["id"] == "cap-201")
        capstone["pass_percent"] = 70
        errors = self.validate(catalog)
        self.assertTrue(any("capstone must declare the global pass threshold" in error for error in errors))

    def test_status_document_must_match_catalog_version(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        catalog["curriculum_version"] = "99.0.0-test"
        errors = self.validate(catalog, materials=True)
        self.assertIn("docs/current-status.md does not match catalog curriculum version", errors)

    def test_track_cannot_omit_a_module_prerequisite(self) -> None:
        catalog = copy.deepcopy(self.catalog)
        track = next(item for item in catalog["tracks"] if item["id"] == "orange-today")
        track["modules"].remove("cmp-101")
        errors = self.validate(catalog)
        self.assertIn("track orange-today omits prerequisite cmp-101 for org-101", errors)


if __name__ == "__main__":
    unittest.main()
