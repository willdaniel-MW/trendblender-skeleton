---
name: trendblender-boolean-punchlist
description: Manage the boolean-maintenance loop for a brand's Meltwater saved searches (one per active pillar in that brand's brand-config.json, arbitrary length). Load this skill when the user says "boolean fixes", "improve the booleans", "fix the noise", "reduce noise", "punchlist", "next round of boolean improvements", when a refresh has surfaced repeatable off-territory content in a specific search, or — routinely — shortly after a brand is first onboarded, since its pillar booleans are auto-drafted and expected to need this pass. Wraps the observed-noise → diagnosis → draft-fix → sign-off → API-push → validation-refresh cycle. Uses `listening_update_search` to push changes and always requires operator sign-off before writing to production. Any pillar deprecated or given a new savedSearchId here must be written back into that brand's brand-config.json.
---

# TrendBlender — Boolean Punchlist Workflow

## Purpose

Every active pillar in a brand's `pillars[]` array (arbitrary length — schema/brand-config.schema.json places no fixed count on it) has a Meltwater saved search behind it. Those searches are the sensors that feed the whole pipeline. When one starts bleeding off-territory content or going silent, the fix belongs here — not in the `trendblender-refresh` skill. This is a distinct, deliberate maintenance workflow with a sign-off gate before any production edit.

## This is a routine step, not a rare one

In this architecture, a brand's pillar booleans are **auto-drafted** by `unified_retrieval_query_gen_tool` at onboarding time from a plain-English pillar description — nobody hand-tunes them before they first run. That means the first real tuning pass for every newly onboarded brand happens here, and it happens *soon* after onboarding, not only if something later goes wrong. Expect to run this skill shortly after any brand's first refresh, as a matter of course, not as an exception-handling path. Treat "day one is rough" as the normal state a fresh brand starts in, and this skill as the expected next step — see the root `README.md`'s "Day one will be rough, on purpose" section for the same framing at the repo level.

## When to add something to the punchlist

Add a search to the punchlist when either:

- **Bleeding** — three or more consecutive refreshes where 30%+ of returned content is off-territory (wrong market, wrong category, engagement-farm content, competitor-brand promo).
- **Silent** — three or more consecutive refreshes at zero returns despite the topic being culturally live.
- **Over-tightened** — a recent boolean edit has dropped the search from healthy volume to near-zero.

Do NOT add a search after one bad refresh — the 3-refresh threshold guards against overreacting to weekly noise. This threshold is sound engineering judgment independent of brand; don't loosen it just because a brand is newly onboarded and everything looks noisy at once — triage by the same rule, just expect more items on the list the first time through.

## The workflow

### Step 1 — surface the punchlist

At the end of a refresh, list all searches on the current punchlist with a one-line diagnosis each, sourced from that brand's own `references/current-punchlist-TEMPLATE.md`-derived working file (see below). Rank by highest-impact-first:

1. **Structural / silent** (search is broken — quick and safe to fix)
2. **Persistent bleed with a clear noise cluster** (add specific NOT clauses)
3. **Persistent bleed without a clear noise cluster** (needs an AND-gate refactor)
4. **Volume-fine but wrong-vocabulary** (rebuild, don't patch — see deprecation criteria)

### Step 2 — pull the current boolean

For each search on the punchlist, call `listening_get_search({ saved_search_id: <id>, include_runes: true })`. Log the current boolean in that brand's round-history file — you'll need it for rollback and for diffing.

### Step 3 — draft the fix

For each search, propose a specific patch. Show the operator:

- The exact fragment being added or removed
- The rationale (what noise this stops, what signal it preserves)
- Estimated boolean size after the change (`listening_update_search` degrades badly as a boolean approaches ~4 kB)

Use the recipes in the sibling **`meltwater-boolean`** skill rather than duplicating them here — it's already brand-agnostic and covers the stain/effort AND-gate, content-based geo blocks, the AI-storytime/engagement-farm block, handle enumeration (`from:` doesn't accept wildcards), and the hashtag dual-index block. Load it alongside this skill; it activates automatically for any Meltwater boolean work.

