---
name: trendblender-refresh
description: Execute a TrendBlender refresh for a brand configured via brand-config.json — fetch signal per pillar from its persisted Meltwater saved search, cluster/dedupe/reject/score it against the brand's own DNA, and write the dashboard's data files. Load this skill when the user says "do a run", "run TrendBlender", "refresh the trends", "refresh the pipeline", "daily refresh", "pull the latest", "update the trends", "run the morning refresh", or "run the evening refresh". Produces trends_data.js (registering window.TRENDS_DATA["<brandKey>"]) plus a client-facing morning_brief.js, matching the exact schema the dashboard expects. Brand-agnostic — reads brand.id, pillars[], scoring, ops, rejectList, activations, audienceSegments and territory from brand-config.json; invents nothing.
---

# TrendBlender — Refresh Workflow

## Preconditions

Before starting, verify:

1. `brand-config.json` exists at the repo root (or the path the operator gives you) and validates against `schema/brand-config.schema.json`. If it fails `scripts/validate_brand_config.py`, stop and tell the operator — do not guess at missing fields.
2. Every pillar in `pillars[]` with `status: "active"` has a non-null `savedSearchId`. A pillar's boolean is drafted and persisted at **onboarding time** by a separate skill (`unified_retrieval_query_gen_tool` → `listening_create_search`, ID written back into `brand-config.json`) — this skill only *consumes* that ID, it never invents a boolean or creates a search itself. If an active pillar has `savedSearchId: null`, skip it, flag it in the operator report, and do not fabricate a substitute search.
3. The relevant Meltwater MCP tools are loaded: `unified_retrieval_statistics_retrieval_tool`, `unified_retrieval_document_retrieval_tool`. Search for them with `ToolSearch` if they're deferred. If they're unavailable, tell the operator the connector needs authorizing and stop.
4. Read `brand-config.json`'s `ops` block and hold yourself to it for the whole run: `ops.maxPillarsPerRefresh` (how many pillars this refresh may touch), `ops.maxDocumentsPerPillar` (hard cap on the `limit` param to the document tool), `ops.retentionWindowDays` (the lookback window for both fetch calls). These are cost controls, not suggestions — do not raise them because a pillar "looks thin."

## The workflow

### Step 1 — select pillars for this refresh

