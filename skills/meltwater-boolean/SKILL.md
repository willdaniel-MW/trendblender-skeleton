---
name: meltwater-boolean
description: Reference for writing, refining and troubleshooting Meltwater boolean search queries — used when creating, editing, or debugging Meltwater Listening saved searches (via the Mira API, the create_search / update_search MCP tools, or the Meltwater Explore UI). Load this when the task touches Meltwater Boolean strings, saved searches, source filtering, or noise reduction in social listening.
---

# Meltwater Boolean Reference

A condensed operator library and best-practice recipes for writing Meltwater Boolean queries. Source: official Meltwater Boolean Library, extended with operational lessons from the TrendBlender pipeline.

## When this applies

Use this skill whenever you are:
- Authoring a new Meltwater saved search (via `create_search` MCP tool or the Explore UI)
- Refining an existing saved search via `update_search`
- Diagnosing why a search is returning too much noise or zero results
- Creating paired searches (e.g. social + news, social-only + news-only)
- Building queries that need to filter by influencer thresholds, content quality, or source type

## Core operators

| Operator | What it does | Example |
|---|---|---|
| `AND` | All terms must appear | `atlantic AND "sailboat racing"` |
| `OR` | Any term may appear | `sailing OR sailboat` |
| `NOT` | Excludes documents containing the term | `sailboat NOT race` |
| `*` | Wildcard (any characters) | `sail*` matches sailing, sailboat |
| `?` | Single-character wildcard | `sen?` matches sent, send |
| `"…"` | Exact phrase match | `"cleaning hacks"` |
| `\` | Escape special characters | `E\*trade` matches the literal "E*trade" |
| `{N}`, `{N,M}` | Word frequency: appears N (or N to M) times | `sailboat {5}` requires 5 mentions |
| `^N` | Boost: weight a term higher in scoring | `race AND (yacht^2 OR sailing^0.5)` |
| `XNOT` | Exclude only in specific combinations (vs absolute NOT) | `bill XNOT "bill gates"` |

## Critical noise-reduction operators

These are the highest-leverage filters for cutting noise in trend / brand monitoring work. **Apply by default** to any search whose purpose is finding genuine social signal:

- **`postType:og`** — original posts only. Strips retweets, quoted tweets, replies. Massive noise reduction on X/Reddit/Facebook.
- **`authorHuman:true`** — only posts from human-classified accounts. Excludes brand accounts, company handles, news bot accounts. Use when looking for organic conversation.
- **`spam:false`** — built-in spam/promotional content filter. Removes affiliate-link spam, sales/coupon promo, Pinterest pin spam. **Does NOT catch AI-generated engagement-farm content** — see the AI-storytime recipe below.
- **`nsfw:false`** — built-in NSFW filter (text + image based).
- **`language:en`** — restrict to English content. **Prefer this over country filters** (see Country Caveat below).

These four together typically remove 70–90% of search volume but leave the highest-quality signal. Combine with topic terms via AND.

## Influencer filter (inline)

`followers >10000` works *inside* the boolean query string. You don't need to set follower thresholds via the UI — they go in the search itself.

- `followers >10000` — at least 10K followers (mid-tier and above)
- `followers >50000` — mid-tier influencer cutoff
- `followers >100000` — macro influencers only
- **Syntax note**: when using inequality operators, **omit the colon**. The correct form is `followers >10000` (with space), NOT `followers:>10000`. The colon is reserved for exact-equality: `followers:100000` matches accounts with exactly 100,000 followers.
- Same pattern applies to `likes`, `shares`, `reach`, `authority` — use a space before the comparison: `likes >5000`, `reach >=10000`, `authority >=5`.
- Pair with `authorVerifiedType:individual` for verified blue-tick humans only, or `verified:true` for any verified handle.

## Country caveat (important) — and content-based geo blocks

**Don't use `country:gb` (or similar) as a primary geographic filter on social searches.** Many social platforms — Reddit notably — don't provide country tags via their API, so country-tagged content is a small and unrepresentative subset. Filtering with `country:` will silently drop most relevant social content.

Safer alternatives:
- `language:en` — covers most UK/US/AU/CA content without dropping untagged posts
- `socialType:` source filtering for platforms where geography is implicit (e.g. UK-specific subreddits or X accounts)
- Source filtering via UI when country is critical (more reliable than the boolean operator)

`country:` is fine for news searches where outlet country is usually known. Just not for social.

**When cross-border content still leaks through:** use **content-based geo blocks**. `country:in` will silently miss India-origin posts that have no country tag, but blocking market-specific brand names, currencies and handles catches them reliably. Reusable pattern for India-market suppression (extend the same approach to LatAm / MENA / Philippines etc):

```
AND NOT ("Lizol" OR "Vim India" OR "Harpic India" OR "Domex" OR "Godrej Ezee")
AND NOT ("₹" OR "rupees" OR "lakh" OR "crore" OR "jugaad" OR "Punjab Kesari" OR "punjabkesari*")
AND NOT from:"punjabkesarijugaad"
```

Content-based geo blocks are dramatically more effective than country-code exclusions in every case we've measured.

## Source / platform operators

| Operator | Example | Notes |
|---|---|---|
| `socialType:` | `socialType:"tiktok"` | Lowercase. Values: `twitter`, `facebook`, `instagram`, `reddit`, `youtube`, `tiktok`, `kakaotalk`, `linevoom`, `social_blogs`, `social_comments`, `social_reviews`, `social_message_boards`, `podcasts` |
| `infoType:` | `infoType:"news"` | `news` / `social` / `broadcast` |
| `site:` | `site:"www.bbc.com"` | No `https://` prefix. `site:"*.bbc.*"` matches all BBC subdomains |
| `author:` | `author:"Yachting World"` | Author handle or name |
| `from:` | `from:"worldsailing"` | Posted by specific handle. Case sensitive. **Does NOT accept wildcards** — you must enumerate handles individually (see gotcha below). |
| `to:` | `to:"americascup"` | Lowercase only. Documents mentioning the handle |
| `mention:` | `mention:"yachtracinglife"` | Documents that @-mention this handle |
| `SourceName:` | `SourceName:"r/Boating"` | Specific subreddit, podcast, or publication |
| `title:` | `title:"Sailing the World"` | Match in title only |
| `content:` | `content:"George Mendonsa"` | Match in body only |
| `ingress:` | `ingress:"yacht race"` | Match in first paragraph only — great for ensuring topic is genuinely featured |

