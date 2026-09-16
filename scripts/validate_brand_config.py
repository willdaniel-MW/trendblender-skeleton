#!/usr/bin/env python3
"""
Deterministic structural validation for brand-config.json against
schema/brand-config.schema.json's constraints.

No external dependencies (no `jsonschema` package assumed installed) -
this hand-rolls the checks that actually matter for the pipeline, not a
general JSON Schema validator. Run this BEFORE persisting brand-config.json
and BEFORE handing it to the merge step. Exits non-zero and prints every
failure found (not just the first) on any violation.

Usage:
    python3 validate_brand_config.py path/to/brand-config.json
"""
import json
import re
import sys

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}$")
SLUG_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FIXED_DIMENSIONS = {"topicFit", "audiencePerspective", "geoTiming", "competitiveWhitespace", "creativeStretch"}
VALID_SCOPES = {"social+news", "social", "news"}
VALID_PILLAR_STATUS = {"active", "punchlist", "deprecated"}


def fail(errors, msg):
    errors.append(msg)


def validate(cfg):
    errors = []

    for key in ["schemaVersion", "brand", "identity", "audienceSegments", "activations",
                "territory", "rejectList", "pillars", "scoring", "ops", "meta"]:
        if key not in cfg:
            fail(errors, f"missing top-level key: {key}")

    brand = cfg.get("brand", {})
    for key in ["id", "name", "category", "essence", "archetype"]:
        if not brand.get(key):
            fail(errors, f"brand.{key} is required and must be non-empty")
    if brand.get("id") and not SLUG_RE.match(brand["id"]):
        fail(errors, f"brand.id '{brand['id']}' must be a lowercase-hyphen slug (used as the brandKey)")

    identity = cfg.get("identity", {})
    colors = identity.get("colors", {})
    for c in ["primary", "secondary", "accent"]:
        v = colors.get(c)
        if not v or not HEX_RE.match(v):
            fail(errors, f"identity.colors.{c} must be a #RRGGBB hex value, got {v!r}")

    segments = cfg.get("audienceSegments", [])
    if not segments:
        fail(errors, "audienceSegments must have at least 1 entry")
    for i, s in enumerate(segments):
        for key in ["id", "name", "description"]:
            if not s.get(key):
                fail(errors, f"audienceSegments[{i}].{key} is required")

    activations = cfg.get("activations", [])
    if not activations:
        fail(errors, "activations must have at least 1 entry")
    activation_names = set()
    for i, a in enumerate(activations):
        if not a.get("name"):
            fail(errors, f"activations[{i}].name is required")
        else:
            activation_names.add(a["name"])
        if not a.get("description"):
            fail(errors, f"activations[{i}].description is required")

    territory = cfg.get("territory", {})
    if not territory.get("description"):
        fail(errors, "territory.description is required")

    reject_list = cfg.get("rejectList", [])
    if not reject_list:
        fail(errors, "rejectList must have at least 1 entry — every brand rejects something; "
                     "an empty list usually means the interview skipped this question, not that "
                     "nothing is off-territory")
    for i, r in enumerate(reject_list):
        for key in ["pattern", "reason"]:
            if not r.get(key):
                fail(errors, f"rejectList[{i}].{key} is required")

    pillars = cfg.get("pillars", [])
    if not pillars:
        fail(errors, "pillars must have at least 1 entry")
    pillar_ids = set()
    pillar_names_lower = set()
    for i, p in enumerate(pillars):
        for key in ["id", "name", "description", "scope", "status"]:
            if not p.get(key):
                fail(errors, f"pillars[{i}].{key} is required")
        if p.get("id"):
            if not SLUG_RE.match(p["id"]):
                fail(errors, f"pillars[{i}].id '{p['id']}' must be a lowercase-hyphen slug")
            if p["id"] in pillar_ids:
                fail(errors, f"pillars[{i}].id '{p['id']}' is not unique")
            pillar_ids.add(p["id"])
        if p.get("name"):
            pillar_names_lower.add(p["name"].lower())
        if p.get("scope") and p["scope"] not in VALID_SCOPES:
            fail(errors, f"pillars[{i}].scope '{p['scope']}' must be one of {sorted(VALID_SCOPES)}")
        if p.get("status") and p["status"] not in VALID_PILLAR_STATUS:
            fail(errors, f"pillars[{i}].status '{p['status']}' must be one of {sorted(VALID_PILLAR_STATUS)}")
        if "savedSearchId" not in p:
            fail(errors, f"pillars[{i}] must have a savedSearchId key (string or null)")

    scoring = cfg.get("scoring", {})
    dims = set(scoring.get("dimensions", []))
    if dims != FIXED_DIMENSIONS:
        fail(errors, f"scoring.dimensions must be exactly {sorted(FIXED_DIMENSIONS)}, got {sorted(dims)} "
                     "— these five names are the dashboard's rendering contract, not brand-configurable")
    weights = scoring.get("weights", {})
    for d in FIXED_DIMENSIONS:
        w = weights.get(d)
        if not isinstance(w, (int, float)) or w < 0:
            fail(errors, f"scoring.weights.{d} must be a non-negative number, got {w!r}")

    ops = cfg.get("ops", {})
    if not ops.get("refreshCadence"):
        fail(errors, "ops.refreshCadence is required")
    rw = ops.get("retentionWindowDays")
    if not isinstance(rw, int) or not (1 <= rw <= 14):
        fail(errors, f"ops.retentionWindowDays must be an integer 1-14, got {rw!r}")
    mp = ops.get("maxPillarsPerRefresh")
    if not isinstance(mp, int) or mp < 1:
        fail(errors, f"ops.maxPillarsPerRefresh must be a positive integer, got {mp!r}")
    md = ops.get("maxDocumentsPerPillar")
    if not isinstance(md, int) or not (1 <= md <= 50):
        fail(errors, f"ops.maxDocumentsPerPillar must be an integer 1-50, got {md!r}")
    if isinstance(mp, int) and mp > len(pillars):
        fail(errors, f"ops.maxPillarsPerRefresh ({mp}) exceeds the number of defined pillars ({len(pillars)})")

    meta = cfg.get("meta", {})
    if not meta.get("builtFromSkeletonVersion"):
        fail(errors, "meta.builtFromSkeletonVersion is required — every build must record its skeleton tag")
    if not meta.get("createdAt"):
        fail(errors, "meta.createdAt is required")

    return errors


def main():
    if len(sys.argv) != 2:
        print("usage: validate_brand_config.py path/to/brand-config.json", file=sys.stderr)
        sys.exit(2)
    path = sys.argv[1]
    with open(path) as f:
        cfg = json.load(f)
    errors = validate(cfg)
    if errors:
        print(f"✗ {path} — {len(errors)} error(s):")
        for e in errors:
            print(f"    - {e}")
        sys.exit(1)
    print(f"✓ {path} — valid brand-config "
          f"({len(cfg['pillars'])} pillars, brand '{cfg['brand']['id']}')")


if __name__ == "__main__":
    main()
