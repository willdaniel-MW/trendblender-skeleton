# Architecture — where to look

The full end-to-end architecture writeup lives at `docs/architecture.md` in the repo root (not under this skill), because it's meant to be shared with a client or team, not just loaded as agent context.

It covers, in more depth than this skill needs to carry:

- The two-loop shape — the autonomous/scheduled refresh loop vs. the human-gated boolean maintenance loop, and why they're deliberately kept separate.
- The fan-out/concurrency model — one subagent per pillar (or pillar-batch), and why wall-clock time for a run tracks the busiest pillar, not the sum of all pillars.
- The fetch redesign in detail — why the original one-freeform-prompt-per-search approach was replaced with query-gen-at-onboarding plus statistics+document retrieval at refresh time.
- The three output-file contracts (`schema/brand-config.schema.json`, `schema/trend-record.schema.json`, `schema/morning-brief.schema.json`), referenced by path rather than restated.
- The enforcement/judgment split, in detail, with examples of what each side can and can't catch.
- Cost and cadence mechanics — how `ops.maxPillarsPerRefresh`, `ops.maxDocumentsPerPillar`, and `ops.refreshCadence` bound the cost of a refresh.

Read `docs/architecture.md` directly when you need any of the above in detail. This pointer file exists so this getting-started skill doesn't have to duplicate a document that's meant to stand on its own.
