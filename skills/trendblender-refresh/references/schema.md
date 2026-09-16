# Trend Record Schema Reference

The exact shape `dashboard/trendjack.html` expects, generic to any brand built from this skeleton. Ground truth is `schema/trend-record.schema.json` at the repo root — this doc is a field-by-field walkthrough of it, plus the failure modes that break the UI silently. If this doc and the JSON Schema ever disagree, the JSON Schema wins.

## Global structure

This is written to disk as a single file, `trends_data.js` (not `trends_<brandKey>.js` — see the note below), and registers into a single aggregated global, keyed by `brand.id` from `brand-config.json`:

```js
window.TRENDS_DATA["<brandKey>"] = { ...trend-record object... };
```

**`brand.id` is a lowercase-hyphen slug** (e.g. `"acme-clean"`), so `window.TRENDS_DATA["<brandKey>"]` bracket notation is mandatory. `window.TRENDS_DATA.<brandKey>` (dot notation) is invalid JavaScript the moment the slug contains a hyphen — it will throw or silently parse as something else, and the dashboard falls back to mock data with an amber "Mock data" indicator. This has been the single highest-frequency source of drift historically; treat it as non-negotiable.

**On-disk filename is always `trends_data.js`, not `trends_<brandKey>.js`.** The dashboard's `<script src="trends_data.js">` tag is fixed (one brand per plugin build, so the HTML never needs per-brand editing) — only the object key inside the file (`window.TRENDS_DATA["<brandKey>"]`) varies by brand. Writing the brand-specific data to a file literally named `trends_<brandKey>.js` will not be loaded by the dashboard at all.

## The top-level trend-record object

```js
{
  "generated_at": "2026-09-16T09:15:00+01:00",   // ISO-8601, prefer brand-local time with offset
  "source_pillars": [                             // optional but recommended
    { "id": "pillar-id", "name": "Pillar label", "savedSearchId": "12345678",
      "status": "clean" }                         // clean|mixed|noisy|broken-mostly-noise|silent-content-farm-only|silent
  ],
  "data_quality_notes": [],                       // optional; internal/operator-facing only, never client-facing
  "trends": [ /* array of trend objects, see below */ ]
}
```

`source_pillars[].status` is the real, numbers-backed read from `unified_retrieval_statistics_retrieval_tool` for that pillar this refresh — not a subjective vibe. Use it in the operator report (Step 7 of SKILL.md), and consider recording it here too so the data quality history is inspectable later.

## The trend object — every field

```js
{
  "id": "acme-clean-1",                      // string, stable per-brand identifier, format <brandKey>-<n>
  "name": "Client-facing trend title",       // string, NO pipeline jargon (see below)
  "summary": "One-sentence analyst context",
  "social": "HIGH",                          // one of: HIGH | MEDIUM | LOW
  "news":   "LOW",                           // one of: HIGH | MEDIUM | LOW
  "social_count": 12345,                     // optional integer, raw mention count
  "news_count":   234,                       // optional integer
  "momentum": "rising",                      // one of: emerging | rising | peaked | declining
  "scores": {                                // object with all 5 fixed keys, all 1-10 integer
    "topicFit":              9,
    "audiencePerspective":   9,
    "geoTiming":             8,
    "competitiveWhitespace": 7,
    "creativeStretch":       2
  },
  "activationMatch": "Guest-Ready Hosting",  // string or null; must exactly match a brand-config.json activations[].name
  "source": "category",                      // "category" | "adjacent"
  "posts": [                                 // array, at least one entry
    {
      "text":     "The actual post text or article headline",
      "author":   "@handle or Source Name",
      "platform": "TikTok",                  // TikTok | Instagram | X | Facebook | YouTube | Reddit | News | Social
      "url":      "https://…",               // real URL from the document-retrieval tool; omit if none returned
      "views":    12345                      // optional integer
    }
  ],
  "hashtags": []                             // optional string array
}
```

## Field notes

### `id`
Format `<brandKey>-<n>`, stable across refreshes for the UI's list-key stability. When a trend from a prior refresh is confirmed still active (see the cross-refresh dedup test in `clustering-judgment-checklist.md`), carry its `id` forward and update its fields rather than minting a new one.

### `name`
Client-facing trend title. The single highest-frequency source of schema drift historically.

**FORBIDDEN in `name`** — this is enforced by `scripts/validate_trends.py`, which derives the forbidden set from two places:
- A fixed generic pipeline-jargon list: "leading", "surfacing", "candidate", "search", "pillar", "cluster", "trending topic", "trend:"
- This brand's own `pillars[].id` and `pillars[].name` (lowercased, and a hyphen-joined `<BrandName>-<PillarName>` form) — so leaking a real pillar label always fails validation, for any brand, without hardcoding brand-specific strings into the validator
- Any raw numeric string 6+ digits long (a saved-search ID)

Rewrite anything that trips this as a real client-facing title before saving. Example: a candidate internally tracked as "leading pillar-hosting-prep cluster" should be written out as something like `"Guest-ready hosting hacks trending ahead of the long weekend"`.

### `summary`
One sentence of analyst context: why this matters, what activation it maps to, what the timing angle is.

