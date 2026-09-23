"""Strict JSON parsing shared by repository validators."""
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SCHEMA_DIR = ".agents/schemas"

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
