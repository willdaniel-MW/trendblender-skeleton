/*
 * TEMPLATE — brand_config.js
 *
 * This is the exact shape a brand's brand_config.js must have to be loaded by
 * dashboard/trendjack.html as window.BRAND_CONFIG. It is validated against
 * schema/brand-config.schema.json (strict JSON inside the assignment below —
 * double-quoted keys, no trailing commas, no comments in the real file).
 *
 * One plugin build == one brand. brand.id is the brandKey used everywhere else
 * in the pipeline (trends_data.js registers into window.TRENDS_DATA[brandKey],
 * saved-search name prefixes, etc.) — it must be a lowercase-hyphen slug.
 *
 * The worked example below uses a fictional demo brand ("Bramblewick" —
 * a plant-based snack bar brand) so it is safe to use as a copy/paste starting
 * point without pulling in any real client's brand book.
 */
window.BRAND_CONFIG = {
  "schemaVersion": "1.0",
  "brand": {
    "id": "bramblewick",
    "name": "Bramblewick",
    "category": "Plant-based snack bars",
    "essence": "Small, honest snacks for people who read the ingredients list before the marketing copy.",
    "archetype": "The Straight-Talking Forager"
  },
  "identity": {
    "colors": {
      "primary": "#3F6B35",
      "secondary": "#F4EDE1",
      "accent": "#E08A2B"
    },
    "hashtags": ["#Bramblewick", "#SnackHonestly", "#ForagedNotFaked"],
    "logoText": "Bramblewick"
  },
  "audienceSegments": [
    {
      "id": "label-readers",
      "name": "Label Readers",
      "description": "Actively check ingredient lists and reject anything with more than a handful of recognisable ingredients."
    },
    {
      "id": "lunchbox-parents",
      "name": "Lunchbox Parents",
      "description": "Parents looking for snacks their kids will actually eat that they don't feel guilty packing."
    },
    {
      "id": "trailhead-snackers",
      "name": "Trailhead Snackers",
      "description": "Hikers and outdoor-activity people who want dense, portable, real-food energy without gels or bars full of syrup."
    }
  ],
  "activations": [
    {
      "name": "Foraged Not Faked",
      "description": "Brand platform contrasting Bramblewick's short, real ingredient lists against ultra-processed snack alternatives.",
      "triggerKeywords": ["ingredient list", "ultra-processed", "clean label", "real food", "additives"]
    },
    {
      "name": "Trailhead Fuel",
      "description": "Seasonal activation around hiking and outdoor-activity season — Bramblewick as portable real-food trail fuel.",
      "triggerKeywords": ["hiking", "trail", "outdoor", "backpacking", "camping"]
    }
  ],
  "territory": {
    "description": "On-territory: snacking, ingredient transparency, ultra-processed food debate, lunchbox culture, portable/on-the-go real food, plant-based (not vegan-lifestyle) eating.",
    "onTerritoryKeywords": ["snack", "ingredient list", "clean label", "lunchbox", "trail food", "plant-based snack"]
  },
  "rejectList": [
    {
      "pattern": "General veganism / animal-rights activism content",
      "reason": "Bramblewick is plant-based for taste and ingredient simplicity, not an ethical-vegan brand — this territory belongs to a different kind of brand voice."
    },
    {
      "pattern": "Weight-loss / diet-culture content",
      "reason": "Bramblewick positions on ingredient honesty, not calorie restriction or body-image messaging."
    },
    {
      "pattern": "Crypto/NFT/Web3 content",
      "reason": "No brand relevance; consistently low-quality trend matches from generic keyword overlap."
    }
  ],
  "pillars": [
    {
      "id": "clean-label-conversation",
      "name": "Clean Label Conversation",
      "description": "Social and news conversation about reading ingredient lists, additive-free food, and skepticism toward ultra-processed snacks.",
      "scope": "social+news",
      "savedSearchId": null,
      "status": "active"
    },
    {
      "id": "lunchbox-culture",
      "name": "Lunchbox Culture",
      "description": "Parent-facing conversation about school lunchbox ideas, snack guilt, and kid-approved healthier snacks.",
      "scope": "social",
      "savedSearchId": null,
      "status": "active"
    },
    {
      "id": "trail-and-outdoor-snacking",
      "name": "Trail & Outdoor Snacking",
      "description": "Conversation about snack choices for hiking, camping and other outdoor activity.",
      "scope": "social",
      "savedSearchId": null,
      "status": "punchlist"
    }
  ],
  "scoring": {
    "dimensions": ["topicFit", "audiencePerspective", "geoTiming", "competitiveWhitespace", "creativeStretch"],
    "weights": {
      "topicFit": 1.5,
      "audiencePerspective": 1,
      "geoTiming": 1,
      "competitiveWhitespace": 1,
      "creativeStretch": 0.5
    }
  },
  "ops": {
    "refreshCadence": "1/weekday",
    "retentionWindowDays": 3,
    "maxPillarsPerRefresh": 3,
    "maxDocumentsPerPillar": 25
  },
  "meta": {
    "builtFromSkeletonVersion": "v1",
    "createdAt": "2026-01-15",
    "lastRebuiltAt": "2026-01-15",
    "meltwaterAccountId": "demo-account-id"
  }
};
