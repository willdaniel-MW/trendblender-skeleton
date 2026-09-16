---
name: trendblender-getting-started
description: Orientation primer for TrendBlender — a brand-agnostic daily social trend-jacking pipeline. Load this the first time in a new session, or when the user says "what is TrendBlender", "how does this work", "onboard me", "explain the pipeline", "what does a run produce", "where are the trends", or asks about pillars, brand-config.json, or this skeleton's scope without other context. This skill is background context, not an action — it hands off to trendblender-refresh, trendblender-morning-brief, trendblender-boolean-punchlist and meltwater-boolean for the actual work.
---

# TrendBlender — Getting Started

## What this system is

TrendBlender is a social trend-jacking pipeline: for a brand you define, it pulls Meltwater signal against a set of "pillars" (topic territories you configure, not a fixed list), clusters and scores what comes back against that brand's own DNA, and writes a small, self-contained dashboard plus a client-facing daily brief.

**This skeleton ships with zero brand content.** No essence, no audience segments, no saved searches, no colours, no real brand name anywhere in this repo. Every brand-specific fact — positioning, audience segments, activations, territory, reject list, pillars, score weights, identity colours, cost/cadence caps — lives in one file, `brand-config.json`, validated against `schema/brand-config.schema.json`. That file is produced by a separate onboarding skill, `trendblender-onboard-brand` (not part of this repo), which interviews the operator and packages this skeleton plus the filled-in config into an installable, brand-specific plugin. If you're looking at this skill with no `brand-config.json` present, you're looking at the skeleton itself — the onboarding skill is what you want next, not a run.

Pillar count is not fixed. A brand can have one pillar or a dozen; nothing in this skeleton assumes a specific number.

## What a run produces

Say the user (with a brand already onboarded) types "do a run" or "refresh the trends":

1. Load the `trendblender-refresh` skill.
2. For each pillar in `brand-config.json`, fetch volume/sentiment via `unified_retrieval_statistics_retrieval_tool` and real evidence posts via `unified_retrieval_document_retrieval_tool`, scoped to that pillar's persisted Meltwater saved search.
3. Cluster, dedupe, and score each candidate trend against the brand's territory, reject list, and activations.
4. Write `trends_data.js` (per-brand trend data, registering `window.TRENDS_DATA["<brandKey>"]` — bracket notation, since brandKey is a hyphenated slug; the on-disk filename is always `trends_data.js`, never `trends_<brandKey>.js`, so the dashboard HTML never needs per-brand edits) and `morning_brief.js` (the four-bullet client-facing brief, `window.MORNING_BRIEF`).
5. Validate both files with the deterministic Python scripts in `scripts/` before anything is considered final.
6. Report back to the operator: which pillars were noisy or silent, any new noise patterns worth a boolean fix.

The dashboard (`dashboard/trendjack.html`) reads brand identity, colours, and score weights from a `brand_config.js` sibling file at load time — it has no brand hardcoded into it.

## What changed vs. a hand-rolled per-brand build

This skeleton is a rebuild of an earlier version that was hardcoded to one client's four brands. The lessons from that build shaped this one:

1. **The fetch bottleneck is fixed.** The original ran one freeform natural-language prompt per hand-tuned saved search through an LLM-mediated search tool — usable only after a lot of iterative manual tuning (one real fix over-tightened a search's noise filter to just 3 documents in 48 hours before it had to be loosened back up). This skeleton instead auto-drafts each pillar's boolean query at onboarding time with `unified_retrieval_query_gen_tool`, persists it as a real Meltwater saved search, and at refresh time fetches through a statistics tool (real numbers, not an LLM's subjective read) and a document tool (real posts with real URLs).
2. **Brand-agnostic by construction.** Nothing in this repo names a real brand. `brand-config.json` is the only place brand content lives, and it's a persisted, standalone artifact independent of any specific built plugin — a brand can be rebuilt against a newer skeleton version later without re-doing the onboarding interview.
3. **Pillar count isn't fixed.** The original had exactly four brands with 7–10 hand-tuned searches each. This skeleton supports any number of pillars per brand.
4. **The dashboard reads config instead of hardcoding it.** Brand identity, colours, and score weights come from `brand_config.js`, not a hardcoded object baked into the dashboard's HTML.
5. **Cost is capped explicitly, not implicitly.** `ops.maxPillarsPerRefresh`, `ops.maxDocumentsPerPillar`, and `ops.refreshCadence` in `brand-config.json` are onboarding-interview questions with conservative defaults, not constants nobody deliberately set.
6. **Day one is expected to be rough.** A freshly onboarded brand's pillars are auto-drafted from a plain-English description, not hand-tuned — the first refresh will be structurally valid but noisy. That's expected, not a bug.
7. **Judgment vs. structure is an explicit, named distinction.** Deterministic Python validators in `scripts/` enforce structure — schema shape, valid enums, no fabricated URLs, no leaked pipeline jargon in client-facing trend names. They cannot and do not enforce judgment — whether two posts represent the same trend, whether a borderline post is on-territory, whether a trend name reads well. That's an LLM call every refresh, and it isn't claimed to be fully consistent. Each relevant skill documents its own checklist for making that judgment call as disciplined as possible.

## What the operator needs to know before the first run

**Meltwater MCP connector must be authorized** for the workspace this brand's saved searches live in (`brand-config.json`'s `meta.meltwaterAccountId`). This skeleton does not ship credentials.

**A freshly onboarded brand needs a tuning pass.** Expect the first refresh to surface noisy or off-territory results on at least one pillar. That's what `trendblender-boolean-punchlist` is for — it's the gated maintenance loop (3-refresh thresholds, always requiring explicit operator sign-off before writing to Meltwater) for tightening a pillar's saved search once it's bleeding noise or gone silent.

**The client sees the brief. Pipeline mechanics stay in chat.** Anything about search noise, boolean tuning, pillar deprecation, competitor observations, or pipeline internals belongs in the operator-facing chat report — never in `morning_brief.js`.

## Reference material bundled

- `references/architecture-pointer.md` — a short pointer into `docs/architecture.md` (the full end-to-end writeup) for anyone who wants the detailed version: the two-loop shape, fan-out/concurrency model, fetch redesign, output contracts, and cost/cadence math.

## Related skills

- **`trendblender-refresh`** — the actual "do a run" workflow: fetch, cluster, score, write, validate.
- **`trendblender-morning-brief`** — writing the four-bullet client-facing brief.
- **`trendblender-boolean-punchlist`** — the human-gated boolean maintenance loop for tuning a pillar's saved search.
- **`meltwater-boolean`** — generic Meltwater boolean-query reference (operators, noise-reduction recipes, syntax gotchas); brand-agnostic, used by the punchlist skill and by onboarding.
