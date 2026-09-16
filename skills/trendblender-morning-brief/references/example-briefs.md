# Example Briefs — Worked Examples

These use a fictional demo brand, **"BrightBasin"** (a fictional home-care brand, `brand.id: "bright-basin"`, category: "kitchen & surface care") — invented for this skeleton, not a real client. Its fictional pillars for these examples: `quick-resets` ("QuickReset"), `eco-swaps` ("EcoSwap"), `scent-story` ("ScentStory"). Its fictional activation names: "Weekend Reset Challenge", "Scent Layering Kit Drop".

Use these to see structure, tone, and locale-neutral phrasing in practice — not as content to copy for a real brand.

## Example 1 — full four-bullet brief

```js
const MORNING_BRIEF = {
  "generated_at": "2026-09-15T07:10:00Z",
  "date": "2026-09-15",
  "generated_for": ["bright-basin"],
  "bullets": [
    {
      "kind": "strongest_signal",
      "label": "Strongest signal",
      "title": "A 20-second countertop reset clip has crossed 410,000 views in 36 hours",
      "body": "A single creator's before/after countertop reset video posted Saturday has pulled 410,000 views and 28,000 saves in 36 hours, well outside this account's normal range (typical post: 15,000-30,000 views). Top comments are asking what product she used and where to buy the caddy shown in frame. No brand mention yet, which is the opportunity: this is an organic format, not a paid placement, and it's still climbing. Recommended today: brief the social team to comment on the post offering the product list, and draft a same-format response video for the brand's own channel within 48 hours while the format is still fresh, tied to the Weekend Reset Challenge activation.",
      "brand_relevance": ["bright-basin"]
    },
    {
      "kind": "earned_media",
      "label": "Earned media",
      "title": "A regional lifestyle outlet named BrightBasin in a roundup of 'quiet luxury' cleaning brands",
      "body": "A mid-tier lifestyle publication (est. 480,000 monthly readers) published a roundup piece on Thursday titled '5 cleaning brands that make the chore look good,' naming BrightBasin third alongside two premium competitors. This is unpaid, unprompted editorial placement — a genuine third-party validation moment rather than a response to any outreach. The piece frames the brand as design-forward rather than purely functional, which lines up well with the eco-swap positioning. Recommended today: brief the PR lead to pitch the same writer a follow-up on the eco-swap range within the week, while the relationship and the article's framing are both still warm.",
      "brand_relevance": ["bright-basin"]
    },
    {
      "kind": "creator_opportunity",
      "label": "Creator opportunity",
      "title": "An unaffiliated home-organization creator with 210,000 followers is actively scouting eco-friendly swaps this month",
      "body": "This creator (210,000 followers, average 60,000 views per post) has posted three separate 'swapping to eco alternatives' videos in the last two weeks, none sponsored, and none yet featuring a surface-care brand specifically. Her audience skews toward the same 25-34 household-manager demographic BrightBasin already targets, and her engagement rate (6.2%) is well above platform average for this follower tier. A competitor has not yet reached out based on comment activity. Recommended this week: brief the influencer team to reach out with a no-pressure product send framed around the eco-swap range, before a competitor's scouting catches up to this creator's current momentum.",
      "brand_relevance": ["bright-basin"]
    },
    {
      "kind": "time_sensitive",
      "label": "Time-sensitive window",
      "title": "The back-to-school clean-slate moment closes in 6 days",
      "body": "Search and social interest in 'reset the house' and 'fresh start' framing typically peaks in the two weeks after schools reopen and drops off sharply after that; this year's window closes around September 21. Content published after that date reliably underperforms compared to the same format published inside the window. Recommended today: prioritize any remaining Weekend Reset Challenge content for publication within the next 6 days rather than holding it for a later date. Related for chat only (not brief): the ScentStory pillar has returned low-relevance results for the second refresh in a row and may need a boolean pass next round.",
      "brand_relevance": ["bright-basin"]
    }
  ]
};

window.MORNING_BRIEF = MORNING_BRIEF;
```

**What worked:** every bullet has a numeric anchor, a named specific (creator, publication, date), and a time-boxed action. The `time_sensitive` bullet's chat-only aside stays out of the client-visible content and correctly avoids naming the pillar in the main body — it only appears after the `Related for chat only (not brief):` marker.

## Example 2 — a weaker earned_media bullet and the fix

**Before (too vague, no anchor, leaks pipeline framing):**

> "Cleaning-adjacent conversation has been trending this week and there's a strong candidate surfacing in the news pillar. Recommended: consider outreach."

Problems: "trending", "candidate", and "pillar" are all forbidden pipeline jargon (see `references/forbidden-phrases.md`); there's no publication name, no reach number, and no time-boxed action.

**After:**

> "A national morning show segment on 'satisfying cleaning content' aired Tuesday and name-checked three viral cleaning formats without naming any brand — an open opportunity to be the brand associated with the format next time a producer books a similar segment. Recommended this week: brief the PR team to pitch a follow-up segment idea to the same producer within 5 days, while the segment is still being referenced in recap coverage."

This version has a concrete anchor (a specific segment, a day, a follow-up window) and reads as something a comms lead can act on immediately, with no internal-pipeline language.
