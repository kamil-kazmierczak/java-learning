"""Check declared project style rules. This is not a full STE checker."""
from __future__ import annotations

import argparse
import json
import os
import re
from pathlib import Path

from validation_common import ROOT, load_json, pointer
from validate_records import route
from validate_documents import markdown_files, validate_documents

VERSION = "1.1.0"
RULES = {"STYLE-01", "STYLE-02", "STYLE-03", "STYLE-04"}
FILLER = (
    "delve into", "game changer", "game-changing", "unlock the power",
    "it is worth noting", "it's worth noting", "in today's fast-paced world",
    "seamlessly", "great job", "excellent work", "in conclusion",
    "leverage", "foster", "cutting-edge", "revolutionary",
)
CONTRACTIONS = re.compile(
    r"\b(?:[a-z]+n['’]t|(?:i|you|we|they)['’](?:m|re|ve|ll|d)|"
    r"(?:he|she|it|that|there|what|who)['’](?:s|ll|d)|let['’]s)\b", re.I)
WORDS = re.compile(r"[^\W\d_]+(?:[-'][^\W\d_]+)*", re.UNICODE)
# These are exact values, identifiers, or source text, rather than prose.
EXACT_KEYS = {
    "schema_version", "record_type", "record_kind", "status", "selection", "kind",
    "source", "help_level", "completion", "category", "mode", "origin", "scope",
    "chat", "review", "repository", "repository_language", "chat_language", "review_language",
    "assessment_mode", "topic_selection", "hint_order", "allowed_resources", "resources_used",
    "closure_command", "framework_use", "version_policy", "branch", "entry_file",
    "required_checks", "workflow_path", "standard", "checker", "exclusions", "command", "output",
    "code_paths", "ide", "jdk_distribution", "term", "allowed_forms", "avoid_forms",
}


def prose_fields(value, path=()):
    """Keep a pointer to each prose value. Data checks reject unknown fields."""
    if isinstance(value, dict):
        for key, child in value.items():
            if key in EXACT_KEYS or key.endswith(("_id", "_ids", "_url")):
                continue
            if key in {"url", "id"} or (key == "title" and "sources" in path):
                continue
            yield from prose_fields(child, path + (key,))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from prose_fields(child, path + (index,))
    elif isinstance(value, str):
        yield pointer(path), value


def plain_prose(text):
    text = re.sub(r"(?ms)^\s*(```|~~~).*?^\s*\1[^\n]*$", " ", text)
    text = re.sub(r"(?m)^\s*>.*$", " ", text)  # marked exact quotes
    text = re.sub(r"`+[^`\n]*`+", " ", text)
    text = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", text)
    return re.sub(r"https?://\S+", " ", text)


def check_text(text, terms):
    findings = []
    prose = plain_prose(text)
    for sentence in re.split(r"(?<=[.!?])\s+|\n+", prose):
        count = len(WORDS.findall(sentence))
        if count > 25:
            findings.append(("STYLE-01", f"Sentence has {count} words; the project limit is 25."))
    for phrase in FILLER:
        if re.search(r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", prose, re.I):
            findings.append(("STYLE-02", f"Remove the stock phrase: {phrase}"))
    for match in CONTRACTIONS.finditer(prose):
        findings.append(("STYLE-03", f"Write the full form of: {match[0]}"))
    for term in terms:
        for form in term["avoid_forms"]:
            # Case is significant: JAVA is not the approved Java spelling.
            if re.search(r"(?<!\w)" + re.escape(form) + r"(?!\w)", prose):
                findings.append(("STYLE-04", f"Use {term['term']} instead of {form}."))
    return findings


def validate_language(root=ROOT):
    findings = []
    def add(rule, file, location, message):
        findings.append({"check_id": "LANGUAGE", "rule_id": rule, "file": file,
                         "json_pointer": location, "severity": "error", "message": message})
    policy = load_json(root / "language/policy.json")
    terms = load_json(root / "language/technical-terms.json")["terms"]
    automatic = {r["rule_id"] for r in policy["coverage"] if r["mode"] == "automatic"}
    if automatic != RULES:
        add("COVERAGE", "language/policy.json", "/coverage", "Declared automatic rules do not match the checker.")
    checked_files = []
    for path in sorted(root.rglob("*.json")):
        relative = path.relative_to(root).as_posix()
        target = route(relative)
        if target is None or target[1] != "live":
            continue
        checked_files.append(relative)
        for location, text in prose_fields(load_json(path)):
            for rule, message in check_text(text, terms):
                add(rule, relative, location, message)
    for error in validate_documents(root):
        add(error['rule_id'], error['file'], '', error['message'])
    for path in markdown_files(root):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink() or not path.resolve().is_relative_to(root.resolve()):
            continue
        checked_files.append(relative)
        for rule, message in check_text(path.read_text(encoding="utf-8"), terms):
            add(rule, relative, "", message)
    return {
        "commit_sha": os.getenv("GITHUB_SHA"), "check_id": "LANGUAGE",
        "checker": f"project-style {VERSION}", "passed": not findings,
        "coverage": policy["coverage"], "checked_files": checked_files,
        "ste_compliance": "not_verified", "manual_review": "required",
        "extraction_limits": "Code spans, code fences, marked quotes, URLs, and exact fields are excluded. Review their use manually.",
        "errors": findings,
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=ROOT)
    args = parser.parse_args()
    try:
        report = validate_language(args.root)
    except (OSError, ValueError, KeyError, TypeError) as error:
        report = {"commit_sha": os.getenv("GITHUB_SHA"), "check_id": "LANGUAGE",
                  "passed": False, "ste_compliance": "not_verified", "error": str(error)}
    print(json.dumps(report, indent=2, ensure_ascii=False))
    return 0 if report["passed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
