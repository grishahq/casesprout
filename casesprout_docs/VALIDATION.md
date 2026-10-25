# Validation record

Release: `v0.1.0a1`, immutable commit `cbbfe608e89e492a4189a0da5a998cf886461749`.
Upstream baseline: `8bfd72689f1fbba4e858f7440dc77b764cd653b9`.

- Focused upstream action/application/graph/state/validation/local-tracker/model tests plus CaseSprout contract tests: **397 passed, 1 skipped** on Python 3.11. One upstream Pydantic deprecation warning. `evidence/validation.log`.
- Current standalone CaseSprout contract tests: **39 passed**. `evidence/contracts-final.log`.
- Upstream distribution/license configuration tests: **3 passed**. `evidence/upstream-release-config.log`.
- Independent read-only AI review found four P2 defects. Each was fixed and rechecked; no further P1/P2 blockers found within scope. `evidence/INDEPENDENT_REVIEW.md`.
- Development wheel installed into a clean environment, outside the source import path. Included demo generated real Burr traces and exported suite: **5 passed**. `evidence/clean-import.log`, `evidence/clean-suite.log`.
- Published wheel downloaded from GitHub, checked against release SHA-256 manifest, installed in another isolated environment and executed with Python isolated mode: **5 exported tests passed**. `evidence/release-verification.json`, `evidence/release-suite.log`.
- All three predeclared mutant implementations produce pytest assertion failures (exit code 1), checked separately from successful baseline. `evidence/mutation-verification.json` and `evidence/demo/mutant-*/pytest.log`.
- GitHub CI for the release commit passes on Python 3.10, 3.11 and 3.12: see `evidence/release-ci-runs.json` and `evidence/github-ci.json`. A later Dependabot PR run is separate and is not substituted for release-commit evidence.
- Built wheel includes core runtime, support policy and Apache/third-party wheel notices. Source retains broader component notices. `evidence/package-contents.json`.

This is focused validation, not a claim that every upstream integration, database, model provider, web viewer build or platform has been tested. The skipped upstream test and warning are retained honestly. The controlled experiment is synthetic deterministic software execution, not measured model quality or production adoption.
