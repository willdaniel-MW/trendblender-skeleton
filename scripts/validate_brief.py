#!/usr/bin/env python3
"""
Deterministic structural validation for morning_brief.js against
schema/morning-brief.schema.json's constraints. Exactly four bullets,
fixed kind values, fixed order.

Usage:
    python3 validate_brief.py path/to/morning_brief.js
"""
import json
import re
import sys

REQUIRED_KIND_ORDER = ["strongest_signal", "earned_media", "creator_opportunity", "time_sensitive"]


def extract_brief(js_text):
    m = re.search(r"(?:const\s+MORNING_BRIEF\s*=|window\.MORNING_BRIEF\s*=)\s*(\{.*?\});", js_text, re.S)
    if not m:
        return None
    return json.loads(m.group(1))


def validate(obj):
    errors = []
    for key in ["generated_at", "date", "generated_for", "bullets"]:
        if key not in obj:
            errors.append(f"missing top-level key: {key}")

    if not obj.get("generated_for"):
        errors.append("generated_for must be a non-empty array of brandKeys")

    bullets = obj.get("bullets", [])
    if len(bullets) != 4:
        errors.append(f"bullets must have exactly 4 entries, got {len(bullets)}")

    kinds = [b.get("kind") for b in bullets]
    if kinds != REQUIRED_KIND_ORDER:
        errors.append(f"bullets[].kind must appear in this exact order: {REQUIRED_KIND_ORDER}, got {kinds}")

    for i, b in enumerate(bullets):
        for key in ["kind", "label", "title", "body"]:
            if not b.get(key):
                errors.append(f"bullets[{i}].{key} is required")

    return errors


def main():
    if len(sys.argv) != 2:
        print("usage: validate_brief.py path/to/morning_brief.js", file=sys.stderr)
        sys.exit(2)
    path = sys.argv[1]
    with open(path) as f:
        js_text = f.read()

    obj = extract_brief(js_text)
    if obj is None:
        print(f"✗ {path} — no MORNING_BRIEF assignment found")
        sys.exit(1)

    errors = validate(obj)
    if errors:
        print(f"✗ {path} — {len(errors)} error(s):")
        for e in errors:
            print(f"    - {e}")
        sys.exit(1)

    print(f"✓ {path} — valid brief for {obj.get('generated_for')}")


if __name__ == "__main__":
    main()
