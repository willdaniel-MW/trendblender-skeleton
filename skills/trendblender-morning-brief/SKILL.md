---
name: trendblender-morning-brief
description: "Write the client-facing four-bullet morning brief for a TrendBlender brand. Load this skill when the user says \"write the brief\", \"morning brief\", \"generate the brief\", \"client brief\", \"write the four bullets\", or automatically at the end of a TrendBlender refresh run (called by trendblender-refresh). Produces `morning_brief.js` (window.MORNING_BRIEF) with exactly four bullets: strongest_signal, earned_media, creator_opportunity, time_sensitive — the fixed contract in schema/morning-brief.schema.json. Reads the brand's own brand-config.json for voice, pillar names, and locale; never hardcodes any single brand's content."
---

# TrendBlender — Morning Brief

## What this brief is (and isn't)

`morning_brief.js` is a four-bullet daily briefing the brand's own comms/marketing team reads. It's the primary client-facing artefact of the pipeline — for every brand this skill runs against, not just one.

**In the brief:** things the client can act on — creator briefs to commission, PR moments to lean into, competitive windows closing, activation windows opening.

**NOT in the brief:** search-boolean drift, pillar deprecation reasoning, pipeline-mechanics observations, boolean punch-list items, competitive-intel that isn't actionable, MCP/tool outages. Those go to the operator via chat, never the client file.

## Read the brand's own config first

Before drafting, read that brand's `${CLAUDE_PLUGIN_ROOT}/brand-config.json` (validated against `${CLAUDE_PLUGIN_ROOT}/schema/brand-config.schema.json`) for:

- `brand.name`, `brand.essence`, `brand.archetype` — voice and positioning to write in.
- `activations[].name` — the ONLY valid values a trend's `activationMatch` may reference; when a bullet recommends an activation, name one of these exactly, never invent one.
- `pillars[].name` / `pillars[].id` — these must never leak into the brief (see forbidden-phrases check below). They're internal pipeline labels, not client vocabulary, regardless of how descriptive they sound.
- `identity.hashtags` — if the brand tracks specific campaign hashtags, they're fair game to reference in a bullet body.
- Any locale/spelling convention the brand or operator has set (see below) — this schema doesn't currently have a dedicated field for it, so confirm with the operator once per brand and note it in your working context; don't assume a default.

## The four required bullet kinds

Every brief has exactly four bullets, in this order, with these `kind` values (fixed by `schema/morning-brief.schema.json` — do not add, drop, reorder, or rename):

1. **`strongest_signal`** — the single strongest cross-brand or single-brand narrative the refresh has surfaced. Usually a multi-post cluster, ideally with a specific numeric anchor (view count, sentiment shift, geographic concentration). Ends with a recommended activation.
2. **`earned_media`** — a PR / trade-press moment the client can amplify with owned voices. Usually a news-pillar story or an authoritative external validation. Ends with recommended who-to-brief and what-to-say.
3. **`creator_opportunity`** — a specific unaffiliated (or affiliated-with-competitor) creator to brief this week. Named creator, view-count evidence, competitive-scouting-window rationale, brief language recommendation.
4. **`time_sensitive`** — the window that closes within 3–10 days. Usually cultural (a live event, holiday, or seasonal moment), competitive (a competitor launching within the same week), or news-cycle (a story with a short amplification runway).

## Schema

```js
const MORNING_BRIEF = {
  generated_at: "2026-07-08T21:45:00Z",              // ISO-8601 UTC
  date: "2026-07-08",                                // YYYY-MM-DD
  generated_for: ["acme-clean"],                     // brandKey(s) this brief covers
  bullets: [
    {
      kind: "strongest_signal",                       // one of the four, in this order
      label: "Strongest signal",                      // display label
      title: "Short, specific, action-implied headline (max ~30 words)",
      body: "180-260 word paragraph — dense, numeric anchors, named creators, recommended action, timeline. No line breaks inside.",
      brand_relevance: ["acme-clean"]                  // subset of generated_for
    }
    // ... three more bullets in the same shape
  ]
};

window.MORNING_BRIEF = MORNING_BRIEF;
```

