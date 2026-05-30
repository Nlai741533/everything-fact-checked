#!/usr/bin/env python3
"""Validate fact-check evidence records against schemas/evidence.schema.json.

Makes the skill's "standard evidence format" mechanically enforceable: it checks
the JSON Schema constraints (required fields, types, enums, no stray fields) plus
the cross-field fact-check rules that plain JSON Schema can't express (e.g. a
"verified" verdict must cite a well-formed http/https source_url, and P0/P1
claims require a primary or secondary source_tier).

Stdlib only — implements the small subset of JSON Schema this project uses, so
there is no third-party dependency.

Usage:
  python3 validate_evidence.py evidence.json      # array or single record
  python3 validate_evidence.py --schema PATH evidence.json
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from urllib.parse import urlparse

DEFAULT_SCHEMA = os.path.join(
    os.path.dirname(__file__), "..", "schemas", "evidence.schema.json"
)

def _looks_like_url(value: str) -> bool:
    """Check that value is a plausible http/https URL with a non-empty host."""
    try:
        parsed = urlparse(value.strip())
        return parsed.scheme in {"http", "https"} and bool(parsed.netloc)
    except Exception:
        return False


_JSON_TYPES = {
    "string": str,
    "number": (int, float),
    "object": dict,
    "array": list,
    "boolean": bool,
    "null": type(None),
}


def _type_ok(value, type_spec) -> bool:
    types = type_spec if isinstance(type_spec, list) else [type_spec]
    for t in types:
        py = _JSON_TYPES[t]
        if t == "number" and isinstance(value, bool):
            continue
        if isinstance(value, py):
            return True
    return False


def validate_record(rec, schema: dict) -> list:
    """Return a list of human-readable errors for one record ([] if valid)."""
    if not isinstance(rec, dict):
        return ["<not an object>: record must be a JSON object"]

    errors = []
    cid = rec.get("claim_id", "<no id>")
    props = schema.get("properties", {})

    for field in schema.get("required", []):
        if field not in rec:
            errors.append(f"{cid}: missing required field '{field}'")

    if schema.get("additionalProperties") is False:
        for field in rec:
            if field not in props:
                errors.append(f"{cid}: unexpected field '{field}'")

    for field, value in rec.items():
        spec = props.get(field)
        if spec is None:
            continue
        if "type" in spec and not _type_ok(value, spec["type"]):
            errors.append(f"{cid}: field '{field}' has wrong type (expected {spec['type']})")
            continue
        if "enum" in spec and value not in spec["enum"]:
            allowed = ", ".join(repr(v) for v in spec["enum"])
            errors.append(f"{cid}: field '{field}'={value!r} not in [{allowed}]")
        if spec.get("pattern") and isinstance(value, str) and not re.match(spec["pattern"], value):
            errors.append(f"{cid}: field '{field}'={value!r} does not match {spec['pattern']}")
        if spec.get("minLength") and isinstance(value, str) and len(value) < spec["minLength"]:
            errors.append(f"{cid}: field '{field}' is shorter than {spec['minLength']}")

    errors.extend(_check_rules(rec, cid))
    return errors


def _check_rules(rec: dict, cid: str) -> list:
    """Cross-field fact-check rules (see schema.factCheckRules)."""
    errors = []
    verdict = rec.get("verdict")

    if verdict == "verified":
        url = rec.get("source_url")
        if not url:
            errors.append(f"{cid}: 'verified' requires a non-null source_url")
        elif not _looks_like_url(url):
            errors.append(
                f"{cid}: 'verified' source_url does not look like a URL: {url!r}"
            )
        if rec.get("priority") in ("P0", "P1") and rec.get("source_tier") not in ("primary", "secondary"):
            errors.append(
                f"{cid}: 'verified' P0/P1 claim requires source_tier 'primary' or 'secondary'"
            )
    elif verdict == "error":
        if rec.get("reported_value") in (None, "") or rec.get("source_value") in (None, ""):
            errors.append(f"{cid}: 'error' requires both reported_value and source_value")
    elif verdict == "unverifiable":
        if not (rec.get("notes") or "").strip():
            errors.append(f"{cid}: 'unverifiable' requires a non-empty 'notes' field")

    return errors


def validate_evidence(data, schema: dict) -> list:
    """Validate a single record or a list of records. Returns all errors."""
    records = data if isinstance(data, list) else [data]
    errors = []
    for rec in records:
        errors.extend(validate_record(rec, schema))
    return errors


def load_schema(path: str = DEFAULT_SCHEMA) -> dict:
    with open(path, encoding="utf-8") as fh:
        return json.load(fh)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("evidence", help="Path to evidence JSON (array or single record)")
    parser.add_argument("--schema", default=DEFAULT_SCHEMA, help="Path to the schema file")
    args = parser.parse_args(argv)

    try:
        schema = load_schema(args.schema)
        with open(args.evidence, encoding="utf-8") as fh:
            data = json.load(fh)
    except (OSError, json.JSONDecodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 2

    errors = validate_evidence(data, schema)
    n = len(data) if isinstance(data, list) else 1
    if errors:
        for err in errors:
            print(f"INVALID: {err}")
        print(f"\n{len(errors)} problem(s) across {n} record(s).")
        return 1

    print(f"OK: {n} record(s) valid.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
