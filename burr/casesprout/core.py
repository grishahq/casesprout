"""Deterministic, offline selection with an explicit human oracle boundary.

Copyright 2026 CaseSprout contributors. Licensed under Apache-2.0.
"""

import copy
import hashlib
import html
import json
import re
from pathlib import Path

SCHEMA = "casesprout/v1"
DEFAULT_REDACT = ("email", "token", "password", "api_key", "secret")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def redact(value, fields=DEFAULT_REDACT):
    """Replace matching dictionary keys recursively, including dictionaries in lists.

    Field names are case-insensitive. Values, free text, and identifiers are not scanned.
    """
    names = {name.casefold() for name in fields}
    if isinstance(value, dict):
        return {k: "[REDACTED]" if k.casefold() in names else redact(v, names) for k, v in value.items()}
    if isinstance(value, list):
        return [redact(v, names) for v in value]
    return value


def error_class(exception):
    if not exception:
        return None
    if not isinstance(exception, str):
        raise ValueError("Trace exception must be a traceback string or null")
    # Take the first diagnostic header in each standard traceback section,
    # never the last message/exception-note line. Chained exceptions reset it.
    candidate = None
    awaiting_header = True
    seen_traceback_header = False
    for line in exception.splitlines():
        if line in ("The above exception was the direct cause of the following exception:",
                    "During handling of the above exception, another exception occurred:"):
            candidate = None
            awaiting_header = True
            seen_traceback_header = False
            continue
        if line == "Traceback (most recent call last):":
            if candidate is not None or seen_traceback_header:
                raise ValueError("Ambiguous traceback header in exception message; review trace manually")
            seen_traceback_header = True
            continue
        if awaiting_header:
            match = re.fullmatch(r"([A-Za-z_][\w.]*)(?::.*)?", line)
            if match:
                candidate = match.group(1)
                awaiting_header = False
    if candidate is None:
        raise ValueError("Cannot classify exception traceback; exception groups are not supported")
    return candidate


def read_trace(path):
    """Import one complete local Burr application log (one invocation, sequence 0..n).

    First action inputs are the runner invocation. Final public state is observed output.
    A custom runner maps this contract to the application; custom serializers are not run.
    """
    events = [json.loads(line) for line in Path(path).read_text().splitlines() if line.strip()]
    begins, ends = {}, {}
    active = None
    for event in events:
        if not isinstance(event, dict):
            raise ValueError(f"Expected JSON object event: {path}")
        kind = event.get("type")
        if kind not in ("begin_entry", "end_entry"):
            continue
        seq = event.get("sequence_id")
        if type(seq) is not int or seq < 0:
            raise ValueError(f"Invalid sequence in {path}")
        if kind == "begin_entry":
            if active is not None or seq != len(ends):
                raise ValueError(f"Invalid action event order: {path}")
            active = seq
        else:
            if active != seq:
                raise ValueError(f"End event without matching active begin: {path}")
            active = None
        bucket = begins if kind == "begin_entry" else ends
        if seq in bucket:
            raise ValueError(f"Repeated sequence in {path}; split resumed invocations first")
        bucket[seq] = event
    if not begins or begins.keys() != ends.keys() or sorted(begins) != list(range(len(begins))):
        raise ValueError(f"Incomplete or non-contiguous run: {path}")
    ordered = [ends[i] for i in sorted(ends)]
    for i, end in enumerate(ordered):
        if not isinstance(end.get("action"), str) or end["action"] != begins[i].get("action"):
            raise ValueError(f"Mismatched action: {path}")
        if i < len(ordered) - 1 and end.get("exception"):
            raise ValueError(f"Run continues after error: {path}")
    inputs, state = begins[0].get("inputs"), ordered[-1].get("state")
    if not isinstance(inputs, dict) or not isinstance(state, dict):
        raise ValueError(f"Expected JSON object inputs and final state: {path}")
    public_state = {k: v for k, v in state.items() if not k.startswith("__")}
    return {"inputs": inputs, "path": [e["action"] for e in ordered],
            "error": error_class(ordered[-1].get("exception")), "observed": public_state}


def signature(case):
    return canonical([case["path"], case["error"]])


