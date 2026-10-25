"""Copyright 2026 CaseSprout contributors. Licensed under Apache-2.0."""
import copy
import json
import subprocess
import sys

import pytest

from burr.casesprout.core import error_class, export_suite, read_trace, redact, select, write_report
from burr.casesprout.demo import approve_from_policy
from burr.casesprout.support import run


def trace(i=0, path=None, error=None):
    return {"inputs": {"request": {"topic": "faq", "ticket": str(i), "email": "sensitive"}},
            "path": path or ["intake", "faq"], "error": error,
            "observed": {"request": {"topic": "faq"}, "disposition": "wrong_history"}}


def test_deterministic_selection_dedup_budget_and_rare_strata():
    records = [trace(i) for i in range(8)] + [trace(9, ["intake", "outage"], "ConnectionError")]
    records.append(records[0])
    result = select(records, 2)
    assert result == select(list(reversed(records)), 2)
    assert result["report"]["duplicates_removed"] == 1
    assert result["report"]["selected_paths"] == 2
    assert result["cases"][0]["error"] == "ConnectionError"
    assert len(select(records, 100)["cases"]) == 9
    assert select(records, 1)["report"]["uncovered_strata"]


@pytest.mark.parametrize("budget", [0, -1, True, 1.5])
def test_budget_validation(budget):
    with pytest.raises(ValueError):
        select([trace()], budget)


def test_redaction_recursive_and_does_not_mutate():
    value = {"Email": "secret", "list": [{"TOKEN": "abc"}], "message": "free text remains"}
    assert redact(value) == {"Email": "[REDACTED]", "list": [{"TOKEN": "[REDACTED]"}], "message": "free text remains"}
    assert value["Email"] == "secret"
    assert "sensitive" not in json.dumps(select([trace()], 1))


def test_approval_never_copies_historical_output(tmp_path):
    manifest = select([trace()], 1)
    with pytest.raises(ValueError, match="approval"):
        export_suite(manifest, tmp_path / "unreviewed", "burr.casesprout.support:replay")
    approved = approve_from_policy(manifest)
    case = approved["cases"][0]
    assert case["approval"]["expected"]["output"]["disposition"] == "self_service"
    assert case["observed"]["disposition"] == "wrong_history"
    export_suite(approved, tmp_path / "suite", "burr.casesprout.support:replay")
    process = subprocess.run([sys.executable, "-m", "pytest", "-q", str(tmp_path / "suite")], capture_output=True, text=True)
    assert process.returncode == 0, process.stdout + process.stderr


@pytest.mark.parametrize("change", ["input", "duplicate", "basis", "false_approval", "bad_expected", "error_output"])
def test_export_rejects_invalid_review(tmp_path, change):
    manifest = approve_from_policy(select([trace()], 1))
    case = manifest["cases"][0]
    if change == "input":
        case["inputs"]["new"] = "tampered"
    elif change == "duplicate":
        manifest["cases"].append(copy.deepcopy(case))
    elif change == "basis":
        case["approval"]["basis"] = " "
    elif change == "false_approval":
        case["approval"]["approved"] = "yes"
    elif change == "bad_expected":
        case["approval"]["expected"] = {"output": {}}
    else:
        case["approval"]["expected"]["error"] = "ConnectionError"
    with pytest.raises(ValueError):
        export_suite(manifest, tmp_path / "suite", "burr.casesprout.support:replay")


def test_export_no_overwrite_and_no_code_injection(tmp_path):
    manifest = approve_from_policy(select([trace()], 1))
    with pytest.raises(ValueError):
        export_suite(manifest, tmp_path / "suite", "os:system;danger")
    export_suite(manifest, tmp_path / "suite", "burr.casesprout.support:replay")
    with pytest.raises(FileExistsError):
        export_suite(manifest, tmp_path / "suite", "burr.casesprout.support:replay")


def test_real_burr_tracking_and_failed_run(tmp_path):
    run({"request": {"topic": "faq"}}, storage=tmp_path, app_id="good")
    case = read_trace(tmp_path / "support/good/log.jsonl")
    assert case["path"] == ["intake", "faq"]
    assert case["observed"]["disposition"] == "self_service"
    assert case["inputs"] == {"request": {"topic": "faq"}}
    with pytest.raises(ConnectionError):
        run({"request": {"topic": "outage"}}, storage=tmp_path, app_id="failed")
    assert read_trace(tmp_path / "support/failed/log.jsonl")["error"] == "ConnectionError"