### `social` / `news`
HIGH/MEDIUM/LOW buckets, not numeric — set these from the real statistics-tool output, not intuition:
- HIGH social = unmissable in-feed for the target audience this pillar covers
- MEDIUM social = discoverable if you're paying attention
- LOW social = niche or emerging
- HIGH news = mainstream press pickup
- LOW news = social-only

### `momentum`
Only these four values render correctly on the dashboard. Anything else (`steady`, `peaking`, `holding`, `flat`) silently falls back to a default rendering that doesn't match intent.
- `emerging` — first-week signal, unclear whether it holds
- `rising` — consistent period-over-period growth within the retention window
- `peaked` — hit its high, holding rather than growing
- `declining` — past peak, fading

### `scores`
All five keys, always, on a 1–10 integer scale. These five names are fixed by the dashboard's rendering code and `scoring.dimensions` in brand-config.json — never brand-configurable, never renamed. The dashboard's weighted-score formula is:

```
weighted = w_topicFit*topicFit + w_audiencePerspective*audiencePerspective + w_geoTiming*geoTiming
         + w_competitiveWhitespace*competitiveWhitespace + w_creativeStretch*creativeStretch
```

with weights from `brand-config.json`'s `scoring.weights`. **Do not invent alternative key names** (`brandFit`, `cultureHeat`, `activationSpeed`, `riskLevel`, `reachPotential`, etc.) — any key drift renders that trend's score column as `NaN` on the dashboard, and `validate_trends.py` will fail it as a hard error (exact key-set match required, not superset/subset).

Rough interpretation guide, evaluated against the specific brand's `territory.description`, `audienceSegments[]`, and `activations[]` — never against a generic notion of "on brand":
- **`topicFit`** — how well the trend maps to this brand's territory (10 = textbook activation match)
- **`audiencePerspective`** — how well the trend's audience aligns with this brand's audience segments (10 = bullseye)
- **`geoTiming`** — geographic and temporal relevance right now (10 = brand's market, this week, culturally live)
- **`competitiveWhitespace`** — how much room to move (10 = uncontested by competitors; 1 = fully saturated)
- **`creativeStretch`** — how much creative risk/originality required (10 = brand-defining stretch; 1 = safe evergreen)

### `activationMatch`
Must exactly equal one `activations[].name` from `brand-config.json`, or `null`. `null` is correct and expected for a trend that's on-territory but doesn't map cleanly to a named activation — never invent an activation name to fill the field.

### `source`
`"category"` for hits sourced from one of the brand's dedicated pillar searches. `"adjacent"` for hits from a broader lifestyle/audience-adjacent pillar, if the brand has one configured with a looser `scope`.

### `posts`
At least one example post/article evidencing the trend. Every post requires `text`, `author`, `platform`. `url` is optional but should be populated whenever `unified_retrieval_document_retrieval_tool` returned one — the dashboard renders a "View ↗" link when present. **Never fabricate a `url`.** If the tool didn't return one for a given post, omit the field entirely rather than guessing or constructing one from a handle/platform.

### `views`
Integer view count where available from `social_metrics` on the retrieved document. Omit when unknown — don't estimate.

## The morning_brief.js structure

Separate file, separate schema (`schema/morning-brief.schema.json`), produced by the `trendblender-morning-brief` skill from the trends this skill just wrote:

```js
const MORNING_BRIEF = {
  generated_at: "2026-09-16T08:15:00Z",              // ISO-8601 UTC
  date: "2026-09-16",                                // YYYY-MM-DD, brand-local
  generated_for: ["<brandKey>"],
  bullets: [                                          // EXACTLY four, in this exact order
    { kind: "strongest_signal",    label: "Strongest signal",              title: "…", body: "…", brand_relevance: ["<brandKey>"] },
    { kind: "earned_media",        label: "Earned-media moment",           title: "…", body: "…", brand_relevance: ["<brandKey>"] },
    { kind: "creator_opportunity", label: "Most actionable creator angle", title: "…", body: "…", brand_relevance: ["<brandKey>"] },
    { kind: "time_sensitive",      label: "Time-sensitive — act this week",title: "…", body: "…", brand_relevance: ["<brandKey>"] }
  ]
};
window.MORNING_BRIEF = MORNING_BRIEF;
```

## Common schema-drift mistakes to avoid

- **Global name drift** — must be `window.TRENDS_DATA["<brandKey>"]` bracket notation. Never `window.<BRANDKEY>_TRENDS`, never dot notation on a hyphenated slug.
- **Score-key drift** — exactly the five fixed keys, no more, no fewer, no renames.
- **Momentum drift** — only the four listed values.
- **URL fabrication** — omit rather than invent.
- **Loose JS instead of strict JSON** — the object literal after `=` must parse with `json.loads`: double-quoted keys/strings only, no trailing commas, no comments, no unquoted identifiers. It's fine that the surrounding file is `.js`; the literal itself must be JSON.
- **Inventing `activationMatch`** — must be an exact string match to `brand-config.json`'s `activations[].name`, or `null`.

## Where the files live

Flat directory alongside the dashboard, typically the repo root or a brand build's output folder:

```
trends_data.js            (registers window.TRENDS_DATA["<brandKey>"] internally)
morning_brief.js
dashboard/trendjack.html   (loads the above via <script> tags)
```