def select(traces, budget, fields=DEFAULT_REDACT):
    """Cover rare observed path/error strata first, then fill in content-hash order.

    Duplicate identity includes input, observed output, path and error before redaction.
    Never ranks cases using expected outcomes or regression detection results.
    """
    if type(budget) is not int or budget < 1:
        raise ValueError("Budget must be a positive integer")
    unique = {digest(case): case for case in traces}
    groups = {}
    for key, case in sorted(unique.items()):
        groups.setdefault(signature(case), []).append(key)
    strata = sorted(groups, key=lambda s: (len(groups[s]), s))
    chosen = [groups[s][0] for s in strata][:budget]
    chosen += [key for key in sorted(unique) if key not in chosen][:max(0, budget-len(chosen))]
    cases = []
    for key in chosen:
        case = {**unique[key], "inputs": redact(unique[key]["inputs"], fields),
                "observed": redact(unique[key]["observed"], fields)}
        case["id"] = key[:20]
        case["fingerprint"] = digest(case)
        case["approval"] = {"approved": False, "reviewer": "", "basis": "", "expected": None}
        cases.append(case)
    all_paths = {canonical(c["path"]) for c in traces}
    selected_paths = {canonical(c["path"]) for c in cases}
    report = {"input_runs": len(traces), "unique_runs": len(unique), "duplicates_removed": len(traces)-len(unique),
              "budget": budget, "selected_runs": len(cases), "observed_paths": len(all_paths),
              "selected_paths": len(selected_paths), "observed_path_error_strata": len(groups),
              "selected_path_error_strata": len({signature(c) for c in cases}),
              "uncovered_strata": [json.loads(s) for s in strata if s not in {signature(c) for c in cases}],
              "selection": "rare observed path/error strata, then SHA-256 order",
              "coverage_scope": "observed complete runs only; not all reachable graph paths",
              "redacted_fields": sorted(set(fields)),
              "redaction_limit": "field-key replacement only; review free text and replay semantics before sharing"}
    return {"schema": SCHEMA, "report": report, "cases": cases}


def write_report(manifest, path):
    body = html.escape(json.dumps(manifest["report"], indent=2))
    rows = "".join("<tr><td>" + html.escape(c["id"]) + "</td><td>" + html.escape(" → ".join(c["path"]))
                   + "</td><td>" + html.escape(c["error"] or "success") + "</td><td>"
                   + ("approved" if c["approval"]["approved"] else "needs review") + "</td></tr>" for c in manifest["cases"])
    Path(path).write_text("<!doctype html><html lang='en'><meta charset='utf-8'><title>CaseSprout selection</title>"
                         "<style>body{font:17px system-ui;max-width:1100px;margin:48px auto;background:#f5f3ed;color:#173d36}"
                         "td,th{padding:14px;text-align:left;border-bottom:1px solid #bac9bf}pre{padding:24px;background:white;white-space:pre-wrap}</style>"
                         "<h1>CaseSprout · Selection report</h1><p>Observed coverage. Expected outcomes require explicit review.</p>"
                         "<table><tr><th>Case</th><th>Execution path</th><th>Outcome class</th><th>Review</th></tr>" + rows + "</table><pre>" + body + "</pre></html>")


def export_suite(manifest, target, runner):
    """Export only reviewed cases. Runner is an importable module:function, no code generation from trace values."""
    if not re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*:[A-Za-z_]\w*", runner):
        raise ValueError("Runner must be module:function")
    if manifest.get("schema") != SCHEMA or not manifest.get("cases"):
        raise ValueError("Expected a non-empty casesprout/v1 review manifest")
    ids = set()
    for case in manifest["cases"]:
        original = {k: v for k, v in case.items() if k not in ("fingerprint", "approval")}
        if digest(original) != case.get("fingerprint") or case["id"] in ids:
            raise ValueError("Case changed or duplicate ID; reselect and review")
        ids.add(case["id"])
        approval = case.get("approval", {})
        expected = approval.get("expected")
        if approval.get("approved") is not True or any(not isinstance(approval.get(key), str) or not approval[key].strip() for key in ("reviewer", "basis")):
            raise ValueError(f"Case {case['id']} needs explicit approval, reviewer and independent basis")
        if not isinstance(expected, dict) or set(expected) != {"output", "error"}:
            raise ValueError("Expected must contain exactly output and error")
        if expected["error"] is not None and (not isinstance(expected["error"], str) or not re.fullmatch(r"[A-Za-z_]\w*(?:\.[A-Za-z_]\w*)*", expected["error"])):
            raise ValueError("Expected error must be a class name or null")
        if expected["error"] is not None and expected["output"] is not None:
            raise ValueError("Error cases must use null output")
    target = Path(target)
    target.mkdir(parents=True, exist_ok=False)
    payload = copy.deepcopy(manifest)
    payload["runner"] = runner
    (target / "cases.json").write_text(json.dumps(payload, indent=2, ensure_ascii=False, allow_nan=False) + "\n")
    (target / "test_casesprout.py").write_text(TEST_TEMPLATE)
    write_report(manifest, target / "report.html")


TEST_TEMPLATE = '''"""Generated by CaseSprout. Run only with a trusted application adapter."""
import importlib
import json
from pathlib import Path
import pytest

MANIFEST = json.loads(Path(__file__).with_name("cases.json").read_text())

@pytest.mark.parametrize("case", MANIFEST["cases"], ids=lambda c: c["id"])
def test_reviewed_execution(case):
    module, name = MANIFEST["runner"].split(":")
    runner = getattr(importlib.import_module(module), name)
    expected = case["approval"]["expected"]
    try:
        output = runner(case["inputs"])
    except Exception as exc:
        actual = type(exc).__name__
        qualified = type(exc).__module__ + "." + actual
        assert expected["error"] in (actual, qualified), f"Unexpected error class: {actual}"
    else:
        assert expected["error"] is None, "Expected an exception but execution succeeded"
        assert output == expected["output"]
'''