## Engagement & quality filters

| Operator | Example | Purpose |
|---|---|---|
| `likes>` | `sailing AND likes>5000` | Min like count |
| `shares>` | `sailing AND shares>500` | Min share/retweet count |
| `reach>=` | `reach>=10000` | News articles by audience reach |
| `enrichments.socialScores.tw_likes>` | `> 20` | More precise X likes filter |
| `enrichments.socialScores.fb_post_reactions>` | `> 20` | Facebook reactions |
| `authority>=5` | | Meltwater authority score |

## Proximity operators

| Operator | What it does | Example |
|---|---|---|
| `NEAR` | Within 4 words of each other (any order) | `sailboat NEAR racing` |
| `NEAR/N` | Within N words of each other | `sailboat NEAR/10 racing` |
| `ONEAR` | Within 4 words IN ORDER | `sailboat ONEAR racing` (sailboat then racing) |
| `ONEAR/N` | Within N words IN ORDER | `sailboat ONEAR/10 racing` |

Use for tight contextual matches when AND is too loose. Especially useful when generic terms might otherwise create false positives.

## Image / visual operators

| Operator | Example | Purpose |
|---|---|---|
| `imageText:` | `imageText:stop` (lowercase) | OCR on images |
| `imageEntity:` | `imageEntity:"Elon Musk"` | Known entity (logo or celebrity) |
| `imageObject:` | `imageObject:dog` | Object recognition |
| `imageScene:` | `imageScene:beach` | Scene recognition |
| `imageEmotion:` | `imageEmotion:j` (j=joy, a=anger, u=unknown) | Detected emotion |
| `attachmentType:` | `attachmentType:image` or `:video` or `:reel` | Posts with attachment of type |

## Common syntax gotchas

- **Colons in keywords** — wrap in quotes: `"Euronext:ROTH"`, otherwise the colon is read as an operator.
- **Backslash escapes literal characters** — `E\*trade` to match the literal E*trade rather than E followed by anything.
- **Case sensitivity:**
  - Most operators are case-insensitive (AND, OR, hashtag matching).
  - `caseSensitive:(Apple)` to enforce case — useful for distinguishing "Apple" the brand from "apple" the fruit.
  - `from:` is case-sensitive; `to:` and `mention:` are lowercase-only.
