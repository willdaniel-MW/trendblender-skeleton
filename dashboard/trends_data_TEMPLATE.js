/*
 * TEMPLATE — trends_data.js
 *
 * This is the exact shape a brand's live trends file must have to be loaded by
 * dashboard/trendjack.html as window.TRENDS_DATA. It is validated against
 * schema/trend-record.schema.json (strict JSON inside the assignment below —
 * double-quoted keys, no trailing commas, no comments in the real file).
 *
 * IMPORTANT — file naming vs. object key:
 *   - The refresh pipeline writes this brand's file to disk as trends_data.js
 *     (see the comment at the top of dashboard/trendjack.html for why: one
 *     brand per plugin build means the HTML never needs per-brand edits).
 *   - Inside that file, the object is still registered under the brand's own
 *     brandKey (window.TRENDS_DATA["<brandKey>"], bracket notation because the
 *     id contains hyphens) so the shape stays self-describing and portable if
 *     ever consolidated into a multi-brand file again.
 *
 * The single worked example trend below uses the same fictional demo brand as
 * brand_config_TEMPLATE.js ("Bramblewick", a plant-based snack bar brand).
 */
window.TRENDS_DATA = window.TRENDS_DATA || {};
window.TRENDS_DATA["bramblewick"] = {
    "generated_at": "2026-01-15T07:12:00+00:00",
    "source_pillars": [
      { "id": "clean-label-conversation", "name": "Clean Label Conversation", "savedSearchId": 1000001, "status": "clean" },
      { "id": "lunchbox-culture", "name": "Lunchbox Culture", "savedSearchId": 1000002, "status": "mixed" }
    ],
    "data_quality_notes": [
      "Lunchbox Culture pillar returned some noisy results from unrelated back-to-school retail promos — filtered before scoring."
    ],
    "trends": [
      {
        "id": "bramblewick-1",
        "name": "Parents filming ingredient-label reveals for snack swaps",
        "summary": "A wave of parent creators are filming side-by-side ingredient-label comparisons when swapping a mainstream lunchbox snack for a shorter-ingredient-list alternative. Format is simple: hold up both packets, read the back, react. High engagement, low production cost, and squarely in Bramblewick's clean-label territory.",
        "social": "HIGH",
        "news": "LOW",
        "social_count": 842,
        "news_count": 6,
        "momentum": "rising",
        "scores": {
          "topicFit": 9,
          "audiencePerspective": 9,
          "geoTiming": 7,
          "competitiveWhitespace": 8,
          "creativeStretch": 2
        },
        "activationMatch": "Foraged Not Faked",
        "source": "category",
        "posts": [
          {
            "text": "Read the back of both packets before you decide what's actually a 'healthy' snack. Genuinely shocked at how different these ingredient lists are for basically the same product.",
            "author": "@snacklabelswap",
            "platform": "TikTok",
            "url": "https://www.tiktok.com/@snacklabelswap/video/0000000000000000000",
            "views": 184000
          },
          {
            "text": "Did the label-swap challenge with my kids' lunchbox snacks this morning. Not going back after seeing this.",
            "author": "@thelunchboxdiaries",
            "platform": "Instagram"
          }
        ],
        "hashtags": ["#labelswap", "#cleanlabel", "#lunchboxideas"]
      }
    ]
};
