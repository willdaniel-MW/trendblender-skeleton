# TrendBlender Skeleton

A brand-agnostic social trend-jacking pipeline: pull Meltwater signal for a set of "pillars" you define, cluster and score it against a brand's own DNA, and write a small, self-contained dashboard.

**This repo is not installable on its own.** It has no brand in it — no essence, no audience segments, no saved searches, no colours. It is the versioned, tagged foundation that the [`trendblender-onboard-brand`](../trendblender-onboard-brand) skill clones, fills in, and packages into an installable, brand-specific plugin.

If you're a Solutions Consultant who wants a working TrendBlender for a specific brand, you want that skill, not this repo directly.

## What's in here

```
schema/       — brand-config.schema.json (the contract), trend-record + morning-brief schemas
scripts/      — deterministic validators (Python 3, no external deps)
skills/       — the 5 pipeline skills, all reading from brand-config.json, none brand-specific
dashboard/    — trendjack.html + template data files, config-driven (no hardcoded brand)
docs/         — end-to-end architecture writeup, worked examples use a fictional demo brand
```

## The contract: brand-config.json

Everything brand-specific — essence, audience segments, activations, territory, reject list, search pillars, score weights, identity colours, and cost/cadence caps — lives in one file: `brand-config.json`, validated against `schema/brand-config.schema.json`. See that schema for the full shape.

A brand can have any number of pillars — this isn't fixed to any prior client's shape. The five scoring dimension **names** (`topicFit`, `audiencePerspective`, `geoTiming`, `competitiveWhitespace`, `creativeStretch`) are fixed by the dashboard's own rendering code and are not brand-configurable; their **weights** are.

## Versioning

Releases are tagged (`v1`, `v2`, ...). A brand build records exactly which tag it was built from in its own `brand-config.json` (`meta.builtFromSkeletonVersion`). Brand builds never auto-update — rebuilding against a newer tag is a deliberate, explicit re-run of the onboarding skill against the *same* saved `brand-config.json` and a newer tag, not a silent drift.

## What this system does and doesn't guarantee

The validators in `scripts/` deterministically enforce **structure**: required fields, valid enums, score-key completeness, no fabricated URLs, no leaked pipeline jargon in client-facing trend names. They run before anything is written or shown.

They cannot and do not enforce **judgment**: whether two posts represent the same underlying trend, whether a borderline post is genuinely off-territory, whether a trend name reads well to a client. Those are exactly the parts an LLM has to make a call on every refresh, and this skeleton does not claim to make those calls consistently — see each skill's SKILL.md for the checklists and self-critique steps used to make the judgment layer as disciplined as possible, and expect a human review pass, especially on a newly onboarded brand's first refresh.

## Day one will be rough, on purpose

A freshly onboarded brand's search pillars are auto-drafted from a plain-English description, not hand-tuned. The first refresh will be structurally valid but noisy — that's expected, not a bug. `trendblender-boolean-punchlist` exists specifically for the tuning pass that follows.

## Cost and cadence are configurable, not hardcoded

`ops.maxPillarsPerRefresh`, `ops.maxDocumentsPerPillar`, and `ops.refreshCadence` in `brand-config.json` bound how much a refresh actually costs. These are onboarding-interview questions, not constants baked into a skill file — a self-serve onboarding flow with no caps can run away on API cost.
