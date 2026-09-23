"""Validate record formats and links. This tool does not certify STE compliance."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker
from referencing import Registry, Resource

from validate_plan import PLAN, SCHEMA, SCHEMA_DIR, ROOT, load_json, pointer, validate_plan, validate_entry_links

SINGLETONS = {
    "profile.json": "profile",
    "teaching.json": "teaching",
    "curriculum.json": "curriculum",
    "state/current.json": "current-state",
    "language/policy.json": "language-policy",
    "language/technical-terms.json": "technical-terms",
    "project-instructions.json": "project-instructions",
}
RECORD_TYPES = set(SINGLETONS.values()) | {"topic", "lesson", "exercise"}
SCHEMA_NAMES = RECORD_TYPES | {"common", "system-plan"}
EXAMPLES_DIR = ".agents/examples"
# Schema IDs are stable identifiers, independent of their local directory.
BASE = "https://github.com/kamil-kazmierczak/java-learning/schemas/"
PATTERNS = (
    (r"topics/([a-z][a-z0-9]*(?:-[a-z0-9]+)*)\.json", "topic", "topic_id"),
    (r"lessons/(lesson-[0-9]{4,})\.json", "lesson", "lesson_id"),
    (r"exercises/(exercise-[a-z0-9]+(?:-[a-z0-9]+)*)/exercise\.json", "exercise", "exercise_id"),
)


def route(path):
    if path in SINGLETONS:
        return SINGLETONS[path], "live", None, None
    match = re.fullmatch(re.escape(EXAMPLES_DIR) + r"/([a-z-]+)\.json", path)
    if match and match[1] in RECORD_TYPES:
        return match[1], "example", None, None
    for pattern, record_type, id_field in PATTERNS:
        match = re.fullmatch(pattern, path)
        if match:
            return record_type, "live", id_field, match[1]
    return None


def add(errors, rule, file, field, message, check="LINKS"):
    errors.append({"check_id": check, "severity": "error", "rule_id": rule,
                   "file": file, "json_pointer": field, "message": message})


def unique_index(items, field, file, location, errors):
    result = {}
    for index, item in enumerate(items):
        value = item[field]
        if value in result:
            add(errors, "DUPLICATE_ID", file, f"{location}/{index}/{field}", value)
        else:
            result[value] = item
    return result


def walk_refs(value):
    if isinstance(value, dict):
        if "$ref" in value:
            yield value["$ref"]
        for child in value.values():
            yield from walk_refs(child)
    elif isinstance(value, list):
        for child in value:
            yield from walk_refs(child)


def schema_registry(schemas, errors):
    registry = Registry().with_resources(
        (s["$id"], Resource.from_contents(s)) for s in schemas.values()
    )
    for name, schema in schemas.items():
        for ref in walk_refs(schema):
            try:
                registry.resolver(schema["$id"]).lookup(ref)
            except Exception as error:
                add(errors, "SCHEMA_REFERENCE", f"{SCHEMA_DIR}/{name}.schema.json", "",
                    str(error), "DATA")
    return registry


def validate_group(records, root, errors, kind):
    """Keep fictional examples and learner data in separate reference graphs."""
    by_type = {}
    for path, record in records.items():
        by_type.setdefault(record["record_type"], []).append((path, record))
    if not records:
        return
    for required in SINGLETONS.values():
        if len(by_type.get(required, [])) != 1:
            add(errors, "MISSING_SINGLETON", "AGENTS.md", "", f"{kind}: {required}")
    if any(len(by_type.get(t, [])) != 1 for t in SINGLETONS.values()):
        return

    def singleton(t):
        return by_type[t][0]

    def collection(t, field):
        result = {}
        for path, record in by_type.get(t, []):
            identifier = record[field]
            if identifier in result:
                add(errors, "DUPLICATE_ID", path, "/" + field, identifier)
            else:
                result[identifier] = (path, record)
        return result

    topics = collection("topic", "topic_id")
    lessons = collection("lesson", "lesson_id")
    exercises = collection("exercise", "exercise_id")
    curriculum_path, curriculum = singleton("curriculum")
    topic_map = unique_index(curriculum["topics"], "topic_id", curriculum_path, "/topics", errors)
    for identifier in topic_map.keys() - topics.keys():
        add(errors, "MISSING_TOPIC", curriculum_path, "/topics", identifier)
    for identifier in topics.keys() - topic_map.keys():
        add(errors, "UNKNOWN_TOPIC", topics[identifier][0], "/topic_id", identifier)
    for index, item in enumerate(curriculum["topics"]):
        for prerequisite in item["prerequisite_ids"]:
            if prerequisite not in topic_map:
                add(errors, "UNKNOWN_PREREQUISITE", curriculum_path,
                    f"/topics/{index}/prerequisite_ids", prerequisite)
        if item["topic_id"] in topics:
            path, topic = topics[item["topic_id"]]
            if topic["selection"] != item["selection"] or topic["title"] != item["title"]:
                add(errors, "TOPIC_MAP_MISMATCH", path, "", item["topic_id"])
    visited, active = set(), set()

    def visit(identifier):
        if identifier in active:
            add(errors, "PREREQUISITE_CYCLE", curriculum_path, "/topics", identifier)
            return
        if identifier in visited or identifier not in topic_map:
            return
        active.add(identifier)
        for dependency in topic_map[identifier]["prerequisite_ids"]:
            visit(dependency)
        active.remove(identifier)
        visited.add(identifier)

    for identifier in topic_map:
        visit(identifier)

    def check_topics(ids, file, field):
        for identifier in ids:
            if identifier not in topics:
                add(errors, "UNKNOWN_TOPIC", file, field, identifier)

    evidence = {}
    tasks_by_lesson = {}
    assessments_by_lesson = {}
    for lesson_id, (path, lesson) in lessons.items():
        check_topics(lesson["topic_ids"], path, "/topic_ids")
        tasks = unique_index(lesson["tasks"], "task_id", path, "/tasks", errors)
        tasks_by_lesson[lesson_id] = tasks
        observations = unique_index(lesson["observations"], "evidence_id", path, "/observations", errors)
        assessments_by_lesson[lesson_id] = unique_index(
            lesson["assessments"], "topic_id", path, "/assessments", errors
        )
        for evidence_id, observation in observations.items():
            evidence[(lesson_id, evidence_id)] = observation
        if lesson["approval"]["approved_on"] < lesson["date"]:
            add(errors, "APPROVAL_DATE", path, "/approval/approved_on", "Approval precedes the lesson.")
        unique_index(lesson["sources"], "id", path, "/sources", errors)
        for index, task in enumerate(lesson["tasks"]):
            if not set(task["topic_ids"]).issubset(lesson["topic_ids"]):
                add(errors, "TASK_TOPIC", path, f"/tasks/{index}/topic_ids", "Task topics must be lesson topics.")
            exercise_id = task["exercise_id"]
            if exercise_id is not None:
                if exercise_id not in exercises:
                    add(errors, "UNKNOWN_EXERCISE", path, f"/tasks/{index}/exercise_id", exercise_id)
                elif not set(task["topic_ids"]).issubset(exercises[exercise_id][1]["topic_ids"]):
                    add(errors, "EXERCISE_TOPIC", path, f"/tasks/{index}/topic_ids", exercise_id)
        expected_unfinished = {t["task_id"] for t in lesson["tasks"] if t["completion"] == "unfinished"}
        actual_unfinished = unique_index(lesson["unfinished_tasks"], "task_id", path, "/unfinished_tasks", errors)
        if expected_unfinished != actual_unfinished.keys():
            add(errors, "UNFINISHED_TASKS", path, "/unfinished_tasks", "List each unfinished task once.")
        for index, error in enumerate(lesson["errors"]):
            if error["task_id"] not in tasks:
                add(errors, "UNKNOWN_TASK", path, f"/errors/{index}/task_id", error["task_id"])
        check_topics(lesson["next_step"]["topic_ids"], path, "/next_step/topic_ids")

    def resolve(ref, topic_id, file, field):
        observation = evidence.get((ref["lesson_id"], ref["evidence_id"]))
        if observation is None:
            add(errors, "UNKNOWN_EVIDENCE", file, field, f"{ref['lesson_id']}#{ref['evidence_id']}")
        elif observation["topic_id"] != topic_id:
            add(errors, "EVIDENCE_TOPIC", file, field, "Evidence belongs to another topic.")
            return None
        return observation

    def independent(observation):
        return (observation["kind"] in ("independent_attempt", "delayed_check")
                and observation["help_level"] == "none"
                and observation["explained_mechanism"] and observation["solved_new_variant"])

    def check_status(status, refs, topic_id, file, field):
        observations = [resolve(ref, topic_id, file, field) for ref in refs]
        observations = [item for item in observations if item is not None]
        if status != "not_assessed" and not observations:
            add(errors, "MISSING_EVIDENCE", file, field, "Assessed states need evidence.")
        if status in ("applied_independently", "retained") and not any(map(independent, observations)):
            add(errors, "INDEPENDENT_EVIDENCE", file, field, "An independent result and explanation are required.")
        if status == "retained" and not any(o["kind"] == "delayed_check" and independent(o) for o in observations):
            add(errors, "DELAYED_EVIDENCE", file, field, "A delayed independent result is required.")

    for lesson_id, (path, lesson) in lessons.items():
        tasks = tasks_by_lesson[lesson_id]
        for index, observation in enumerate(lesson["observations"]):
            location = f"/observations/{index}"
            task = tasks.get(observation["task_id"])
            if task is None:
                add(errors, "UNKNOWN_TASK", path, location + "/task_id", observation["task_id"])
            else:
                if observation["topic_id"] not in task["topic_ids"]:
                    add(errors, "EVIDENCE_TOPIC", path, location + "/topic_id", "Evidence must refer to a task topic.")
                if observation["help_level"] != "none" and "llm_hints" not in task["resources_used"]:
                    add(errors, "UNRECORDED_HINT", path, location, "Record the hint resource.")
                if observation["kind"] in ("independent_attempt", "delayed_check"):
                    if "llm_hints" in task["resources_used"] or task["completion"] != "complete":
                        add(errors, "SUPPORTED_ATTEMPT", path, location, "An independent task must be complete and use no LLM hints.")
                if observation["source"] == "agent_execution" and task["execution"]["source"] != "agent_execution":
                    add(errors, "EXECUTION_SOURCE", path, location + "/source", "No agent execution result exists for this task.")
            previous = observation["previous_evidence_ref"]
            if previous is not None:
                earlier = resolve(previous, observation["topic_id"], path, location + "/previous_evidence_ref")
                earlier_lesson = lessons.get(previous["lesson_id"])
                if earlier_lesson and earlier_lesson[1]["date"] >= lesson["date"]:
                    add(errors, "REVIEW_DATE", path, location, "The earlier result must have an earlier calendar date.")
                if earlier and not independent(earlier):
                    add(errors, "REVIEW_BASELINE", path, location, "The earlier result must be independent.")
        for index, assessment in enumerate(lesson["assessments"]):
            if assessment["topic_id"] not in lesson["topic_ids"]:
                add(errors, "ASSESSMENT_TOPIC", path, f"/assessments/{index}/topic_id", assessment["topic_id"])
            refs = [{"lesson_id": lesson_id, "evidence_id": item} for item in assessment["evidence_ids"]]
            check_status(assessment["status"], refs, assessment["topic_id"], path, f"/assessments/{index}")

    for topic_id, (path, topic) in topics.items():
        check_status(topic["status"], topic["evidence_refs"], topic_id, path, "/evidence_refs")
        lesson_id = topic["updated_from_lesson_id"]
        if lesson_id is None:
            if topic["status"] != "not_assessed" or topic["evidence_refs"] or topic["gaps"]:
                add(errors, "UNSOURCED_TOPIC_STATE", path, "/updated_from_lesson_id", "This topic state needs an assessment lesson.")
        else:
            assessment = assessments_by_lesson.get(lesson_id, {}).get(topic_id)
            if assessment is None:
                add(errors, "MISSING_ASSESSMENT", path, "/updated_from_lesson_id", lesson_id)
            elif assessment["status"] != topic["status"]:
                add(errors, "STATUS_MISMATCH", path, "/status", "The topic and its assessment have different states.")
            elif any({"lesson_id": lesson_id, "evidence_id": eid} not in topic["evidence_refs"] for eid in assessment["evidence_ids"]):
                add(errors, "STATE_EVIDENCE", path, "/evidence_refs", "Include all evidence from the source assessment.")
        topic_assessments = [lid for lid, values in assessments_by_lesson.items() if topic_id in values]
        if topic_assessments:
            latest = max(topic_assessments, key=lambda lid: int(lid.split("-")[1]))
            if lesson_id != latest:
                add(errors, "STALE_TOPIC_STATE", path, "/updated_from_lesson_id", latest)
        review_id = topic["review"]["last_review_lesson_id"]
        if review_id is not None:
            review_lesson = lessons.get(review_id)
            if not review_lesson or not any(o["topic_id"] == topic_id and o["kind"] == "delayed_check" for o in review_lesson[1]["observations"]):
                add(errors, "MISSING_REVIEW", path, "/review/last_review_lesson_id", review_id)

    for exercise_id, (path, exercise) in exercises.items():
        check_topics(exercise["topic_ids"], path, "/topic_ids")
        unique_index(exercise["sources"], "id", path, "/sources", errors)
        prefix = f"{EXAMPLES_DIR}/code/" if kind == "example" else f"exercises/{exercise_id}/"
        for index, code_path in enumerate(exercise["code_paths"]):
            target = root / code_path
            if not code_path.startswith(prefix) or not target.is_file() or not target.resolve().is_relative_to(root.resolve()):
                add(errors, "CODE_PATH", path, f"/code_paths/{index}", code_path)

    state_path, state = singleton("current-state")
    lesson_order = sorted(lessons, key=lambda lid: int(lid.split("-")[1]))
    if len({int(lid.split("-")[1]) for lid in lessons}) != len(lessons):
        add(errors, "DUPLICATE_LESSON_NUMBER", state_path, "/last_lesson_id", "Lesson sequence numbers must be unique.")
    latest = lesson_order[-1] if lesson_order else None
    if state["last_lesson_id"] != latest:
        add(errors, "STALE_CURRENT_STATE", state_path, "/last_lesson_id", str(latest))
    for earlier, later in zip(lesson_order, lesson_order[1:]):
        if lessons[earlier][1]["date"] > lessons[later][1]["date"]:
            add(errors, "LESSON_DATE_ORDER", lessons[later][0], "/date", "Lesson dates must follow the lesson sequence.")
    if state["current_topic_id"] is not None:
        check_topics([state["current_topic_id"]], state_path, "/current_topic_id")
        topic = topics.get(state["current_topic_id"])
        if topic and topic[1]["selection"] != "accepted":
            add(errors, "UNAPPROVED_CURRENT_TOPIC", state_path, "/current_topic_id", state["current_topic_id"])
    unique_index(state["proposed_topics"], "topic_id", state_path, "/proposed_topics", errors)
    check_topics([p["topic_id"] for p in state["proposed_topics"]], state_path, "/proposed_topics")
    pending = set()
    for index, task in enumerate(state["pending_tasks"]):
        key = (task["lesson_id"], task["task_id"])
        source = tasks_by_lesson.get(key[0], {}).get(key[1])
        if key in pending or source is None or source["completion"] != "unfinished":
            add(errors, "PENDING_TASK", state_path, f"/pending_tasks/{index}", str(key))
        pending.add(key)
    if latest is not None:
        required = {(latest, t["task_id"]) for t in lessons[latest][1]["unfinished_tasks"]}
        if not required.issubset(pending):
            add(errors, "MISSING_PENDING_TASK", state_path, "/pending_tasks", "Carry unfinished work from the last lesson.")
    unique_index(state["review_queue"], "topic_id", state_path, "/review_queue", errors)
    for index, review in enumerate(state["review_queue"]):
        check_topics([review["topic_id"]], state_path, f"/review_queue/{index}/topic_id")
        for ref in review["evidence_refs"]:
            resolve(ref, review["topic_id"], state_path, f"/review_queue/{index}/evidence_refs")
        topic = topics.get(review["topic_id"])
        if topic and topic[1]["review"]["next_due_on"] != review["due_on"]:
            add(errors, "REVIEW_DATE_MISMATCH", state_path, f"/review_queue/{index}/due_on", "The topic and queue dates must match.")
    queued = {r["topic_id"] for r in state["review_queue"]}
    for topic_id, (path, topic) in topics.items():
        if topic["review"]["next_due_on"] is not None and topic_id not in queued:
            add(errors, "MISSING_REVIEW_QUEUE", path, "/review/next_due_on", topic_id)

    policy_path, policy = singleton("language-policy")
    unique_index(policy["editorial_rules"], "rule_id", policy_path, "/editorial_rules", errors)
    keys = [(item["origin"], item["rule_id"]) for item in policy["coverage"]]
    if len(keys) != len(set(keys)):
        add(errors, "DUPLICATE_RULE", policy_path, "/coverage", "Coverage rule IDs must be unique per origin.")
    if policy["checker"] is None and any(c["mode"] == "automatic" for c in policy["coverage"]):
        add(errors, "MISSING_LANGUAGE_CHECKER", policy_path, "/checker", "Automatic language checks need a named tool.")
    terms_path, terms = singleton("technical-terms")
    unique_index(terms["terms"], "term", terms_path, "/terms", errors)
    for index, term in enumerate(terms["terms"]):
        if term["term"] not in term["allowed_forms"] or set(term["allowed_forms"]) & set(term["avoid_forms"]):
            add(errors, "TERM_FORMS", terms_path, f"/terms/{index}", "Term forms are inconsistent.")

    if kind == "live":
        entry = (root / "AGENTS.md").read_text(encoding="utf-8")
        links = re.findall(r"\]\((lessons/[^)#]+\.json)\)", entry)
        expected = {path for path, _ in lessons.values()}
        if set(links) != expected or len(links) != len(set(links)):
            add(errors, "LESSON_INDEX", "AGENTS.md", "", "Link each live lesson exactly once.")


def validate_repository(root):
    root = Path(root).resolve()
    errors, data, schemas = [], {}, {}
    for path in sorted(root.rglob("*.json")):
        rel = path.relative_to(root).as_posix()
        if any(part in {".git", ".venv", "__pycache__"} for part in path.relative_to(root).parts):
            continue
        if path.is_symlink() or not path.resolve().is_relative_to(root):
            add(errors, "UNSAFE_FILE", rel, "", "Do not use linked JSON files.", "DATA")
            continue
        try:
            data[rel] = load_json(path)
        except (ValueError, OSError) as error:
            add(errors, "JSON_PARSE", rel, "", str(error), "DATA")
    for name in sorted(SCHEMA_NAMES):
        path = f"{SCHEMA_DIR}/{name}.schema.json"
        schema = data.get(path)
        if schema is None:
            add(errors, "MISSING_SCHEMA", path, "", name, "DATA")
            continue
        try:
            Draft202012Validator.check_schema(schema)
            if schema.get("$id") != BASE + name + ".schema.json":
                raise ValueError("The schema ID must match the registered record type.")
            if schema.get("$schema") != "https://json-schema.org/draft/2020-12/schema":
                raise ValueError("Use the agreed JSON Schema dialect.")
            schemas[name] = schema
        except Exception as error:
            add(errors, "INVALID_SCHEMA", path, "", str(error), "DATA")
    if errors:
        return errors, False
    registry = schema_registry(schemas, errors)
    if errors:
        return errors, False
    groups = {"live": {}, "example": {}}
    for path, value in data.items():
        if path in {f"{SCHEMA_DIR}/{name}.schema.json" for name in SCHEMA_NAMES}:
            continue
        if path == PLAN:
            for err in validate_plan(value, schemas["system-plan"]):
                add(errors, err["rule_id"], err["file"], err["json_pointer"], err["message"], "DATA")
            continue
        matched = route(path)
        if matched is None:
            add(errors, "NO_VALIDATION_ROUTE", path, "", "No schema is assigned to this path.", "DATA")
            continue
        record_type, kind, id_field, expected_id = matched
        validator = Draft202012Validator(schemas[record_type], registry=registry, format_checker=FormatChecker())
        record_errors = list(validator.iter_errors(value))
        for error in record_errors:
            add(errors, "JSON_SCHEMA", path, pointer(error.absolute_path), error.message, "DATA")
        if record_errors:
            continue
        if value["record_kind"] != kind:
            add(errors, "RECORD_KIND", path, "/record_kind", "Examples and learner records must stay separate.", "DATA")
        if id_field and value[id_field] != expected_id:
            add(errors, "FILE_ID", path, "/" + id_field, "The ID must match the file path.", "DATA")
        groups[kind][path] = value
    if PLAN not in data:
        add(errors, "MISSING_PLAN", PLAN, "", "The plan is required.", "DATA")
    for record_type in sorted(RECORD_TYPES):
        if f"{EXAMPLES_DIR}/{record_type}.json" not in data:
            add(errors, "MISSING_EXAMPLE", f"{EXAMPLES_DIR}/{record_type}.json", "", record_type, "DATA")
    for err in validate_entry_links(root):
        add(errors, err["rule_id"], err["file"], err["json_pointer"], err["message"])
    if not errors:
        for kind, records in groups.items():
            validate_group(records, root, errors, kind)
    configured = all(path in groups["live"] for path in SINGLETONS)
    return errors, configured


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        errors, configured = validate_repository(args.root)
    except Exception as error:
        errors, configured = [], False
        add(errors, "VALIDATOR_ERROR", "", "", str(error), "DATA")
    report = {
        "commit_sha": os.environ.get("GITHUB_SHA"),
        "scope": "record_contracts",
        "passed": not errors,
        "data_configuration_present": configured,
        "coverage": ["strict_json", "json_schema_2020_12", "record_links", "progress_evidence", "lesson_index"],
        "ste_compliance": "not_verified",
        "semantic_truth": "requires_human_review",
        "errors": errors,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
