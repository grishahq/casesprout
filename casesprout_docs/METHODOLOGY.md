# Controlled experiment: fixed before measurement

The machine-readable protocol is `burr/casesprout/support_policy.json`. Its hash is recorded in `evidence/demo/results.json`. Expected outcomes, mutation names, corpus composition, sample size, random seed and sensitivity-seed count were written before generating results. No model API, production traffic, external tool or customer data is involved.

## Population and independent oracle

Run the real Burr state machine in `burr/casesprout/support.py` with LocalTrackingClient: 80 FAQ, 12 refund, 4 security, 3 escalation and 1 outage invocation. Ten extra FAQ runs repeat existing inputs: 110 actual tracked runs, 100 unique complete executions after content-based deduplication. Timestamps/trace file names are excluded from duplicate identity. Topic, synthetic ticket identifier and synthetic email are inputs. Each run has intake plus a topic-specific terminal action, giving five observed paths. The unavailable backend intentionally raises ConnectionError.

The historical security handler intentionally produces `auto_reset`. Independent policy requires `human_security_review`. The fixed replay handler implements that policy. Demo approvals are generated from the separately specified policy table, never from observed outputs. This is a transparent deterministic fixture oracle, not a claim of human evaluation of model answers. In real use, developers must supply their own approved expected outcomes and basis.

## Equal-budget comparison

Both methods receive the same 100 unique executions; each chooses five. CaseSprout takes a representative of each observed path/error stratum, sorting rare strata first, breaking ties by canonical signature, then content SHA-256. Remaining budget fills in SHA-256 order. Random sampling uses Python `random.Random(7).sample` without replacement from the same population sorted by content SHA-256. No expected outcome or mutation result is used to select.

Replay each sample against three predeclared variants: refund automatically approved, security reset automatically, outage exception swallowed. A mutant is detected if any approved case fails on exact output or expected error class. Tests are also exported as real pytest suites; separate validation runs execute each mutant suite and expect failing exit codes.

Repeat random selection for seeds 0 through 999 to show sensitivity instead of relying only on one favorable random draw. All seeds use the same sample budget and oracle. `results.json` records actual measured counts, detected mutation names and means. This measures path/error representation and detection of these three controlled mutations, not generalized quality or a universal advantage over random sampling.

## Limits

The workload deliberately places mutations on rare paths. Path-based selection is favored by that design. It can miss within-path semantic variation, unseen paths, branches within actions and nondeterministic failures. More observed coverage does not establish correctness. The source history contains an intentionally bad outcome precisely to show why historical outputs must not become expected truth automatically. Exact equality is suitable for this deterministic support example, but may be unsuitable for model outputs. No performance, cost, adoption or debugging-time claim is made.

## Reproduce

```sh
python -m burr.casesprout.demo /tmp/casesprout-demo
python -m pytest /tmp/casesprout-demo/suite -q
cat /tmp/casesprout-demo/results.json
```

The destination must be fresh. Demo trace logs contain only controlled synthetic data; they do not establish a privacy guarantee for arbitrary user logs. Key-based redaction does not scrub free text or make a required redacted credential replayable.
