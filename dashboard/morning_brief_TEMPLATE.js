/*
 * TEMPLATE — morning_brief.js
 *
 * This is the exact shape a brand's daily morning brief must have to be loaded
 * by dashboard/trendjack.html as window.MORNING_BRIEF. It is validated against
 * schema/morning-brief.schema.json (strict JSON inside the assignment below —
 * double-quoted keys, no trailing commas, no comments in the real file).
 *
 * Always exactly 4 bullets, in this fixed order of "kind":
 *   1. strongest_signal      — the single highest-confidence trend right now
 *   2. earned_media          — a news/press angle worth knowing about
 *   3. creator_opportunity   — a specific influencer/creator angle
 *   4. time_sensitive        — something with a closing window (act now or miss it)
 *
 * generated_for lists the brandKey(s) this brief covers — for a single-brand
 * plugin build this is almost always a one-item array.
 *
 * Uses the same fictional demo brand as the other templates ("Bramblewick").
 */
window.MORNING_BRIEF = {
  "generated_at": "2026-01-15T22:03:00+00:00",
  "date": "2026-01-15",
  "generated_for": ["bramblewick"],
  "bullets": [
    {
      "kind": "strongest_signal",
      "label": "Strongest Signal",
      "title": "Parent-led ingredient-label swap videos are accelerating",
      "body": "Social volume on ingredient-label comparison videos is up sharply over the last 72 hours, driven by parent creators swapping lunchbox snacks. This sits directly inside Bramblewick's clean-label territory and the window is still open — no competitor snack brand has been tagged in the format yet.",
      "brand_relevance": ["bramblewick"]
    },
    {
      "kind": "earned_media",
      "label": "Earned Media",
      "title": "Local news coverage of ultra-processed food debate continues",
      "body": "A handful of regional outlets ran follow-up pieces on ultra-processed snack additives this week, keeping the clean-label conversation in the news cycle alongside the social trend. Low volume but useful supporting context for a press pitch.",
      "brand_relevance": ["bramblewick"]
    },
    {
      "kind": "creator_opportunity",
      "label": "Creator Opportunity",
      "title": "Mid-tier lunchbox creators are open to brand partnerships on this format",
      "body": "Several of the creators driving the label-swap trend are mid-tier (20k-80k followers) and have a track record of disclosed brand partnerships without losing engagement. Good fit for a fast-turnaround gifted-product outreach before the trend peaks.",
      "brand_relevance": ["bramblewick"]
    },
    {
      "kind": "time_sensitive",
      "label": "Time Sensitive",
      "title": "Back-to-school lunchbox content cycle closes within two weeks",
      "body": "Lunchbox-focused content naturally tapers off after the first few weeks of term. Any activation tied to the label-swap trend should brief and go live within the next 10-14 days to catch the remaining window.",
      "brand_relevance": ["bramblewick"]
    }
  ]
};
