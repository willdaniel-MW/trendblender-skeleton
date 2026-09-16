# Round History — TEMPLATE

Copy this file into a brand-specific working file (e.g. `round-history-<brandKey>.md`, kept alongside that brand's `brand-config.json`) at onboarding time or the first time this skill runs for a brand. Do not fill in real brand data here — this file stays an empty starter template.

Every boolean-round's fixes with before/after and validation verdicts. Institutional memory for what was tried and whether it worked, per brand.

Format per round:
```
## Round N — YYYY-MM-DD
### [SEARCH_ID] SearchName (pillar: <pillar id from brand-config.json>)
- **Before:** <fragment>
- **After:** <fragment>
- **Rationale:** <why>
- **Verdict:** WIN | PARTIAL | OVER-TIGHTENED | NO CHANGE | ROLLED BACK
- **brand-config.json updated:** yes/no — <what changed: status, savedSearchId, or "n/a">
```

Note the "Round 1" for any newly onboarded brand is expected to be a larger-than-usual batch, since pillar booleans are auto-drafted at onboarding rather than hand-tuned — that's normal, not a sign the onboarding step failed.

*(No rounds logged. Add entries as the operator pushes and validates fixes.)*