- **Country/language codes are lowercase**: `country:us`, `language:en`. Use 2- or 3-letter ISO codes.
- **`site:` and `containsLink:` exclude the protocol** — never include `https://` or `http://`.
- **OR inside a single operator (March 2024 feature)** — `ingress:("Solar energy" OR "Solar power")` works. No need to repeat the operator for each phrase.
- **`from:` does not accept wildcards.** You cannot block a handle family with `NOT from:"fabiosa.*"`. Enumerate individually:
  ```
  AND NOT from:"fabiosa.usa"
  AND NOT from:"fabiosa.canada"
  AND NOT from:"fabiosa.india"
  AND NOT from:"fabiosa.philippines"
  AND NOT from:"fabiosa.daily"
  AND NOT from:"fabiosa.belle"
  ```
- **Hashtag dual-index behaviour.** Meltwater indexes hashtags into both the `body.*` text fields AND a dedicated `body.contentTags` field. When adding hashtag NOTs, include both the `#tag` form and the plain-string form to cover both paths:
  ```
  AND NOT ("#GRWM" OR "GRWM")
  ```

## Standard search patterns

### Brand/topic monitoring (general)
```
( <brand or topic hashtags and keywords joined with OR> )
AND language:en
AND postType:og
AND authorHuman:true
AND spam:false
```

### Influencer-only feed (mid-tier+)
```
( <same territory as parent search> )
AND followers >10000
AND postType:og
AND authorHuman:true
AND spam:false
AND language:en
```

### News-only on the same territory
```
( <same hashtag/keyword bundle> )
AND infoType:"news"
```
Or simpler: create the search with `informationTypes:["news"]` set via the UI after creation.

### Paired social + news (for trend detection)
- Search A: combined social+news. Use for trend identification.
- Search B: news-only. Use to verify news mention counts per identified trend.
- Both share the same keyword/hashtag territory; only the `infoType` filter (or source filter set in the UI) differs.

### High-confidence "this is genuinely on topic" filter
Combine with `ingress:` to require the term in the first paragraph:
```
( body:"sustainable laundry" OR body:"eco fabric softener" )
AND ingress:( "laundry" OR "fabric care" )
```
Or use word frequency to ensure the term is featured, not just mentioned:
```
( "scent layering" {3} )
```

### AND-gate for over-loose hooks (idiomatic-phrase search anchors)

When the search hook is a common idiomatic phrase — "play on", "keep it real", "get dirty", "back on top" — no amount of NEAR tightening on the include side stops false positives; the phrase itself is too common. The fix is a **global AND-gate** that requires topical vocabulary to co-occur anywhere in the document:

```
(<existing include union — NEAR clauses + hashtag list>)
AND (
  "<topical noun 1>" OR "<topical noun 2>" OR "<topical noun 3>"
  OR "#topical_hashtag_1" OR "#topical_hashtag_2"
)
AND NOT (…)
```

Rules learned the hard way:
- **Include hashtags in the AND-gate list**, not just literal vocabulary. Fandom / community posts often speak in hashtags without repeating the effort/topic words in prose.
- **Include bare topical nouns** (e.g. `"grass"`), not just compound phrases (e.g. `"grass stain"`). Requiring compound phrases over-tightens dramatically.
- **Test on a validation refresh before assuming the gate is right.** A real first implementation of this pattern, on an idiomatic-phrase pillar, over-tightened to 3 docs in 48h; loosening bare nouns and hashtags recovered the search.

## Working with the create_search / update_search MCP tools

The MCP tools (`create_search`, `update_search`, `listening_create_search`, `listening_update_search`) accept `name` and `query` (with a `type: "boolean"`, `case_sensitivity`, and `boolean` string for boolean searches). They don't expose:
- Source-type filtering (e.g. "only Instagram + TikTok") — UI only
- Information-type filtering (social vs news vs broadcast scope) — UI only after creation
- Follower count filters set via the filters object — **but `followers:>N` inline in the boolean works**
- Language filter via the filters object — **but `language:en` inline works**

So as a rule of thumb: do everything you can via inline operators in the boolean query. Reach for the UI only when:
- Restricting `informationTypes` (the scope-flag — news vs social vs broadcast)
- Restricting source types beyond what `socialType:` covers
- Setting up complex universal filters that aren't expressible in the boolean

**Operational notes for the tools:**

