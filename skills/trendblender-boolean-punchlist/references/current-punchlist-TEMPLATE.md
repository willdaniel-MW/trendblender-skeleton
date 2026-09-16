# Current Punchlist State — TEMPLATE

Copy this file into a brand-specific working file (e.g. `current-punchlist-<brandKey>.md`, kept alongside that brand's `brand-config.json`) at onboarding time or the first time this skill runs for a brand. Do not fill in real brand data here — this file stays an empty starter template.

Live carry-over between sessions. Every refresh appends or removes items here.

Format per item:
```
- [SEARCH_ID] SearchName (pillar: <pillar id from brand-config.json>) — <one-line diagnosis> — <status: new / in-progress / validated / declined>
```

Diagnosis should name one of: bleeding, silent, over-tightened, volume-fine-but-wrong-vocabulary (see SKILL.md thresholds — 3 consecutive refreshes for bleeding/silent, immediate for over-tightened after a known recent edit).

Remember: once an item here reaches `validated` (WIN) or `declined` (deprecated), reflect the outcome in that brand's `brand-config.json` (`pillars[].status`, `pillars[].savedSearchId`) — this file is working notes, not the artifact of record.

*(No items yet. Populated by the trendblender-boolean-punchlist workflow.)*
