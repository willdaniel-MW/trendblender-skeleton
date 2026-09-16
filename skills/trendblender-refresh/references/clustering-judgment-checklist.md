# Clustering & Judgment Checklist

The deterministic validators (`scripts/validate_trends.py`, `scripts/validate_brief.py`) enforce **structure**: required fields, valid enums, exact score-key sets, id prefixing/uniqueness, no fabricated URLs, no leaked pipeline jargon. They are derived from `brand-config.json` so they work for any brand, but they cannot and do not judge:

- Whether two posts (possibly from different pillars, possibly from different refreshes) represent the **same** underlying real-world trend
- Whether a borderline post is **genuinely** off-territory for this specific brand, versus adjacent-but-usable
- Whether a trend **name reads well** to a client, beyond just not containing forbidden strings
- Whether a score is **honest** rather than inflated to make a thin refresh look fuller

Those are judgment calls. This skill has to make them fresh every refresh, using the numbered checks below, and this system does not guarantee it makes them the same way twice. Expect human review of the output — especially on a brand's first refresh, when pillars are freshly auto-drafted and not yet tuned.

## 1. Same-moment clustering test

For every pair of candidate posts/documents pulled this refresh, ask: **is this the same underlying cultural moment, described by different posts (possibly on different platforms, possibly surfaced by different pillars)?**

- Same moment → collapse into a single trend record. Use the highest-engagement post as the lead example, but keep 2–4 supporting posts in `posts[]` if they add real texture (different platform, different angle, a notably large account).
- A post can be evidence for **at most one** trend's identity, even if its content would also plausibly support a second candidate trend. Assign it to the trend it most centrally represents; don't double-count it into two trend records just because both pillars' searches happened to surface it.
- Different moments that merely share a keyword or hashtag are NOT the same trend — check for shared specifics (same product hack, same meme format, same event, same public figure), not just shared vocabulary.

## 2. Cross-pillar and cross-refresh dedup test

- **Cross-pillar (within this refresh):** if two different pillars' saved searches both surfaced the same moment, merge into one trend record and note which pillars contributed (informally, in your own working notes — `source` is still just `"category"` or `"adjacent"` for the primary pillar).
- **Cross-refresh:** `ops.retentionWindowDays` deliberately overlaps between consecutive refreshes (e.g. a 5-day window run daily overlaps 4 days with the prior run). A real trend that's still live is not a new trend just because it reappears in this window. If you have visibility into the prior `trends_data.js`, compare candidate trends against it by content, not just by name string:
  - Same moment, still growing → same `id`, update `momentum`/`scores`/`posts` in place.
  - Same moment, now fading → same `id`, update `momentum` to `peaked`/`declining`.
  - Genuinely new moment → new `id`, next available `<brandKey>-<n>`.

## 3. Reject-list gate — applied BEFORE scoring, not after

Run every surviving candidate against `brand-config.json`'s `rejectList[]` **before** you spend any effort scoring it. No score — however high `topicFit` or `creativeStretch` might look — rescues a candidate that matches a reject pattern. This ordering matters operationally: scoring first and rejecting after invites motivated reasoning ("but the score is a 9, surely it's fine"). Reject first, score only the survivors.

## 4. Self-critique pass before writing output

Once you have a scored shortlist, do one more full pass, out loud in your own reasoning, before writing `trends_data.js`:

- Re-read every surviving trend's `name`, `summary`, and lead post against `rejectList[]` one more time.
- Ask explicitly: **"would a skeptical brand manager reject this?"** — not "could I justify keeping it," but would someone whose job is protecting this brand's territory push back on seeing it in the file.
- If yes, either rewrite it (if the underlying signal is real but the framing/angle is the problem) or drop it (if the signal itself is off-territory).
- Only after this pass do you write the file and run the Step 5 validator.

---

## Worked example — fictional demo brand

**Brand:** *Little Whiskers* — a fictional independent pet-care brand (grain-free treats + enrichment toys for cats). Not a real client. Territory: cat owners who treat their cat's wellbeing/enrichment as a lifestyle interest, not just a chore. Reject list includes "dog-only content", "veterinary medical advice / medication discussion" (liability), and "graphic animal injury/death content".

### Raw candidate hits (pooled across two pillars: `cat-enrichment` and `pet-parent-lifestyle`)

