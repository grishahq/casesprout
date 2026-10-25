# CaseSprout

**Turn Burr run history into focused, reviewed regression tests.**

CaseSprout is an independent attributed fork of [Apache Burr](https://github.com/apache/burr), retaining its state-machine runtime, persistence, tracing and trace-viewer source. It adds deterministic batch trace selection, exact deduplication, field redaction and an explicit review step before exporting runnable pytest fixtures and observed-path coverage reports.

**v0.1.0a1 is an alpha developer tool.** Local JSON traces, one complete invocation per application log, deterministic adapters and exact assertions first. It is not an ASF release. Original credits and licensing are preserved; read [UPSTREAM.md](UPSTREAM.md) and [the upstream README](README.upstream.md).

Burr already provides manual `burr-test-case create`, persistence and replay. CaseSprout's addition is selecting and reviewing a useful batch. It never assumes that a historical answer was correct.

## Install and run the offline demo

Python 3.10+; validation uses Python 3.11. Use a new environment: this fork retains the `burr` namespace and must not share an environment with `apache-burr`.

```sh
python3 -m venv .venv
. .venv/bin/activate
python -m pip install 'casesprout_burr-0.1.0a1-py3-none-any.whl[tracking-client]' pytest
python -m burr.casesprout.demo /tmp/casesprout-demo
python -m pytest /tmp/casesprout-demo/suite -q
```

Download the wheel from this repository's GitHub release first. No PyPI publication is claimed. For a source checkout, use `python -m pip install '.[tracking-client]' pytest` instead. No model keys are needed.

The demo creates 110 real controlled Burr runs, deduplicates to 100, selects five and exports a passing reviewed suite. The historical security answer is intentionally wrong; expected behavior comes from a separate policy table. Compare the fixed version against three injected regressions. Read the [methodology and limitations](casesprout_docs/METHODOLOGY.md), [measured results](evidence/demo/results.json), and [selection report](evidence/demo/suite/report.html).

## Use your own local traces

```sh
casesprout select /path/to/project-traces --budget 12 --output review.json --redact-field customer_id
# Edit review.json: inspect each case, set approval fields from your acceptance policy.
casesprout export review.json --runner myapp.regression:replay --output exported-suite
python -m pytest exported-suite -q
```

A reviewer supplies each case's approval:

```json
{
  "approved": true,
  "reviewer": "developer-name",
  "basis": "Support acceptance policy section 4; not observed output",
  "expected": {"output": {"disposition": "human_review"}, "error": null}
}
```

The imported `inputs` are the first action's inputs. Your adapter accepts that JSON object and returns the final public state (or the output object you approve). Expected exceptions use `{"output": null, "error": "ConnectionError"}`. For side effects, use a controlled test environment. Exported tests run your adapter as normal Python code; they are not a sandbox. See [the contract](casesprout_docs/CONTRACT.md).

Default redaction replaces dictionary values for email, token, password, api_key and secret, case-insensitively at any depth in inputs/observed state. Additional named keys can be added. This does not scan free text, source identifiers or approved expectations. Review exports before sharing; redaction can change replay semantics. Keep real trace archives private.

Coverage means paths and path/error signatures observed in imported complete runs, not all possible graph paths. Selection favors rare signatures and can miss variation within a path. Approval is an explicit recorded decision, not proof of a correct oracle.

## Keep the Burr baseline

The original `burr` commands, runtime, viewer source, examples and documentation remain. Install `.[tracking]` for the upstream tracker server dependencies and follow `README.upstream.md` to build/run the trace viewer. A prebuilt viewer bundle is not added to this alpha wheel. For CaseSprout's report, open the generated HTML directly; no server or JavaScript is required.

## Development and roadmap

```sh
python -m pip install -e '.[tracking-client]' pytest pytest-asyncio build
python -m pytest tests/casesprout tests/core/test_action.py tests/core/test_application.py tests/core/test_graph.py tests/core/test_state.py tests/core/test_validation.py tests/tracking/test_local_tracking_client.py tests/tracking/test_common_models.py -q
```

v0.2: browser review interface, redaction configuration and CI comparison. v0.3: one further import/export format chosen from early user needs. Keep changes modular under `burr/casesprout`; deliberately merge upstream updates and rerun the contract and relevant core tests. See [the implementation plan](IMPLEMENTATION_PLAN.md) and [changelog](CHANGELOG.md).

Report reproducible issues in this fork's issue tracker. Security concerns: use the upstream SECURITY.md for upstream Burr issues; report CaseSprout-specific concerns privately to the repository owner. Do not attach private traces to public issues.
