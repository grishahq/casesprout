# CaseSprout implementation plan

CaseSprout is an independent Apache-2.0 fork of Apache Burr, not an ASF release.
Upstream baseline: `8bfd72689f1fbba4e858f7440dc77b764cd653b9`.

## Stages
1. Preserve Burr history/runtime/viewer and notices; document existing manual test creation.
2. Add a modular `burr.casesprout` CLI/library: strict local trace import, deterministic path/error selection, exact duplicate removal, configurable field redaction, explicit reviewed expectations, portable pytest export and JSON/HTML coverage report.
3. Run a deterministic support-agent through real Burr tracking. Specify expected outcomes independently. Freeze injected regressions and sample size before comparing seeded random selection. Save raw controlled traces, methodology and measured results.
4. Run focused upstream core/tracking tests, new contract tests, independent review and clean wheel install with exported suite. Fix defects. Build attributed wheel/source/evidence artifacts.
5. Publish public grishahq/casesprout v0.1.0 alpha release, verify artifact/tag installation and release readback.
6. Prepare five LinkedIn posts and five X threads with real evidence, two original generated concept assets, actual demo screenshot and plotted chart. Verify social access and coordinate scheduling under the portfolio lock.

## v0.1 acceptance
- Original Burr runtime and viewer source remain available; upstream remote and immutable baseline recorded.
- Local tracker JSONL is parsed with sequence validation; incomplete runs fail visibly.
- Selection reproducibly covers observed path/error signatures within budget, with deterministic ties and duplicate counts.
- Redaction removes configured fields recursively from inputs and observed state; no claim of general anonymization.
- Historical output is never silently accepted as truth: export requires a separately supplied approved expectation for every selected case.
- Exported pytest calls a developer-provided runner with redacted input and checks approved output/error class; real demo suite passes and detects predeclared regressions.
- Reports distinguish observed coverage from possible graph paths and report sample/experiment limits.
- Clean artifact install and published GitHub prerelease are verified; all campaign claims match saved evidence.

## Roadmap and maintenance
v0.2: browser review interface, richer redaction configuration and CI comparison. v0.3: one additional import/export format justified by early users. Keep changes within `burr/casesprout`, tests and docs; merge upstream deliberately and rerun contract/core tests. Support Python 3.10+ for the fork; triage issues weekly, document compatibility and publish fixes with versioned tags. No hosted service or API keys required for v0.1.