- **`update_search` is a full replace on name + query, not a patch.** You always send the entire boolean string. Read the current search first with `get_search` (or `listening_get_search`), then modify, then push. Never assume you can send a delta.
- **UI filter state can drift after an API update.** After a boolean push, the Explore UI's filter-panel state can go stale — the user often needs to click "reset filters" for the new boolean to take full effect. If a validation refresh looks off, ask whether the filters were reset.
- **Boolean size ceiling ≈ 3–4 kB.** Beyond that, the Explore UI can freeze when loading the search. If your boolean approaches that limit, split the noise-reduction section into a companion combined-search rather than one giant expression.
- **"Not valid in your account" is often transient.** When `mira_search_media_news` returns this on a search you know exists, retry once before assuming a permissions issue. It's usually a session-state hiccup.
- **Include `include_runes: true`** on `get_search` when you want to inspect the compiled query (helpful for diagnosing why a search matches what it matches).

## Quick recipe library

**Reduce a noisy search by 80%:**
Append `AND postType:og AND authorHuman:true AND spam:false AND language:en` to the existing query.

**Turn any search into an influencer feed:**
Append `AND followers >10000` (or 50000 for mid-tier+, 100000 for macro).

**Exclude your own brand's content:**
`NOT author:"YourBrandHandle" NOT mention:"YourBrandHandle"` — but be careful, this also removes user mentions; usually you only want to exclude `from:` not mentions.

**Find content that talks about competitors:**
`( "Lenor" OR "Downy" OR "Snuggle" ) AND authorHuman:true AND postType:og`

**Find earliest signals of a hashtag's growth:**
`hashtag:"<tag>" AND followers <5000 AND postType:og` — small accounts using the tag are leading-indicator signals.

**Block AI-generated engagement-farm content (universal noise):**
`spam:false` does NOT catch AI-storytime / engagement-farm content. Add this block to any broad-anchor search:
```
AND NOT (
  "AI storytime" OR "AI-storytime" OR "storytime AI"
  OR "story of the husband" OR "story of the wife" OR "story of the driver"
  OR "welding hands" OR "welder father" OR "miracle moment"
  OR "prom dress used" OR "prom dress toilet"
  OR "fabiosa*"
)
AND NOT from:"fabiosa.usa"
AND NOT from:"fabiosa.canada"
AND NOT from:"fabiosa.india"
AND NOT from:"fabiosa.philippines"
AND NOT from:"fabiosa.daily"
AND NOT from:"fabiosa.belle"
```
These formats have become universal cross-brand noise categories — they surface anywhere with a broad enough anchor. Block them once in every top-of-funnel search.

**Block India-market content when country:in isn't landing:**
```
AND NOT ("Lizol" OR "Vim India" OR "Harpic India" OR "Domex" OR "Godrej Ezee")
AND NOT ("₹" OR "rupees" OR "lakh" OR "crore" OR "jugaad" OR "Punjab Kesari" OR "punjabkesari*")
AND NOT from:"punjabkesarijugaad"
```
Adapt the pattern for other markets that leak through despite `country:` exclusions.

## When to deprecate a saved search

Formal deprecation criteria (from repeated operational experience — iterating past this threshold wastes time):

- **Four or more consecutive scheduled refreshes at zero returns.** The search is structurally broken or the boolean has drifted past the actual content that exists. Rebuild from intent, don't patch.
- **Three consecutive refreshes where more than 70% of returned content is off-territory noise.** The anchor is fundamentally wrong for the topic; a boolean-tightening approach won't recover it.
- **Boolean has grown past ~4 kB with layered NOT clauses.** Explore starts freezing and future maintenance becomes exponentially harder. Rebuild leaner.

When deprecating, either:
- Delete the search entirely (freeing the pillar slot for a replacement), OR
- Move it to a "cold storage" naming convention (e.g. prefix with `zz_`) so it doesn't run on scheduled refreshes but stays available for reference.

## Verified status reference

- `verified:true` / `verified:false` — any verified handle (X)
- `authorVerifiedType:business` — gold tick (X)
- `authorVerifiedType:individual` — blue tick (X)
- `authorVerifiedType:government` — grey tick (X)

## Inequality operators

Used with: reach, authority, shares, follower count, like count, etc.
- `>` greater than
- `>=` greater than or equal
- `<` less than
- `<=` less than or equal
- *Note: use colon (`:`) without comparison sign for exact equality* — `followers:100000` matches exactly 100,000

## Things this skill does NOT cover

- Mira `ask` prompt engineering — this is about the saved search itself, not how you query it
- Klear / Engage / Media Relations product specifics — different APIs
- Saved search analytics (volume, sentiment breakdown) — different operation
