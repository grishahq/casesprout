# v1 trace, review and export contract

## Input

`casesprout select` accepts one `log.jsonl` or recursively finds those files in a directory. Each file is one completed, sequential Burr invocation starting at sequence zero. Resumed runs and logs containing multiple invocations must be split first. Begin/end entries must alternate in sequence and match action names. Spans and other Burr events are ignored. Missing ends, duplicate sequence IDs, gaps and continuation after an error fail visibly; import never silently drops a failed record.

This alpha supports JSON-native inputs/state. It does not execute custom serializers. The first action's `inputs` are captured as runner input; final state keys beginning with `__` are omitted from observed output. Applications with required initial state or later external inputs need a purpose-built adapter/import workflow; this importer cannot reconstruct them automatically.

Burr stores exceptions as formatted traceback strings. CaseSprout recognizes ordinary Python exception diagnostics, message-less exceptions and standard chains; it discards messages. Exception groups and ambiguous embedded traceback headers are rejected. These lossy strings are not authenticated structured exception metadata. Error classification is best-effort for supported formats and is not a free-text privacy guarantee.

## Selection

Exact duplicate identity is SHA-256 of canonical JSON containing raw first inputs, action path, final public state and error class. Time, source paths, app identifiers and traceback messages are excluded. Raw values are hashed before redaction; hashes are identifiers, not a privacy or encryption mechanism. Same input/path with different output remains distinct.

Selection covers rare observed path/error signatures first. Strata sort by unique-run frequency then canonical path/error signature. Representatives and remaining fill sort by content SHA-256. Budget is a positive integer; fewer unique runs produce fewer cases. Order of source files cannot change selection. Reports name uncovered observed signatures when budget is insufficient. All coverage is observational, not graph reachability, branch coverage or correctness.

## Redaction

Dictionary-key matching is case-insensitive and recursive in inputs and observed state, including lists. Defaults: email, token, password, api_key, secret. `--redact-field` adds keys. Metadata path/error/ID remains structural. Free text, dictionary keys themselves and approved expectations are not scrubbed. Review before sharing. Hashes may permit guessing low-entropy raw records. Redacted required fields may break replay; use synthetic replacements or a controlled adapter and review that behavior explicitly.

## Review

Selection writes pending approvals; no observed output becomes an expectation. For every selected case the developer must set `approved` to boolean true, a nonempty string `reviewer`, a nonempty string `basis`, and `expected` with exactly `output` and `error`. Error cases require null output and a short or qualified Python exception class name. Historical observed values remain visible to help review but are not assertions.

Case fingerprints detect changes to selected content after review-file creation; approval edits are allowed. This protects against accidental drift, not malicious edits: it is not a signature or identity verification. Review your input/output semantics and ensure the independent basis actually supports the expectation.

## Export and execution

`--runner module:function` identifies a trusted installed adapter. It receives the selected redacted `inputs` dictionary and returns a JSON-compatible Python value matching approved output exactly, or raises the approved exception class. Generated tests import the adapter at execution, not export time. Inputs are stored as JSON rather than interpolated as Python source. Unexpected exception classes, missing expected exceptions and output differences fail pytest. Output/trace-path equality is not additionally asserted; approved outcome is the contract.

Export writes a fresh directory with `cases.json`, `test_casesprout.py` and `report.html`; existing directories are refused. An exported suite needs pytest, the adapter's application dependencies, and any fixture services it explicitly requires. The demo's adapter is included in the wheel. Error-class equality is deliberately simple and does not compare exception messages or subclasses.

Neither selection nor export authenticates provenance, sanitizes arbitrary secrets, sandboxes replay, or generates a correct acceptance policy. Those responsibilities remain with the developer and test environment.
