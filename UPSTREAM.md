# Attribution and fork boundary

CaseSprout is an independent attributed fork maintained by grishahq. It is not an Apache Software Foundation release, endorsed product, or new name for Apache Burr.

- Upstream: https://github.com/apache/burr
- Immutable baseline: `8bfd72689f1fbba4e858f7440dc77b764cd653b9`
- Upstream version at baseline: Apache Burr 0.43.0 development tree.
- Preserved upstream: full git history, state-machine runtime, persistence, tracing, trace-viewer source, examples, documentation and original licensing files.
- Existing capability: `burr-test-case create` manually extracts one recorded state for pytest. See `docs/examples/guardrails/creating_tests.rst`. CaseSprout does not claim trace replay or manual test creation as new.
- Addition: modular `burr/casesprout`, deterministic batch path/error selection, exact duplicate handling, key-based redaction, explicit expectation approval and suite/report export, controlled demo and experiment.
- Packaging changes: distribution name `casesprout-burr`, alpha version and CLI entry point, project URLs and self-referencing optional dependencies. The Python namespace remains `burr`; use a separate environment from `apache-burr` to avoid overlapping files.

Apache Burr authors and contributors retain their credits. Read the original README in `README.upstream.md`; original `LICENSE`, `LICENSE-sdist`, `LICENSE-wheel`, `NOTICE` and `DISCLAIMER` remain included. The trace viewer and some examples have additional third-party notices in those files and component directories. These are not replaced by a blanket core-only license claim. New CaseSprout code is Apache-2.0; generated concept art is labeled separately in campaign provenance.

Maintenance: preserve an `upstream` remote; compare updates against this SHA, merge intentionally, rerun core/tracking and export contracts, and review distribution notices. No upstream push is part of this fork's workflow.

Upstream CI jobs are retained with an `apache/burr` repository guard. This prevents fork pushes from attempting ASF website deployment or unrelated upstream administration. The fork runs its own focused offline CI matrix.
