# Changelog

## v1.1.0 — 2026-09-16

- Fixed unsubstituted `<brandKey>` template placeholders in `trendblender-refresh` and `trendblender-morning-brief` SKILL.md descriptions — these are syntactically XML tags and were failing plugin validation ("SKILL.md description cannot contain XML tags") on any generated brand build.
- Added `scripts/sanitize_skills.py`, run by the onboarding skill before packaging, to catch this class of issue automatically on future builds.

## v1.0.0 — 2026-09-16

Initial brand-agnostic skeleton, rebuilt from the Unilever Home Care TrendBlender plugin.

- Introduced `brand-config.json` as the explicit contract between this repo and the onboarding skill, replacing hardcoded per-brand prose.
- Replaced the freeform `mira_search_media_news` fetch with a hybrid model: `unified_retrieval_query_gen_tool` drafts pillar booleans, persisted as real Meltwater saved searches, then `unified_retrieval_statistics_retrieval_tool` and `unified_retrieval_document_retrieval_tool` fetch structured volume/sentiment stats and real evidence documents per refresh.
- `dashboard/trendjack.html` now reads brand identity, colours, and score weights from a `brand_config.js` sibling instead of a hardcoded `BRANDS` object.
- Added deterministic validators (`scripts/validate_brand_config.py`, `scripts/validate_trends.py`, `scripts/validate_brief.py`) with no external dependencies.
- Pillar count is unbounded and brand-defined, replacing the original's fixed 4-brand / 33-search shape.
- Documented the judgment/enforcement split explicitly: structure is validated deterministically, clustering and territory judgment calls are not and are not claimed to be.