1. **Post A** (TikTok, `cat-enrichment` pillar): a cat owner shows a DIY cardboard "puzzle box" feeder they built over a weekend, high engagement, comments full of other owners sharing their own builds.
2. **Post B** (Instagram, `cat-enrichment` pillar): a different owner's Reel of the same cardboard puzzle-feeder trend, using the same audio, posted two days after Post A.
3. **Post C** (X, `pet-parent-lifestyle` pillar): a viral thread about a cat that needed emergency surgery after eating a foreign object, with graphic photos, high reach.
4. **Post D** (News, `pet-parent-lifestyle` pillar): a mainstream pet-lifestyle outlet's roundup article, "5 boredom-busting DIY cat toys," which name-checks the same cardboard puzzle-feeder trend and links back to posts like A and B.

### Applying the checklist

1. **Same-moment clustering:** Posts A, B, and D are all the same underlying moment (DIY puzzle-feeder trend) — different platforms, different specific builds, but the same cultural moment. Collapse into one candidate trend. Post C is a different moment entirely (a medical emergency story), not related to the feeder trend — it stays separate for now.
2. **Cross-pillar dedup:** the feeder moment was surfaced by the `cat-enrichment` pillar (A, B) and independently corroborated by the `pet-parent-lifestyle` pillar (D, the news roundup). That's a merge, not two trends — one trend record, `source: "category"` (its primary pillar), with A, B, D all eligible as supporting posts (use the highest-engagement of A/B as lead, keep D as the news corroboration since it also lifts the `news` bucket to something above LOW).
3. **Reject-list gate, applied first:** Post C (surgery thread with graphic injury photos) is checked against `rejectList` before any scoring effort — it matches "graphic animal injury/death content" directly. Reject it outright. It never gets scored, and it does not become a trend record.
4. **Scoring the survivor** (the puzzle-feeder trend) against Little Whiskers' territory/audience/activations: high `topicFit` (textbook enrichment content), high `audiencePerspective` (exactly the lifestyle-not-chore audience), decent `geoTiming` (evergreen rather than dated, so mid-range), likely lower `competitiveWhitespace` if several pet brands already have DIY-toy content out, and low-to-mid `creativeStretch` since DIY feeder content is a well-worn format for this category.
5. **Self-critique pass:** re-reading the merged puzzle-feeder trend against `rejectList` — no dog-only content, no medical advice, no graphic content. A skeptical brand manager would not reject it. It ships.

### Resulting trend records

```js
window.TRENDS_DATA["little-whiskers"] = {
  "generated_at": "2026-09-16T09:15:00+01:00",
  "source_pillars": [
    { "id": "cat-enrichment", "name": "Cat Enrichment", "savedSearchId": 40010203, "status": "clean" },
    { "id": "pet-parent-lifestyle", "name": "Pet Parent Lifestyle", "savedSearchId": 40010204, "status": "mixed" }
  ],
  "data_quality_notes": [
    "One candidate (viral surgery/injury thread) rejected pre-scoring per rejectList: graphic animal injury content."
  ],
  "trends": [
    {
      "id": "little-whiskers-1",
      "name": "DIY cardboard puzzle-feeders are having a moment with cat owners",
      "summary": "A home-built enrichment feeder format is spreading across TikTok/Instagram and just got picked up by a mainstream pet-lifestyle outlet, giving it both social traction and earned-media credibility.",
      "social": "HIGH",
      "news": "MEDIUM",
      "momentum": "rising",
      "scores": {
        "topicFit": 9,
        "audiencePerspective": 9,
        "geoTiming": 6,
        "competitiveWhitespace": 5,
        "creativeStretch": 4
      },
      "activationMatch": "Enrichment Made Easy",
      "source": "category",
      "posts": [
        {
          "text": "built my cat a $2 puzzle box out of a cereal box and she's obsessed",
          "author": "@example_cat_owner",
          "platform": "TikTok",
          "url": "https://example.com/tiktok/placeholder-1",
          "views": 184000
        },
        {
          "text": "5 boredom-busting DIY cat toys your cat will actually use",
          "author": "Example Pet Lifestyle Weekly",
          "platform": "News",
          "url": "https://example.com/news/placeholder-1"
        }
      ],
      "hashtags": ["#catenrichment", "#DIYcattoy"]
    }
  ]
};
```

Note the rejected surgery thread never appears anywhere in the output file — not as a dropped trend, not as a low-scored one. It only shows up in `data_quality_notes` (internal) and in the Step 7 operator chat report, never in client-facing content.

All names, handles, and URLs above are placeholders for illustration — never carry placeholder URLs like `https://example.com/...` into a real run. A real refresh only writes `url` values actually returned by `unified_retrieval_document_retrieval_tool`.
