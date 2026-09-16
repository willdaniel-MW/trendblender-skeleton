# Fetch Tools Reference

Concise, confirmed-working reference for the three retrieval tools this pipeline touches. Two run at refresh time (this skill); one runs at onboarding time only (a separate skill) and is documented here for context so a fresh session isn't guessing about how a pillar's `savedSearchId` came to exist.

These tools are typically deferred — load with `ToolSearch` (e.g. `select:mcp__…__unified_retrieval_statistics_retrieval_tool,mcp__…__unified_retrieval_document_retrieval_tool`) before calling them.

## `unified_retrieval_query_gen_tool` — onboarding time only, NOT called by this skill

Used by the brand-onboarding skill to turn a pillar's plain-English `description` into a draft Meltwater boolean. The resulting boolean is then persisted as a real saved search via `listening_create_search`, and the returned search ID is written into `brand-config.json`'s `pillars[].savedSearchId`.

By the time `trendblender-refresh` runs, this step should already be done for every active pillar. If you find an active pillar with `savedSearchId: null` mid-refresh, that's a precondition failure (see SKILL.md Preconditions) — skip the pillar and flag it, don't call this tool yourself as a workaround. Onboarding and refresh are deliberately separate skills so a refresh never silently mints new searches.

For boolean syntax and noise-reduction patterns once a draft needs tuning, see the `meltwater-boolean` skill.

## `unified_retrieval_statistics_retrieval_tool` — refresh time, call #1 per pillar

Purpose: a real volume/sentiment/platform breakdown for a pillar's saved search over the retention window. This is what replaces a subjective "this pillar feels clean/noisy" read with actual numbers — use the output to set `source_pillars[].status` and the operator-report health read in SKILL.md Step 7.

Confirmed-working parameters:

| Param | Required | Notes |
|---|---|---|
| `query` | Yes | Use `"*"` for saved-search-only retrieval (the saved search already defines the topic). |
| `savedSearchIds` | No, but use it here | Array of int — pass `[<pillar.savedSearchId>]` (brand-config.json stores this as an integer already, no cast needed). |
| `startDate` / `endDate` | No, but use it here | `YYYY-MM-DD`. Derive from `ops.retentionWindowDays`: `startDate = today - retentionWindowDays`, `endDate = today`. |
| `platforms` | No | Leave unset unless a pillar's `scope` requires narrowing beyond what the saved search already does. |
| `sentiment` | No | Leave unset for a full breakdown; the tool returns the sentiment split itself. |
| `languages` | No | Leave unset unless the brand's territory is language-restricted beyond what the saved search encodes. |
| `countries` | No | Leave unset by default — see the `meltwater-boolean` skill's country-filter caveat; country tagging under-represents social content. |

Call shape:

```json
{
  "query": "*",
  "savedSearchIds": [12345678],
  "startDate": "2026-09-09",
  "endDate": "2026-09-16"
}
```

Use the response's volume/sentiment/platform figures directly in the operator report — don't paraphrase them into vague terms like "seems active."

## `unified_retrieval_document_retrieval_tool` — refresh time, call #2 per pillar

Purpose: the actual documents (posts/articles) that become trend evidence and `posts[]` entries. This replaces the original pipeline's freeform "give me the top trending stories" prompt with real, structured documents.

Confirmed-working parameters:

| Param | Required | Notes |
|---|---|---|
| `query` | Yes | **Plain-English semantic description only — this param does NOT support boolean operators (AND/OR/NOT).** Pass the pillar's `description` field from brand-config.json verbatim or lightly paraphrased. The saved search (via `savedSearchIds`) does the actual topical filtering; `query` here just biases relevance/ranking within it. |
| `savedSearchIds` | No, but use it here | Array of int — pass `[<pillar.savedSearchId>]` to scope retrieval to this pillar. |
| `sortBy` | No, but use it here | Set to `"engagement"` so the highest-traction documents come back first — this is what replaces the original's "top trending" framing. |
| `limit` | No, but use it here | Hard-cap at `ops.maxDocumentsPerPillar`. Never raise this per-call to compensate for a thin pillar — a thin pillar is itself a signal (feed it to the noisy/silent read in the operator report, and potentially the boolean-punchlist skill), not something to paper over with a bigger pull. |
| `startDate` / `endDate` | No, but use it here | Same retention window as the statistics call, for consistency. |

Call shape:

```json
{
  "query": "DIY enrichment activities and toys cat owners are making or sharing at home",
  "savedSearchIds": [12345678],
  "sortBy": "engagement",
  "limit": 15,
  "startDate": "2026-09-09",
  "endDate": "2026-09-16"
}
```

### Return shape — what's actually usable

Each returned document has been confirmed (by live testing) to carry:

- `author.handle` / `author.name` — map to `posts[].author` (prefer `@handle` where the platform uses handles, else `name`)
- `platform` — map to `posts[].platform`, but validate against the fixed enum first (`TikTok | Instagram | X | Facebook | YouTube | Reddit | News | Social`) — remap anything the tool returns in a different casing/spelling (e.g. `"twitter"` → `"X"`) before writing it out, since `validate_trends.py` enforces the exact enum.
- `url` — map to `posts[].url` **only when present**. If a given document has no `url` field or it's empty, omit `posts[].url` entirely for that post. Never construct one from the handle/platform/date.
- `content` — the post text/body, maps to `posts[].text`.
- `date` — useful for momentum judgment (is this document from early or late in the retention window) but not itself a schema field.
- `social_metrics` (engagement/reach/views/shares) — use `views` (or the closest available count) for `posts[].views` if present; omit if not returned. Use engagement/reach figures to help judge `social`/`news` bucket levels and `momentum`, but don't invent a `social_count`/`news_count` figure the tool didn't actually give you.

### Common mistakes to avoid

- Passing a boolean string (`"cat AND enrichment NOT dog"`) into `query` — it will not filter as expected; boolean logic belongs in the saved search itself, set up at onboarding time.
- Raising `limit` past `ops.maxDocumentsPerPillar` to get more candidates — this is an explicit cost cap in brand-config.json, not a soft default.
- Fabricating a `url`, `views`, or `social_count`/`news_count` value when the tool didn't return one.
- Skipping the statistics call and inferring pillar health purely from the documents you happened to retrieve — the statistics tool is the actual volume/sentiment source of truth, independent of the engagement-sorted sample the document tool returns.
