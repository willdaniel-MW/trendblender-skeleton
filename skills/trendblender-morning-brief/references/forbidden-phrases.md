# Forbidden Phrases — Morning Brief

Audit against this list before writing `morning_brief.js`. None of the following may appear in `title` or `body`, for any brand.

## Pipeline jargon (generic — applies to every brand)

- "leading", "surfacing", "candidate", "search", "pillar", "cluster"
- "trending topic", "trend:"
- "TrendBlender", "the pipeline", "the refresh"
- "boolean", "boolean fix", "punchlist round", "Round N boolean"
- "punchlist", "punch list"
- "schema", "the schema", "brand-config", "brand config"
- "Mira", "MCP", "connector", "saved search", "savedSearchId"

## Raw IDs (generic — applies to every brand)

- Any raw Meltwater search ID (a bare 6+ digit number in a trend name or brief title is almost always a leaked search ID, not a real number the client would recognize)
- Any `<brandKey>-<n>` trend record id (e.g. `acme-clean-7`)

## Pillar names and ids — DERIVE THIS PER BRAND, DO NOT HARDCODE

This is the part that must be regenerated for every brand, not copied from a prior build. Before finalizing a brief:

1. Read that brand's `brand-config.json` and pull `pillars[].id` and `pillars[].name` for every pillar (any length list — don't assume a fixed count).
2. Build a check list from those values: each pillar's raw `id` (e.g. `bathroom-hacks`), its `name` in lowercase (e.g. `bathroom hacks`), and the hyphen/concatenated form some drafts fall into (e.g. `AcmeClean-BathroomHacks`).
3. Scan the drafted `title` and `body` text of every bullet against that brand-specific list. A pillar name is internal shorthand for a search territory, not a phrase a client-facing document should ever surface verbatim — even when it sounds like a plausible trend name.
4. If a bullet's content genuinely comes from that pillar, describe the *topic* in plain language instead of naming the pillar (e.g. write about "kitchen cleaning shortcuts", not `KitchenHacks`).

This replaces any fixed, hardcoded pillar list — a config with 6 pillars needs a 6-item check; a config with 40 needs a 40-item check. Never carry over a specific brand's pillar names into another brand's audit.

## Data-quality language (generic)

- "silent", "silent pillar", "returned zero"
- "off-territory", "bleeding", "leak"
- "over-tightened", "under-tightened"
- "deprecation", "deprecation candidate"
- "engagement farm", "spam filter"
- Anything about search noise or boolean maintenance

## Internal-only observations (generic)

- Anything about which pillars or searches are broken
- Anything naming the operator or internal team by role or name — operator context stays out of the client brief
- Anything describing a competitor's likely internal reaction or timeline in a way that reveals the client's own monitoring/escalation posture (the client doesn't need to see their own scouting strategy spelled out)

## Where these go instead

If the observation is important, add it to the **chat report** (the plain-text summary posted to the operator) OR to the `time_sensitive` bullet's body as a `Related for chat only (not brief):` line at the very end, which the brief-consuming script can strip before delivery to the client.

Example correct usage (fictional demo brand — see `references/example-briefs.md`):

> **Body:** "…window closes with the festival's opening weekend. Related for chat only (not brief): the SurfaceShine-EcoSwap pillar's India bleed is still present — a boolean fix is now overdue; the ScentStory / QuickReset pillars have both reactivated this refresh."

The client-shipping version of the brief removes everything after `Related for chat only (not brief):`.