def events():
    return [{"type": "begin_entry", "sequence_id": 0, "action": "intake", "inputs": {}},
            {"type": "end_entry", "sequence_id": 0, "action": "intake", "state": {}, "exception": None}]


@pytest.mark.parametrize("kind", ["empty", "missing_end", "repeated", "gap", "action", "invalid_input", "continues_after_error"])
def test_malformed_and_incomplete_traces(tmp_path, kind):
    records = events()
    if kind == "empty":
        records = []
    elif kind == "missing_end":
        records.pop()
    elif kind == "repeated":
        records += events()
    elif kind == "gap":
        for item in records:
            item["sequence_id"] = 2
    elif kind == "action":
        records[-1]["action"] = "different"
    elif kind == "invalid_input":
        records[0]["inputs"] = []
    else:
        records[-1]["exception"] = "ValueError: failed"
        follow = events()
        for item in follow:
            item["sequence_id"] = 1
        records += follow
    path = tmp_path / "log.jsonl"
    path.write_text("\n".join(json.dumps(e) for e in records))
    with pytest.raises(ValueError):
        read_trace(path)


def test_error_class_no_message_and_html_escape(tmp_path):
    assert error_class("Traceback (most recent call last):\n  File \"demo.py\", line 1, in run\n    raise ValueError()\nValueError: private detail") == "ValueError"
    with pytest.raises(ValueError):
        error_class("unsupported exception format")
    manifest = select([trace(0, ["<script>alert(1)</script>"])], 1)
    write_report(manifest, tmp_path / "report.html")
    assert "<script>" not in (tmp_path / "report.html").read_text()


def test_cli_failure_and_selection(tmp_path):
    path = tmp_path / "log.jsonl"
    path.write_text("\n".join(json.dumps(e) for e in events()))
    args = [sys.executable, "-m", "burr.casesprout", "select", str(path), "--budget", "1", "--output", str(tmp_path / "review.json")]
    assert subprocess.run(args, capture_output=True).returncode == 0
    assert subprocess.run(args, capture_output=True).returncode == 2
    assert subprocess.run([sys.executable, "-m", "burr.casesprout", "export", str(tmp_path / "review.json"), "--runner", "x:y", "--output", str(tmp_path / "suite")], capture_output=True).returncode == 2


def test_exception_headers_not_multiline_message_or_notes():
    import traceback
    assert error_class("".join(traceback.format_exception(ValueError()))) == "ValueError"
    exc = ValueError("problem\nprivate_identifier: 123")
    if hasattr(exc, "add_note"):
        exc.add_note("another_secret: 456")
    assert error_class("".join(traceback.format_exception(exc))) == "ValueError"
    try:
        try:
            raise KeyError("inner")
        except KeyError as inner:
            raise RuntimeError("outer") from inner
    except RuntimeError as outer:
        assert error_class("".join(traceback.format_exception(outer))) == "RuntimeError"


@pytest.mark.parametrize("field", ["reviewer", "basis"])
@pytest.mark.parametrize("value", [None, False, 42, [], {}])
def test_review_metadata_requires_strings(tmp_path, field, value):
    manifest = approve_from_policy(select([trace()], 1))
    manifest["cases"][0]["approval"][field] = value
    with pytest.raises(ValueError, match="approval"):
        export_suite(manifest, tmp_path / "suite", "burr.casesprout.support:replay")


def test_end_before_begin_is_rejected(tmp_path):
    path = tmp_path / "log.jsonl"
    path.write_text("\n".join(json.dumps(e) for e in reversed(events())))
    with pytest.raises(ValueError, match="matching active begin"):
        read_trace(path)


def test_saved_demo_reports_agree_with_cases():
    # Reproduced evidence is checked when present; no generation/model call here.
    from pathlib import Path
    for path in Path("evidence/demo").glob("*-suite/cases.json"):
        manifest = json.loads(path.read_text())
        assert manifest["report"]["selected_paths"] == len({tuple(c["path"]) for c in manifest["cases"]})


def test_redaction_preserves_selection_metadata():
    item = trace()
    item["inputs"]["path"] = "private"
    selected = select([item], 1, fields=("path",))["cases"][0]
    assert selected["path"] == ["intake", "faq"]
    assert selected["inputs"]["path"] == "[REDACTED]"


def test_embedded_traceback_header_fails_closed():
    import traceback
    exc = ValueError("problem\nTraceback (most recent call last):\nprivate_identifier: 123")
    with pytest.raises(ValueError, match="Ambiguous"):
        error_class("".join(traceback.format_exception(exc)))
