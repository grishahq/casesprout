# CaseSprout English launch kit

Five distinct story beats, each with a substantive LinkedIn post and four-post X thread. `CAMPAIGN.md` is the readable copy; `campaign.json` holds audience, hook, evidence references, CTA, image, alt text, length checks and separate prepared/scheduled/published states.

## Assets

1. `assets/01-trace-is-not-test.png`: original conceptual illustration generated with built-in imagegen; prompt/source in `image-provenance.json`.
2. `assets/02-choose-paths.png`: second original conceptual illustration; same visual direction and full provenance.
3. `assets/03-real-selection-report.png`: actual browser screenshot of the working CaseSprout report from `evidence/demo/suite/report.html`, served locally. No fabricated UI.
4. `assets/04-equal-budget-experiment.png`: matplotlib plot from `evidence/demo/results.json`; reproducible with `scripts/casesprout_chart.py`. No generated metrics.
5. `assets/05-verified-release.png`: actual public GitHub prerelease screenshot after publication, showing the alpha label, immutable tag/commit, attribution and evidence notes.

Visual direction: ivory, forest green and muted amber; tactile paper-cut conceptual illustrations; real software screenshots and data-driven charts for evidence. All image text and alt text are English. Both generated outputs and both screenshots/chart were visually inspected.

## Publication status

A prepared campaign is not a scheduled or published campaign. The repository release is public. Read `scheduling.json` for exact native account checks, queue observations, reservations, successful readback and any limitations. Never infer scheduling from the copy or proposed slots. The campaign source generator rewrites prepared states; do not rerun it after scheduling without preserving confirmed scheduling records.

Default cadence is at most three primary items per week per platform across the entire five-project portfolio; one X thread counts as one item. Reservation and native-composer access require the shared lock. Existing unrelated scheduled posts must be preserved.

Character limits were checked against LinkedIn Help (3,000) and X Help (standard 280). X counts use a conservative weighted bound (URLs 23, ASCII 1, all other codepoints 2); every message is comfortably below 280. No long-post entitlement is assumed.
