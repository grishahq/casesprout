"""Copyright 2026 CaseSprout contributors. Licensed under Apache-2.0."""
import argparse
import json
from pathlib import Path

from .core import DEFAULT_REDACT, export_suite, read_trace, select, write_report


def main():
    parser = argparse.ArgumentParser(description="Select and review Burr local traces before exporting pytest")
    commands = parser.add_subparsers(dest="command", required=True)
    selection = commands.add_parser("select", help="One complete local tracker application log per run")
    selection.add_argument("traces", type=Path)
    selection.add_argument("--budget", type=int, required=True)
    selection.add_argument("--output", type=Path, required=True)
    selection.add_argument("--redact-field", action="append", default=[])
    exporting = commands.add_parser("export", help="Export explicitly approved expectations")
    exporting.add_argument("review", type=Path)
    exporting.add_argument("--runner", required=True)
    exporting.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    try:
        if args.command == "select":
            files = sorted(args.traces.rglob("log.jsonl")) if args.traces.is_dir() else [args.traces]
            if not files:
                raise ValueError("No log.jsonl files found")
            if args.output.exists() or args.output.with_suffix(".html").exists():
                raise ValueError("Output already exists; choose a fresh path")
            manifest = select([read_trace(p) for p in files], args.budget, (*DEFAULT_REDACT, *args.redact_field))
            args.output.parent.mkdir(parents=True, exist_ok=True)
            args.output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n")
            write_report(manifest, args.output.with_suffix(".html"))
            print(json.dumps(manifest["report"], indent=2))
        else:
            export_suite(json.loads(args.review.read_text()), args.output, args.runner)
            print(f"Exported reviewed pytest suite to {args.output}")
    except (ValueError, OSError, KeyError, TypeError) as exc:
        parser.exit(2, f"CaseSprout: {exc}\n")


if __name__ == "__main__":
    main()
