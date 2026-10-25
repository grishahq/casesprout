# CaseSprout 0.1.0a1 — alpha

A folder of traces is not a regression suite. CaseSprout selects representative complete Burr executions by observed path and error class, removes exact duplicates, redacts named fields, and requires explicit expected-outcome approval before exporting pytest and a coverage report.

This is an independent attributed Apache Burr fork based on `8bfd72689f1fbba4e858f7440dc77b764cd653b9`. Burr already provides persistence, replay, tracking and manual test creation. Its runtime, trace viewer source, history and notices are retained. This is not an ASF release.

## Reproducible evidence

- Controlled support workflow: 110 actual Burr local-tracker runs, 100 unique executions, five observed paths.
- Equal budget of five cases: CaseSprout covers five paths and detects all three predeclared injected regressions; seeded random (7) covers two and detects one.
- Sensitivity: random seeds 0–999 average 1.876 observed paths and 0.708 detected regressions. Rare-path-targeted mutations favor path selection; no general superiority or production-quality claim.
- Historical security output is intentionally wrong. Expected outcomes come from an independent policy fixture, never the observation.
- Focused core/tracking and new contract tests, independent AI review, exported passing suite and failing mutant suites are saved in `evidence/`. One upstream Python-version-specific test is skipped; one upstream Pydantic deprecation warning remains.

## Quickstart from the wheel asset

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install 'casesprout_burr-0.1.0a1-py3-none-any.whl[tracking-client]' pytest
python -m burr.casesprout.demo /tmp/casesprout-demo
python -m pytest /tmp/casesprout-demo/suite -q
```

Download the wheel first and run from that directory. Python 3.10+; locally verified on 3.11. Use a separate environment from apache-burr because the namespace remains burr. Source-install and custom-adapter instructions are in README.md. No registry publication or model key required.

## Assets and limits

Wheel, source distribution, controlled demo/evidence archive, campaign artwork/copy archive and SHA-256 checksums. The source archive retains licensing and new contract documentation. The separate evidence archive includes synthetic traces and reports.

Alpha scope: one complete sequential invocation per local JSON log; no cloud trace ingestion, custom serializer execution, automatic oracle or browser review UI. Exact equality suits the deterministic example; nondeterministic agents need deliberate assertions. Redaction is key-based, not anonymization, and can change replay semantics. Coverage is limited to observed complete runs. The upstream viewer remains source that needs its normal build, not a newly bundled production UI.

v0.2: browser review, richer redaction configuration and CI comparison. v0.3: another format justified by early users.