### Step 4 — get sign-off

**BLOCKING GATE.** Never push a boolean edit without explicit operator confirmation. Present the fix as a compact review — "current fragment / proposed fragment / rationale" — and wait for a "GO" or specific-line edit before proceeding.

This gate is not brand-specific and does not get relaxed for a newly onboarded brand's first punchlist pass, even though there may be more items to sign off at once. The saved searches are production infrastructure regardless of how new the brand build is; a human stays on every go/no-go decision.

### Step 5 — push the edit

`listening_update_search` is a **full replace on name + query**, not a patch. Send the entire updated boolean string. Preserve:

- The exact search name (unless renaming intentionally)
- `case_sensitivity: "no"` unless the search was already `hybrid` or `yes`
- The `type: "boolean"` shape
- All existing `AND NOT`, `AND NOT from:`, and country-exclusion clauses (unless the fix explicitly removes them)

### Step 6 — filter-reset warning

After the API push, tell the operator: **"The Explore UI filter panel may need a manual reset for the new boolean to take full effect."** This is a known drift issue between API-pushed booleans and the UI's cached filter state.

### Step 7 — validation refresh

Immediately after all sign-off fixes are pushed, run a validation refresh (via `trendblender-refresh`) and produce a per-search verdict:

- **WIN** — noise cluster is gone, signal is preserved, volume is healthy
- **PARTIAL** — noise cluster is gone but signal has dropped (over-tightened; needs loosening)
- **NO CHANGE** — the fix didn't land; investigate whether UI filters were reset
- **OVER-TIGHTENED** — search has dropped to near-zero; propose loosen patch on next round

Log the verdict against each search in that brand's round-history file. If PARTIAL or OVER-TIGHTENED, propose the loosen patch and go back to Step 4 for sign-off.

## Deprecation criteria

Do not iterate past these limits — deprecate instead:

- **Four consecutive scheduled refreshes at zero returns.** Rebuild from intent, don't patch.
- **Three consecutive refreshes where more than 70% of content is off-territory.** The anchor is wrong.
- **Boolean has grown past ~4 kB with layered NOT clauses.** Explore starts freezing.

When deprecating: delete the search entirely OR rename with a `zz_` prefix to remove it from scheduled refreshes while keeping it for reference.

## The fix isn't real until brand-config.json says so

`brand-config.json` is the persisted artifact of record for pillar state, not the punchlist files (those are working notes for the operator/session). Whenever a punchlist action changes a pillar's durable state, write it back into that brand's `brand-config.json` immediately, not just into the punchlist/round-history notes:

- **Deprecating a pillar** — set that pillar's `status` to `"deprecated"` in `pillars[]`. If it's being fully replaced rather than paused, consider whether a new pillar entry is warranted instead of resurrecting the old one.
- **New or replaced saved search** — write the new search ID into that pillar's `savedSearchId` field. A pillar with a stale or null `savedSearchId` after a fix has landed is a config that's drifted from reality.
- **Reactivating a punchlist item** — if a pillar's `status` was `"punchlist"` and the fix validated as WIN, set it back to `"active"`.

Treat a punchlist round as incomplete — even after a WIN verdict — until `brand-config.json` reflects the outcome. A fix that only lives in `round-history.md` will be silently lost the next time the brand is rebuilt from its config.

## Reference material bundled

- **`references/current-punchlist-TEMPLATE.md`** — Starter template for the live punchlist state carried over between sessions. Copy into a brand's own working file (e.g. alongside its `brand-config.json`) and update at the end of every refresh; don't edit the template in place with real brand data.
- **`references/round-history-TEMPLATE.md`** — Starter template for logging every round's fixes with before/after and validation verdicts. Same copy-don't-edit convention as above.

## Related skills

- **`meltwater-boolean`** — the full boolean operator reference and recipe library. Loaded automatically when this skill is active; don't duplicate its recipes here.
- **`trendblender-refresh`** — used for validation refreshes after any push.
