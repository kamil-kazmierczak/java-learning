"""Test record contracts with isolated learner fixtures."""
import copy
import json
import re
import shutil
import tempfile
import unittest
from pathlib import Path

from validate_plan import ROOT, load_json
from validate_records import RECORD_TYPES, SINGLETONS, validate_repository


class RecordValidationTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix="java-record-tests-", dir=ROOT.parent)
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / "repo"
        shutil.copytree(ROOT, self.root, ignore=shutil.ignore_patterns(".git", "__pycache__"))
        # Keep tests independent of future real lessons and assessment results.
        for directory in ("topics", "lessons", "exercises"):
            shutil.rmtree(self.root / directory, ignore_errors=True)
        curriculum = self.read("curriculum.json")
        curriculum["topics"] = []
        self.write("curriculum.json", curriculum)
        state = self.read("state/current.json")
        state.update(last_lesson_id=None, current_topic_id=None, resume_note=None,
                     pending_tasks=[], proposed_topics=[], review_queue=[])
        self.write("state/current.json", state)
        entry = self.root / "AGENTS.md"
        text = re.sub(r"\[[^\]]*\]\(lessons/[^)]+\)", "", entry.read_text())
        entry.write_text(text)

    def read(self, path):
        return load_json(self.root / path)

    def write(self, path, data):
        target = self.root / path
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")

    def errors(self):
        return validate_repository(self.root)[0]

    def assert_rule(self, rule):
        errors = self.errors()
        self.assertIn(rule, {e["rule_id"] for e in errors}, errors)

    def make_live_fixture(self):
        routes = {record_type: path for path, record_type in SINGLETONS.items()}
        routes.update({"topic": "topics/counter-state.json", "lesson": "lessons/lesson-0001.json",
                       "exercise": "exercises/exercise-counter/exercise.json"})
        for record_type, path in routes.items():
            record = self.read(f"examples/{record_type}.json")
            record["record_kind"] = "live"
            self.write(path, record)
        entry = self.root / "AGENTS.md"
        entry.write_text(entry.read_text() + "\n[Lesson 0001](lessons/lesson-0001.json)\n")

    def make_independent_fixture(self):
        self.make_live_fixture()
        path = "lessons/lesson-0001.json"
        lesson = self.read(path)
        lesson["tasks"][0]["completion"] = "complete"
        lesson["tasks"][0]["resources_used"] = ["ide", "tests"]
        lesson["observations"][0].update(kind="independent_attempt", help_level="none",
                                          explained_mechanism=True, solved_new_variant=True)
        lesson["assessments"][0]["status"] = "applied_independently"
        lesson["unfinished_tasks"] = []
        self.write(path, lesson)
        topic = self.read("topics/counter-state.json")
        topic["status"] = "applied_independently"
        self.write("topics/counter-state.json", topic)
        state = self.read("state/current.json")
        state["pending_tasks"] = []
        state["resume_note"] = None
        self.write("state/current.json", state)

    def make_retained_fixture(self):
        self.make_independent_fixture()
        lesson = self.read("lessons/lesson-0001.json")
        lesson.update(lesson_id="lesson-0002", date="2026-01-20", kind="review")
        lesson["approval"]["approved_on"] = "2026-01-20"
        lesson["observations"][0].update(kind="delayed_check", previous_evidence_ref={
            "lesson_id": "lesson-0001", "evidence_id": "evidence-01"})
        lesson["assessments"][0]["status"] = "retained"
        self.write("lessons/lesson-0002.json", lesson)
        topic = self.read("topics/counter-state.json")
        topic.update(status="retained", updated_from_lesson_id="lesson-0002")
        topic["evidence_refs"].append({"lesson_id": "lesson-0002", "evidence_id": "evidence-01"})
        topic["review"]["last_review_lesson_id"] = "lesson-0002"
        self.write("topics/counter-state.json", topic)
        state = self.read("state/current.json")
        state["last_lesson_id"] = "lesson-0002"
        self.write("state/current.json", state)
        entry = self.root / "AGENTS.md"
        entry.write_text(entry.read_text() + "\n[Lesson 0002](lessons/lesson-0002.json)\n")

    def test_empty_fixture_has_no_invented_lesson_history(self):
        errors, configured = validate_repository(self.root)
        self.assertEqual(errors, [])
        self.assertTrue(configured)
        self.assertIsNone(self.read("state/current.json")["last_lesson_id"])
        self.assertEqual(self.read("curriculum.json")["topics"], [])
        self.assertEqual(list((self.root / "lessons").glob("*.json")), [])

    def test_each_record_type_rejects_missing_extra_and_changed_version(self):
        for record_type in sorted(RECORD_TYPES):
            path = f"examples/{record_type}.json"
            original = self.read(path)
            for mutation in ("missing", "extra", "version"):
                with self.subTest(record_type=record_type, mutation=mutation):
                    changed = copy.deepcopy(original)
                    if mutation == "missing":
                        del changed["schema_version"]
                    elif mutation == "extra":
                        changed["invented_field"] = "value"
                    else:
                        changed["schema_version"] = "2.0.0"
                    self.write(path, changed)
                    self.assert_rule("JSON_SCHEMA")
                    self.write(path, original)

    def test_nested_fields_are_closed(self):
        lesson = self.read("examples/lesson.json")
        lesson["observations"][0]["invented_score"] = 100
        self.write("examples/lesson.json", lesson)
        self.assert_rule("JSON_SCHEMA")

    def test_reject_invalid_dates(self):
        lesson = self.read("examples/lesson.json")
        lesson["date"] = "2026-02-30"
        self.write("examples/lesson.json", lesson)
        self.assert_rule("JSON_SCHEMA")

    def test_reject_duplicate_keys_and_non_finite_numbers(self):
        path = self.root / "examples/profile.json"
        for content in ('{"record_type":"profile","record_type":"topic"}', '{"value":NaN}', '{"value":1e999}'):
            with self.subTest(content=content):
                path.write_text(content)
                self.assert_rule("JSON_PARSE")

    def test_schema_refs_do_not_fetch_external_resources(self):
        schema = self.read("schemas/topic.schema.json")
        schema["properties"]["status"] = {"$ref": "https://invalid.example/schema.json"}
        self.write("schemas/topic.schema.json", schema)
        self.assert_rule("SCHEMA_REFERENCE")

    def test_unknown_json_route(self):
        self.write("state/other.json", {})
        self.assert_rule("NO_VALIDATION_ROUTE")

    def test_valid_live_fixture(self):
        self.make_live_fixture()
        errors, configured = validate_repository(self.root)
        self.assertEqual(errors, [])
        self.assertTrue(configured)

    def test_empty_initial_state_is_valid(self):
        self.make_live_fixture()
        for directory in ("topics", "lessons", "exercises"):
            shutil.rmtree(self.root / directory)
        curriculum = self.read("curriculum.json")
        curriculum["topics"] = []
        self.write("curriculum.json", curriculum)
        state = self.read("state/current.json")
        state.update(last_lesson_id=None, current_topic_id=None, resume_note=None,
                     pending_tasks=[], proposed_topics=[], review_queue=[])
        self.write("state/current.json", state)
        entry = self.root / "AGENTS.md"
        entry.write_text(entry.read_text().replace("[Lesson 0001](lessons/lesson-0001.json)", ""))
        self.assertEqual(self.errors(), [])

    def test_example_cannot_be_copied_into_live_state(self):
        self.write("profile.json", self.read("examples/profile.json"))
        self.assert_rule("RECORD_KIND")

    def test_file_name_must_match_id(self):
        self.make_live_fixture()
        lesson = self.read("lessons/lesson-0001.json")
        lesson["lesson_id"] = "lesson-0099"
        self.write("lessons/lesson-0001.json", lesson)
        self.assert_rule("FILE_ID")

    def test_duplicate_task_id(self):
        lesson = self.read("examples/lesson.json")
        lesson["tasks"].append(copy.deepcopy(lesson["tasks"][0]))
        self.write("examples/lesson.json", lesson)
        self.assert_rule("DUPLICATE_ID")

    def test_missing_topic(self):
        (self.root / "examples/topic.json").unlink()
        self.assert_rule("MISSING_EXAMPLE")

    def test_unknown_exercise(self):
        lesson = self.read("examples/lesson.json")
        lesson["tasks"][0]["exercise_id"] = "exercise-missing"
        self.write("examples/lesson.json", lesson)
        self.assert_rule("UNKNOWN_EXERCISE")

    def test_unknown_evidence(self):
        topic = self.read("examples/topic.json")
        topic["evidence_refs"][0]["evidence_id"] = "evidence-99"
        self.write("examples/topic.json", topic)
        self.assert_rule("UNKNOWN_EVIDENCE")

    def test_prerequisite_cycle(self):
        curriculum = self.read("examples/curriculum.json")
        curriculum["topics"][0]["prerequisite_ids"] = ["counter-state"]
        self.write("examples/curriculum.json", curriculum)
        self.assert_rule("PREREQUISITE_CYCLE")

    def test_hint_result_does_not_prove_independent_skill(self):
        topic = self.read("examples/topic.json")
        topic["status"] = "applied_independently"
        self.write("examples/topic.json", topic)
        self.assert_rule("INDEPENDENT_EVIDENCE")

    def test_independent_task_cannot_use_hint_resource(self):
        self.make_independent_fixture()
        lesson = self.read("lessons/lesson-0001.json")
        lesson["tasks"][0]["resources_used"].append("llm_hints")
        self.write("lessons/lesson-0001.json", lesson)
        self.assert_rule("SUPPORTED_ATTEMPT")

    def test_retained_state_needs_later_evidence(self):
        self.make_independent_fixture()
        topic = self.read("topics/counter-state.json")
        topic["status"] = "retained"
        self.write("topics/counter-state.json", topic)
        self.assert_rule("DELAYED_EVIDENCE")

    def test_valid_retained_state(self):
        self.make_retained_fixture()
        self.assertEqual(self.errors(), [])

    def test_delayed_check_cannot_use_same_day(self):
        self.make_retained_fixture()
        lesson = self.read("lessons/lesson-0002.json")
        lesson["date"] = "2026-01-10"
        self.write("lessons/lesson-0002.json", lesson)
        self.assert_rule("REVIEW_DATE")

    def test_delayed_check_needs_independent_baseline(self):
        self.make_retained_fixture()
        lesson = self.read("lessons/lesson-0001.json")
        lesson["observations"][0]["explained_mechanism"] = False
        self.write("lessons/lesson-0001.json", lesson)
        self.assert_rule("REVIEW_BASELINE")

    def test_stale_current_state(self):
        self.make_live_fixture()
        state = self.read("state/current.json")
        state["last_lesson_id"] = None
        self.write("state/current.json", state)
        self.assert_rule("STALE_CURRENT_STATE")

    def test_stale_topic_state(self):
        self.make_retained_fixture()
        topic = self.read("topics/counter-state.json")
        topic["updated_from_lesson_id"] = "lesson-0001"
        self.write("topics/counter-state.json", topic)
        self.assert_rule("STALE_TOPIC_STATE")

    def test_missing_lesson_index_link(self):
        self.make_live_fixture()
        entry = self.root / "AGENTS.md"
        entry.write_text(entry.read_text().replace("[Lesson 0001](lessons/lesson-0001.json)", ""))
        self.assert_rule("LESSON_INDEX")

    def test_unapproved_lesson(self):
        lesson = self.read("examples/lesson.json")
        lesson["approval"]["status"] = "pending"
        self.write("examples/lesson.json", lesson)
        self.assert_rule("JSON_SCHEMA")

    def test_executed_result_needs_output_and_source(self):
        lesson = self.read("examples/lesson.json")
        lesson["tasks"][0]["execution"]["status"] = "passed"
        self.write("examples/lesson.json", lesson)
        self.assert_rule("JSON_SCHEMA")

    def test_code_path_cannot_escape_the_exercise(self):
        exercise = self.read("examples/exercise.json")
        exercise["code_paths"] = ["../secret.java"]
        self.write("examples/exercise.json", exercise)
        self.assert_rule("JSON_SCHEMA")

    def test_live_references_cannot_use_examples(self):
        self.make_live_fixture()
        (self.root / "lessons/lesson-0001.json").unlink()
        entry = self.root / "AGENTS.md"
        entry.write_text(entry.read_text().replace("[Lesson 0001](lessons/lesson-0001.json)", ""))
        self.assert_rule("UNKNOWN_EVIDENCE")

    def test_language_automation_needs_a_tool(self):
        policy = self.read("examples/language-policy.json")
        policy["coverage"][0]["mode"] = "automatic"
        self.write("examples/language-policy.json", policy)
        self.assert_rule("MISSING_LANGUAGE_CHECKER")


if __name__ == "__main__":
    unittest.main()
