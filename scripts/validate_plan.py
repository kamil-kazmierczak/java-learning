"""Validate the plan format and its internal links."""
from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
PLAN = "planning/system-plan.json"
SCHEMA = "schemas/system-plan.schema.json"


def unique_object(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Duplicate JSON key: {key}")
        result[key] = value
    return result


def reject_constant(value):
    raise ValueError(f"Invalid JSON number: {value}")


def finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError(f"Non-finite JSON number: {value}")
    return result


def load_json(path):
    return json.loads(
        Path(path).read_text(encoding="utf-8"),
        object_pairs_hook=unique_object,
        parse_constant=reject_constant,
        parse_float=finite_float,
    )


def pointer(parts):
    return "" if not parts else "/" + "/".join(str(p).replace("~", "~0").replace("/", "~1") for p in parts)


def issue(rule, field, message, file=PLAN):
    return {"rule_id": rule, "file": file, "json_pointer": field, "message": message}


def validate_plan(plan, schema):
    errors = []
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in validator.iter_errors(plan):
        errors.append(issue("JSON_SCHEMA", pointer(error.absolute_path), error.message))
    if errors:
        return errors

    collections = {
        "requirements": "id",
        "progress_states": "value",
        "file_layout": "path",
        "session_flow": "id",
        "acceptance_tests": "id",
        "implementation_steps": "id",
        "open_decisions": "id",
        "sources": "id",
    }
    for collection, key in collections.items():
        seen = set()
        for index, item in enumerate(plan[collection]):
            value = item[key]
            if value in seen:
                errors.append(issue("DUPLICATE_ID", pointer([collection, index, key]), value))
            seen.add(value)

    requirement_ids = {item["id"] for item in plan["requirements"]}
    for index, test in enumerate(plan["acceptance_tests"]):
        for ref_index, ref in enumerate(test["requirement_ids"]):
            if ref not in requirement_ids:
                errors.append(issue(
                    "UNKNOWN_REQUIREMENT",
                    pointer(["acceptance_tests", index, "requirement_ids", ref_index]),
                    ref,
                ))

    check_ids = [item["id"] for item in plan["validation"]["checks"]]
    if len(check_ids) != len(set(check_ids)):
        errors.append(issue("DUPLICATE_ID", "/validation/checks", "Check IDs must be unique."))

    for index, item in enumerate(plan["file_layout"]):
        for key in ("path", "schema"):
            value = item[key]
            if value is None:
                continue
            if value.startswith("/") or ".." in value.split("/") or "\\" in value:
                errors.append(issue("UNSAFE_PATH", pointer(["file_layout", index, key]), value))
        if item["path"].endswith(".json") and item["schema"] is None:
            errors.append(issue(
                "MISSING_SCHEMA", pointer(["file_layout", index, "schema"]), item["path"]
            ))
    return errors


def validate_entry_links(root):
    errors = []
    entry = root / "AGENTS.md"
    if not entry.is_file():
        return [issue("MISSING_ENTRY", "", "AGENTS.md is missing.", "AGENTS.md")]
    text = entry.read_text(encoding="utf-8")
    links = re.findall(r"\]\(([^)]+)\)", text)
    for required in (PLAN, SCHEMA):
        if required not in links:
            errors.append(issue("MISSING_LINK", "", required, "AGENTS.md"))
    for link in links:
        if "://" in link or link.startswith("#"):
            continue
        target = (root / link.split("#", 1)[0]).resolve()
        if not target.is_relative_to(root.resolve()) or not target.is_file():
            errors.append(issue("BROKEN_LINK", "", link, "AGENTS.md"))
    return errors


def main():
    errors = []
    for rel in (PLAN, SCHEMA):
        try:
            load_json(ROOT / rel)
        except (ValueError, OSError) as error:
            errors.append(issue("JSON_PARSE", "", str(error), rel))
    if not errors:
        try:
            errors.extend(validate_plan(load_json(ROOT / PLAN), load_json(ROOT / SCHEMA)))
        except Exception as error:
            errors.append(issue("VALIDATOR_ERROR", "", str(error), SCHEMA))
    errors.extend(validate_entry_links(ROOT))
    report = {
        "scope": "system_plan",
        "passed": not errors,
        "checks": ["json_parse", "json_schema", "plan_references", "entry_links"],
        "ste_compliance": "not_verified",
        "lesson_system_ready": False,
        "errors": errors,
    }
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