Note `generated_for` is usually a single brandKey — one brief per brand build — but the schema allows more than one, so don't assume `[0]` is the only entry when reading it back.

## CRITICAL: the object literal must be strict JSON, not just valid JS

`morning_brief.js` looks like a JS file and will run fine in a browser with JS-style object syntax — but `scripts/validate_brief.py` extracts the `window.MORNING_BRIEF = {...};` assignment with a regex and parses it with Python's `json.loads`. That means the object literal itself must be **strict JSON**, even though the surrounding file is `.js`:

- Double-quoted keys and string values only — `kind: "strongest_signal"` not `kind: 'strongest_signal'`.
- No trailing commas after the last item in an array or object.
- No comments (`//` or `/* */`) inside the object literal.
- No JS-only conveniences — no template literals, no unquoted keys, no `undefined`.

This is a real, easy-to-miss drift risk: code that looks completely normal to write and would execute correctly in any browser will still fail `validate_brief.py` if it isn't strict JSON. Write the object as JSON first, then wrap it in the `const MORNING_BRIEF = ... ; window.MORNING_BRIEF = MORNING_BRIEF;` scaffolding — don't write loose JS and hope it happens to parse.

## Writing style

- **Specific over general.** Named creators, view counts, publication names, dates. "A creator's video landed at 294,000 views" not "there's strong entertaining content".
- **Action-implied.** Every bullet ends with a "recommended today" or "recommended this week" sentence that names who should brief whom and what to say.
- **Client-safe tone.** Never mention data-quality issues, boolean noise, or pipeline mechanics. If something is chat-only, put it in a `Related for chat only (not brief):` line at the end of the `time_sensitive` bullet's body.
- **Locale and spelling are brand-configured, not assumed.** The original build of this skill hardcoded UK spelling for a single UK-based client — that doesn't generalize. Confirm the operator's preferred locale/spelling convention once per brand (there is no dedicated schema field for it today) and write consistently to it. Don't default to US or UK spelling without asking.
- **Numeric anchors.** Every claim about scale gets a number.
- **Time-boxed recommendations.** "5-day window", "72 hours", "this week", "before the event closes" — never open-ended.

## Voice guidance

Write in the brand's own voice per `brand.archetype` and `brand.essence` from its `brand-config.json`: confident, specific, and culture-fluent, but calibrated to that brand's actual tone rather than a generic "punchy marketing" register. If the brand's pillar names reference specific cultural moments the client audience already tracks, you can assume that internal familiarity in the brief's *content* (e.g. referencing a seasonal event by name) — just never surface the pillar label itself (see forbidden-phrases).

## Assembly workflow

1. Read that brand's `${CLAUDE_PLUGIN_ROOT}/brand-config.json` for voice, activations, and pillar labels to avoid leaking.
2. Review `${CLAUDE_PLUGIN_ROOT}/dashboard/trends_data.js`, just produced by the refresh.
3. Identify the strongest narrative (usually the highest-view single post or the tightest multi-post consensus).
4. Draft the four bullets in order.
5. Verify: no forbidden phrases or leaked pillar ids/names (see `references/forbidden-phrases.md`), no raw search IDs, no pipeline jargon, correct locale convention, all four `kind` values present in the fixed order, the object literal is strict JSON.
6. Write to `${CLAUDE_PLUGIN_ROOT}/dashboard/morning_brief.js` (`window.MORNING_BRIEF = {...};`) — always this path, never the operator's current working directory, or `trendjack.html` won't find it.
7. Run `python3 ${CLAUDE_PLUGIN_ROOT}/scripts/validate_brief.py ${CLAUDE_PLUGIN_ROOT}/dashboard/morning_brief.js` and fix any reported errors before considering the brief done.
8. Report to the operator with a one-line summary of the four titles.

## Reference material bundled

- **`references/forbidden-phrases.md`** — Generic pipeline jargon that must never appear in the brief, plus instructions for deriving the brand-specific pillar-leak check from that brand's own `brand-config.json` rather than any hardcoded list.
- **`references/example-briefs.md`** — Worked example brief(s) using a fictional demo brand, for structure and tone reference. Never real client content.