Filter `pillars[]` to `status: "active"` with a non-null `savedSearchId`. If the count exceeds `ops.maxPillarsPerRefresh`, take the highest-priority subset (ask the operator which, if it isn't obvious, rather than silently dropping pillars) and note the deferred ones in the final report.

### Step 2 — dispatch pillars in parallel

Fire one subagent per selected pillar (or small batches of pillars if the count is high) **in a single tool-use block** so they run concurrently — wall-clock tracks the busiest pillar's document count, not the sum across all pillars. Each subagent, for its pillar:

1. Loads the two retrieval tools via one `ToolSearch` call if deferred.
2. Calls `unified_retrieval_statistics_retrieval_tool` with `savedSearchIds: [<pillar.savedSearchId>]`, `query: "*"`, and a date range spanning `ops.retentionWindowDays` back from today. This returns real volume/sentiment/platform numbers for the pillar — use these to describe the pillar as clean/mixed/noisy/silent in the report, not a subjective read of the documents.
3. Calls `unified_retrieval_document_retrieval_tool` with `savedSearchIds: [<pillar.savedSearchId>]`, `query: <pillar.description>` (plain English — this tool does not support boolean operators, the saved search already does the filtering), `sortBy: "engagement"`, `limit: ops.maxDocumentsPerPillar`, and the same date range.
4. Returns the raw documents plus the statistics summary to the orchestrator. Subagents do NOT cluster, score, or write files — that happens once, across all pillars together, in Step 3, because the same real-world moment can surface from more than one pillar and must be deduplicated across them, not just within one.

See `references/fetch-tools-reference.md` for exact parameters and gotchas for all three retrieval tools (including the query-gen tool used at onboarding time, documented there for context).

### Step 3 — cluster, dedupe, reject, score (the judgment layer)

This is the part the deterministic validators in Step 5 cannot do. Work through `references/clustering-judgment-checklist.md` in full — it has the numbered tests to apply and a worked example. In brief:

1. Pool every document returned across all dispatched pillars.
2. Cluster into candidate trends: same underlying real-world moment → one candidate, regardless of which pillar(s) or how many individual posts surfaced it. A post is evidence for at most one trend's identity.
3. Dedupe against **this refresh's own pillars** (cross-pillar) and, if you have visibility into the previous refresh's output (e.g. the existing `trends_data.js` on disk), against **the prior run** (cross-refresh) — `ops.retentionWindowDays` deliberately overlaps refresh to refresh, so a real trend legitimately still being talked about is not a new trend; carry its `id` forward and update it rather than duplicating it.
4. Apply `rejectList[]` as a hard gate **before** scoring. No score, however high, rescues a candidate matching a reject pattern. Record why in your own working notes (not the output file).
5. Score every surviving candidate 1–10 on the five fixed dimensions (`topicFit`, `audiencePerspective`, `geoTiming`, `competitiveWhitespace`, `creativeStretch`) against the brand's `territory.description`, `audienceSegments[]`, and `activations[]`. Set `activationMatch` to an exact `activations[].name` match or `null` — never invent one.
6. Run the self-critique pass: re-read every surviving trend once more against `rejectList[]` and ask "would a skeptical brand manager reject this?" Drop or rewrite anything that fails.

### Step 4 — write the trends file

Write `trends_data.js` (this exact filename, always — the dashboard's `<script src="trends_data.js">` tag is fixed so a single-brand plugin build never needs per-brand HTML edits) in the **exact schema** below, registering into `window.TRENDS_DATA["<brandKey>"]` where brandKey = `brand.id` from brand-config.json — a lowercase-hyphen slug. Because `brand.id` contains hyphens, you MUST use bracket notation. Dot notation is invalid JS for a hyphenated key and will silently break the page load.

```js
window.TRENDS_DATA = window.TRENDS_DATA || {};
window.TRENDS_DATA["<brandKey>"] = {
  "generated_at": "2026-09-16T09:15:00+01:00",
  "source_pillars": [
    { "id": "pillar-id", "name": "Pillar label", "savedSearchId": 12345678, "status": "clean" }
  ],
  "data_quality_notes": [],
  "trends": [
    {
      "id": "<brandKey>-1",
      "name": "Client-facing trend title — no pipeline jargon",
      "summary": "One-sentence analyst context.",
      "social": "HIGH",
      "news": "LOW",
      "momentum": "rising",
      "scores": {
        "topicFit": 9,
        "audiencePerspective": 9,
        "geoTiming": 8,
        "competitiveWhitespace": 7,
        "creativeStretch": 2
      },
      "activationMatch": "Activation name from brand-config.json, or null",
      "source": "category",
      "posts": [
        {
          "text": "Actual post text or headline",
          "author": "@handle or Source Name",
          "platform": "TikTok",
          "url": "https://…",
          "views": 12345
        }
      ],
      "hashtags": []
    }
  ]
};
```

Even though this is a `.js` file, the object literal after the `=` must be **strict, valid JSON**: double-quoted keys and strings, no trailing commas, no comments, no template literals. The validator extracts it with a regex and parses it with `json.loads` — anything that would only work as loose JS fails validation even if a browser would happily run it.

See `references/schema.md` for the full field-by-field reference.

### Step 5 — run the deterministic validator

```bash
python3 scripts/validate_trends.py trends_data.js brand-config.json
```

This checks score-key completeness (all five fixed keys, integers 1–10), momentum enum, platform enum, `activationMatch` against real activation names, id prefixing/uniqueness, and — critically — a forbidden-jargon scan that is **derived from this brand's own `pillars[].id`/`pillars[].name`**, not hardcoded to any specific brand's labels. Read `scripts/validate_trends.py` if you want the exact logic. Do not finalize output until it exits clean. If it fails, fix the file and re-run — do not hand-patch around a failure by relaxing the check.

### Step 6 — write the morning brief

Load the `trendblender-morning-brief` skill to produce `morning_brief.js` — exactly four bullets (`strongest_signal`, `earned_media`, `creator_opportunity`, `time_sensitive`) drawn from the trends you just wrote. Then validate:

```bash
python3 scripts/validate_brief.py morning_brief.js
```

Do not finalize until this also exits clean.

### Step 7 — report to the operator

Post a concise chat summary. This report **never** goes into `morning_brief.js` or any output file — it's for the operator only.

- Pillars fetched this run vs. deferred (and why, e.g. over `maxPillarsPerRefresh`, or `savedSearchId` still null)
- Real statistics per pillar from `unified_retrieval_statistics_retrieval_tool` — volume, sentiment split, platform breakdown — labelled clean/mixed/noisy/silent from the numbers, not vibes
- Document retrieval coverage: documents returned vs. `maxDocumentsPerPillar` cap, per pillar
- URL coverage across all posts written (X/Y, %)
- Candidates rejected at the `rejectList[]` gate, and why (feeds the `trendblender-boolean-punchlist` skill if a pillar is structurally noisy rather than a one-off)
- Total trend count, new vs. carried-forward from the prior refresh
- Any decision-required flags: a pillar candidate for deprecation (see the boolean-reference criteria — repeated zero-return or majority-noise runs), a competitor movement worth a human look, a scoring weight that seems off for this brand

Do not restate trend contents in the chat report — the operator reads those in the file.

## What this skill does and does not guarantee

The Python validators enforce **structure**: schema shape, enums, score-key completeness, no fabricated URLs, no leaked pipeline jargon (derived from this brand's real pillar labels). They cannot and do not judge whether two posts are the same trend, whether a borderline post is genuinely off-territory, or whether a trend name reads well — those are judgment calls this skill has to make fresh every refresh, using the checklist in `references/clustering-judgment-checklist.md`. Expect a human review pass on every refresh's output, and expect the first refresh on a freshly onboarded brand to be noisier than later ones — its pillars were auto-drafted from a plain-English brief, not yet hand-tuned. That is the expected starting point for the `trendblender-boolean-punchlist` skill's tuning loop, not a sign this skill failed.

## Reference material bundled

- **`references/schema.md`** — The `window.TRENDS_DATA` trend-record schema in full, field-by-field, generic to any brand-config.json.
- **`references/clustering-judgment-checklist.md`** — The numbered judgment checklist (clustering, dedup, reject-gate ordering, self-critique) plus a worked example using a fictional demo brand.
- **`references/fetch-tools-reference.md`** — Exact parameters and return shapes for `unified_retrieval_query_gen_tool` (onboarding-time only), `unified_retrieval_statistics_retrieval_tool`, and `unified_retrieval_document_retrieval_tool`.
