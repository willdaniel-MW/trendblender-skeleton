#!/usr/bin/env python3
"""
Deterministic structural validation for a brand's trends_data.js file against
schema/trend-record.schema.json's constraints, generalized from the original
Unilever build's hardcoded schema-validation one-liner.

Unlike the original, the forbidden-jargon list is DERIVED from the brand's
own brand-config.json (pillar ids/names) rather than hardcoded to any
brand's specific pillar labels. This is deterministic structural
enforcement only -- it cannot judge whether a trend name is *good*,
only whether it leaks pipeline internals (see trendblender-refresh's
SKILL.md for the judgment-layer checklist that this script doesn't
and can't replace).

Usage:
    python3 validate_trends.py path/to/trends_data.js path/to/brand-config.json
"""
import json
import re
import sys

FIXED_SCORE_KEYS = {"topicFit", "audiencePerspective", "geoTiming", "competitiveWhitespace", "creativeStretch"}
VALID_MOMENTUM = {"emerging", "rising", "peaked", "declining"}
VALID_BUCKET = {"HIGH", "MEDIUM", "LOW"}
VALID_PLATFORM = {"TikTok", "Instagram", "X", "Facebook", "YouTube", "Reddit", "News", "Social"}
VALID_SOURCE = {"category", "adjacent"}
GENERIC_JARGON = ["leading", "surfacing", "candidate", "search", "pillar", "cluster",
                  "trending topic", "trend:"]


def extract_brand_object(js_text, brand_key):
    # Brand ids are hyphenated slugs (e.g. "acme-clean"), which is not a valid
    # JS dot-access identifier -- the skeleton's convention is always
    # window.TRENDS_DATA["<brandKey>"] bracket notation. Also accept dot
    # notation defensively in case a single-word brand id was written that way.
    patterns = [
        r"window\.TRENDS_DATA\[(?:'|\")" + re.escape(brand_key) + r"(?:'|\")\]\s*=\s*(\{.*?\});",
        r"window\.TRENDS_DATA\." + re.escape(brand_key) + r"\s*=\s*(\{.*?\});",
    ]
    for pat in patterns:
        m = re.search(pat, js_text, re.S)
        if m:
            return json.loads(m.group(1))
    return None


def validate(obj, brand_cfg):
    errors = []
    brand_key = brand_cfg["brand"]["id"]
    activation_names = {a["name"] for a in brand_cfg["activations"]}
    pillar_labels = []
    for p in brand_cfg["pillars"]:
        pillar_labels.append(p["id"])
        pillar_labels.append(p["name"].lower())
        pillar_labels.append(f"{brand_cfg['brand']['name']}-{p['name']}".lower().replace(" ", ""))

    if "generated_at" not in obj:
        errors.append("missing generated_at")

    trends = obj.get("trends")
    if trends is None:
        errors.append("missing trends[] array")
        return errors

    seen_ids = set()
    url_total, url_present = 0, 0

    for i, t in enumerate(trends):
        loc = f"trends[{i}] (id={t.get('id', '?')})"

        tid = t.get("id")
        if not tid:
            errors.append(f"{loc}: missing id")
        elif tid in seen_ids:
            errors.append(f"{loc}: duplicate id '{tid}'")
        elif not tid.startswith(f"{brand_key}-"):
            errors.append(f"{loc}: id '{tid}' should be prefixed '{brand_key}-'")
        seen_ids.add(tid)

        name = (t.get("name") or "")
        if not name:
            errors.append(f"{loc}: missing name")
        name_lower = name.lower()
        for jargon in GENERIC_JARGON:
            if jargon in name_lower:
                errors.append(f"{loc}: name contains forbidden pipeline jargon '{jargon}': {name!r}")
        for label in pillar_labels:
            if label and label in name_lower:
                errors.append(f"{loc}: name leaks a pillar id/label ('{label}'): {name!r}")
        if re.search(r"\b\d{6,}\b", name):
            errors.append(f"{loc}: name appears to contain a raw search ID: {name!r}")

        social = t.get("social")
        news = t.get("news")
        if social not in VALID_BUCKET:
            errors.append(f"{loc}: social '{social}' not in {sorted(VALID_BUCKET)}")
        if news not in VALID_BUCKET:
            errors.append(f"{loc}: news '{news}' not in {sorted(VALID_BUCKET)}")

        momentum = t.get("momentum")
        if momentum not in VALID_MOMENTUM:
            errors.append(f"{loc}: momentum '{momentum}' not in {sorted(VALID_MOMENTUM)}")

        scores = t.get("scores") or {}
        score_keys = set(scores.keys())
        if score_keys != FIXED_SCORE_KEYS:
            errors.append(f"{loc}: scores keys {sorted(score_keys)} != required {sorted(FIXED_SCORE_KEYS)} "
                           "(dashboard renders NaN on any key drift)")
        for k, v in scores.items():
            if not isinstance(v, int) or not (1 <= v <= 10):
                errors.append(f"{loc}: scores.{k} must be an integer 1-10, got {v!r}")

        am = t.get("activationMatch")
        if am is not None and am not in activation_names:
            errors.append(f"{loc}: activationMatch '{am}' does not match any brand-config activation name "
                           f"{sorted(activation_names)} (must be exact, or null)")

        source = t.get("source")
        if source not in VALID_SOURCE:
            errors.append(f"{loc}: source '{source}' not in {sorted(VALID_SOURCE)}")

        posts = t.get("posts") or []
        if not posts:
            errors.append(f"{loc}: posts[] must have at least one entry")
        for j, p in enumerate(posts):
            url_total += 1
            if not p.get("text") or not p.get("author") or not p.get("platform"):
                errors.append(f"{loc}.posts[{j}]: text, author, and platform are all required")
            if p.get("platform") and p["platform"] not in VALID_PLATFORM:
                errors.append(f"{loc}.posts[{j}]: platform '{p['platform']}' not in {sorted(VALID_PLATFORM)}")
            if p.get("url"):
                url_present += 1
                if not re.match(r"^https?://", p["url"]):
                    errors.append(f"{loc}.posts[{j}]: url '{p['url']}' doesn't look like a real URL")

    return errors, url_total, url_present


def main():
    if len(sys.argv) != 3:
        print("usage: validate_trends.py path/to/trends_data.js path/to/brand-config.json", file=sys.stderr)
        sys.exit(2)
    trends_path, config_path = sys.argv[1], sys.argv[2]

    with open(config_path) as f:
        brand_cfg = json.load(f)
    brand_key = brand_cfg["brand"]["id"]

    with open(trends_path) as f:
        js_text = f.read()

    obj = extract_brand_object(js_text, brand_key)
    if obj is None:
        print(f"✗ {trends_path} — no `window.TRENDS_DATA.{brand_key} = {{...}};` assignment found "
              f"(wrong global name means the dashboard silently falls back to mock data)")
        sys.exit(1)

    errors, url_total, url_present = validate(obj, brand_cfg)
    n_trends = len(obj.get("trends", []))
    pct = (url_present * 100 // url_total) if url_total else 0

    if errors:
        print(f"✗ {trends_path} — {n_trends} trends, {url_present}/{url_total} URLs ({pct}%), "
              f"{len(errors)} error(s):")
        for e in errors:
            print(f"    - {e}")
        sys.exit(1)

    print(f"✓ {trends_path} — {n_trends} trends, {url_present}/{url_total} URLs ({pct}%)")


if __name__ == "__main__":
    main()
