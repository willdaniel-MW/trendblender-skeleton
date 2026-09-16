# TrendBlender Architecture

This is the end-to-end architecture of the TrendBlender skeleton: a brand-agnostic social trend-jacking pipeline. It's written to be shareable with a client or an internal team, not just loaded as agent context — worked examples use a fictional demo brand ("Northwind Home," a household-cleaning brand that does not exist) rather than any real client.

Nothing in this document, or in the repo it describes, names a real brand. Brand-specific facts live entirely in `brand-config.json`, produced by the separate `trendblender-onboard-brand` skill and validated against `schema/brand-config.schema.json`.

## 1. The two-loop shape

TrendBlender is two loops, deliberately kept separate:

**The refresh loop — autonomous, scheduled.** This is the "do a run" workflow (`trendblender-refresh` + `trendblender-morning-brief`). It runs on a cadence the brand sets (`brand-config.json`'s `ops.refreshCadence`, e.g. "1/weekday" or "2/weekday"), fetches fresh signal for every active pillar, scores and writes trend data, and produces the client-facing morning brief. No human sign-off gates this loop — it's designed to run unattended on schedule.

**The maintenance loop — human-gated.** This is `trendblender-boolean-punchlist`. It exists because saved searches drift: a pillar goes silent, or starts bleeding off-territory noise. The punchlist skill watches for threshold conditions across refreshes (see §5 below and the `meltwater-boolean` reference for the exact deprecation criteria — four-plus zero-return refreshes, three-plus refreshes over 70% noise, or a boolean that's grown past Meltwater's practical size ceiling), proposes a fix, and **always stops for explicit operator sign-off before writing anything back to Meltwater.** Nothing in this loop is autonomous by design — a saved search is a persistent, shared platform object, and an unreviewed automated edit to it is a different (and much riskier) class of action than writing a local trend-data file.

Keeping these loops separate means the scheduled loop never silently rewrites the thing (the saved search) that everything else depends on being stable, and the maintenance loop never has to move at refresh cadence — it only needs to move when the data says a pillar actually needs attention.

```
 ┌────────────────────────────┐        ┌──────────────────────────────┐
 │   REFRESH LOOP (autonomous)│        │  MAINTENANCE LOOP (gated)     │
 │   trendblender-refresh     │        │  trendblender-boolean-        │
 │   + trendblender-morning-  │        │  punchlist                    │
 │   brief                    │        │                                │
 │                            │  noise  │  observe → diagnose →         │
 │  runs on refreshCadence ───┼────────▶│  propose fix → operator       │
 │  writes trends_*.js +      │ silence │  sign-off → update_search     │
 │  morning_brief.js          │         │                                │
 └────────────────────────────┘        └──────────────────────────────┘
              │                                        │
              ▼                                        ▼
   reads pillars' savedSearchId          writes savedSearchId's boolean
   from brand-config.json                back to the SAME saved search
```

## 2. The fan-out / concurrency model

A refresh dispatches work per pillar, not sequentially through one context. One tool-use block launches a subagent per pillar (or, for brands with many pillars, a subagent per small batch of pillars, bounded by `ops.maxPillarsPerRefresh`) — all in the same round trip, so they execute **concurrently**, not one after another.

Each subagent is an isolated worker: it only sees its own pillar's saved search, territory rules, and reject-list entries. It has no visibility into what other pillars' subagents are doing, and it re-confirms any account-level Meltwater context itself rather than assuming session state carries over — a subagent starts from a blank context.

Within a single pillar's lane, work is sequential: a statistics-tool call, then a document-tool call, then the pillar's own clustering/scoring pass. Concurrency exists across pillars, not within one.

This has a direct wall-clock consequence: **total refresh time tracks the busiest single pillar (or batch), not the sum of all pillars.** For a demo brand like Northwind Home with, say, six pillars split into three subagents of two pillars each, wall-clock is roughly "however long the slowest of those three lanes takes" — not six pillars' worth of sequential calls. This is why pillar count scales cost (see §6) without scaling wall-clock linearly, as long as pillars are fanned out rather than run in one long sequential chain.

## 3. The fetch redesign

This is the most consequential change from the pipeline this skeleton replaces, so it's worth walking through in detail.

**The old approach.** Each saved search was queried through a single freeform natural-language prompt into an LLM-mediated media-search tool — effectively asking an LLM "give me the top trending stories for this search" and trusting its subjective read of what came back. This only became usable after a lot of manual, iterative tuning per search, because the tool's own judgment about relevance and volume had no independent structural signal to check itself against. The failure mode was real and documented: a noise-reduction fix applied to one search over-tightened it so hard that it returned only 3 documents in a 48-hour window, and the fix had to be partially reverted before the search was usable again. Getting a single saved search to a stable, low-noise state took several iterations of "tighten, refresh, observe, loosen a little" — expensive in both API calls and operator time, and it didn't generalize: every new search started that tuning process from zero.

**The new approach — split into three phases:**

1. **Query generation, at onboarding time.** `unified_retrieval_query_gen_tool` takes a plain-English pillar brief (`brand-config.json`'s `pillars[].description`) and drafts a Meltwater boolean query from it. This replaces hand-written boolean tuning as the starting point — it's not perfect out of the box (see §5, "day one is rough"), but it starts from a structurally reasonable boolean instead of an empty one.
2. **Persistence, at onboarding time.** That drafted boolean is saved as a real Meltwater saved search via `listening_create_search`, and its ID is written into the pillar's `savedSearchId` field in `brand-config.json`. From this point on, the pillar has a durable, platform-level object backing it — not a prompt that gets re-interpreted differently each run.
3. **Fetch, at refresh time — split into two independent, non-LLM-mediated calls:**
   - `unified_retrieval_statistics_retrieval_tool` — returns real, computed volume and sentiment numbers for the saved search. This is what tells a refresh whether a pillar is "clean," "mixed," "noisy," or effectively silent — a structural read, not an LLM's impression of the numbers.
   - `unified_retrieval_document_retrieval_tool` — returns real evidence documents (posts, articles) with real URLs, scoped to the same saved search. This is the source of every post that ends up in a trend record's `posts[]` array — never fabricated, and the schema (`schema/trend-record.schema.json`) requires the `url` field be omitted entirely rather than invented if the tool didn't return one for a given post.

The upshot: relevance tuning now happens once, at the saved-search level, using a boolean-maintenance workflow with its own documented recipes (see `meltwater-boolean`) — not implicitly, per-refresh, inside an LLM's interpretation of a freeform prompt. Numbers used for scoring and status ("is this pillar noisy or clean?") come from a statistics call, not an LLM's read of a document dump.

## 4. Output file contracts

Three schemas define everything this pipeline reads or writes. Full field-level detail lives in the schema files themselves — this section explains what each one is for and doesn't restate every field.

- **`schema/brand-config.schema.json`** — the input contract. Everything brand-specific (identity, audience segments, activations, territory, reject list, pillars, scoring weights, ops caps) lives here. This is the only schema a human (via the onboarding interview) fills in directly; everything downstream derives from it.
- **`schema/trend-record.schema.json`** — the shape of `trends_data.js` (the on-disk filename is always `trends_data.js`, never `trends_<brandKey>.js` — the dashboard's script tag is fixed so a single-brand plugin build never needs per-brand HTML edits), loaded by the dashboard as `window.TRENDS_DATA["<brandKey>"]` (bracket notation — brandKey is a hyphenated slug). Per-trend fields include the five fixed scoring dimensions, momentum classification, and an evidence `posts[]` array. The five score dimension *names* and the four momentum values are fixed by the dashboard's own rendering code — not brand-configurable — while score *weights* are read from `brand-config.json`.
- **`schema/morning-brief.schema.json`** — the shape of `morning_brief.js`, loaded as `window.MORNING_BRIEF`. Exactly four bullets, in a fixed `kind` order (`strongest_signal`, `earned_media`, `creator_opportunity`, `time_sensitive`). This is the one artifact a client actually sees; nothing pipeline-internal (search IDs, pillar names, noise diagnostics) is permitted in it.

Both output files are written by `trendblender-refresh` (trend records) and `trendblender-morning-brief` (the brief), and both are checked against their schemas by the validators in `scripts/` before either is treated as final.

## 5. Enforcement vs. judgment

This split is explicit and load-bearing, not incidental.

**What's enforced deterministically.** The Python scripts in `scripts/` (`validate_brand_config.py`, `validate_trends.py`, `validate_brief.py`) run with no external dependencies and check pure structure: required fields present, enum values valid, score objects complete with all five fixed keys, no fabricated URLs (a post either has a real URL from the document-retrieval tool or omits the field), and no leaked pipeline jargon in client-facing trend names (`validate_trends.py` derives its forbidden-term list from the brand's own pillar ids/names, plus a generic jargon list, rather than hardcoding any one brand's vocabulary). These checks are cheap, fast, and produce the same answer every time given the same input. They run before anything is written or shown to an operator or client.

**What is not, and cannot be, enforced deterministically.** Whether two posts represent the same underlying trend (clustering/dedup). Whether a borderline post is genuinely on- or off-territory given the brand's `territory.description` and `rejectList`. Whether a generated trend name actually reads well to a client, beyond just being jargon-free. These are judgment calls, and they're made by an LLM on every single refresh — this skeleton does not claim, and should not be represented as claiming, that those calls are made with full consistency run to run. What it does instead: each skill that makes one of these calls (`trendblender-refresh` for clustering/territory, `trendblender-morning-brief` for bullet selection, `trendblender-boolean-punchlist` for deprecation/rebuild decisions) documents its own checklist and self-critique steps in its `SKILL.md`, aimed at making that judgment as disciplined and repeatable as a judgment call can be made. A human review pass is expected on every refresh, and especially expected on a freshly onboarded brand's first refresh (see below).

**Day one is rough, on purpose.** A freshly onboarded brand's pillars are auto-drafted booleans (§3), not hand-tuned ones. The structural validators will pass on a first refresh even if the results are noisy, because "structurally valid" and "well-tuned" are different properties — that's exactly why the enforcement/judgment split matters. Expect the first refresh for a new brand (or a newly added pillar on an existing brand) to need a pass through `trendblender-boolean-punchlist` shortly after, and treat that as the expected second step of onboarding, not a sign that something went wrong.

## 6. Cost and cadence

Cost scales with **pillar count × per-pillar document cap**, bounded explicitly by three fields in `brand-config.json`'s `ops` block, set at onboarding time:

- **`ops.maxPillarsPerRefresh`** — caps how many pillars a single refresh actually fetches. A brand can have more pillars defined (some `status: "punchlist"` or `"deprecated"`) than it refreshes on every run.
- **`ops.maxDocumentsPerPillar`** (1–50) — caps how many evidence documents `unified_retrieval_document_retrieval_tool` pulls per pillar per refresh. This is the main per-call cost lever.
- **`ops.refreshCadence`** — free-text cadence (e.g. "1/weekday", "2/weekday"), which multiplies the per-refresh cost by however many refreshes happen in a week.

Worked example with the fictional demo brand: Northwind Home onboards with 6 active pillars, `maxDocumentsPerPillar: 20`, and `refreshCadence: "1/weekday"`. Each weekday refresh costs on the order of 6 pillars × (1 statistics call + 1 document call, capped at 20 documents) — a small, bounded, and predictable number of calls, fanned out across (per §2) roughly 2–3 concurrent subagent lanes rather than run sequentially. Contrast a brand with 12 pillars and `maxDocumentsPerPillar: 50` on a "2/weekday" cadence: cost is roughly 4x Northwind Home's per-refresh cost, and happens twice as often — the two knobs compound.

The point of making these three fields explicit onboarding-interview questions, rather than constants baked into a skill file, is that a self-serve onboarding flow with no caps at all can run away on API cost the moment someone requests a large number of pillars, a high document cap, and a high-frequency cadence, all at once, without anyone having deliberately signed off on that combination. Conservative defaults exist so that an operator has to actively choose to raise them.
