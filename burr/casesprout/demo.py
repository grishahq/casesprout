"""Reproduce controlled runs, independent review fixtures and equal-budget experiment.

Copyright 2026 CaseSprout contributors. Licensed under Apache-2.0.
"""
import argparse
import contextlib
import io
import json
import logging
import random
from pathlib import Path

from .core import canonical, digest, export_suite, read_trace, redact, select
from .support import run

POLICY = json.loads(Path(__file__).with_name("support_policy.json").read_text())


def approve_from_policy(manifest):
    """Demo-only explicit oracle, specified separately from workflow and observations.

    Real applications require a developer to review their own policy and expectations.
    """
    for case in manifest["cases"]:
        rule = POLICY["cases"][case["inputs"]["request"]["topic"]]
        case["approval"] = {"approved": True, "reviewer": "controlled-demo-policy-v1",
                            "basis": "support_policy.json, specified independently; not historical output",
                            "expected": {"output": None if rule["error"] else {
                                "request": case["inputs"]["request"], "disposition": rule["disposition"]},
                                         "error": rule["error"]}}
    return manifest


def catches(cases, mutation):
    for case in cases:
        expected = case["approval"]["expected"]
        try:
            actual = run(case["inputs"], variant=mutation)
        except Exception as exc:
            if type(exc).__name__ != expected["error"]:
                return True
        else:
            if expected["error"] is not None or actual != expected["output"]:
                return True
    return False


def metrics(cases):
    caught = [m for m in POLICY["mutations"] if catches(cases, m)]
    return {"sample_size": len(cases), "observed_paths_covered": len({canonical(c["path"]) for c in cases}),
            "injected_regressions_detected": len(caught), "detected_mutations": caught}


def generate(target):
    target = Path(target)
    target.mkdir(parents=True, exist_ok=False)
    storage = target / "traces"
    for topic, count in POLICY["corpus"].items():
        for index in range(count + (POLICY["duplicate_faq_runs"] if topic == "faq" else 0)):
            identity = index % count
            request = {"topic": topic, "ticket": f"{topic}-{identity:03}", "email": "synthetic@example.invalid"}
            try:
                # Historical security outputs are intentionally wrong; acceptance policy is independent.
                run({"request": request}, variant="historical_security_bug", storage=storage, app_id=f"{topic}-{index:03}")
            except ConnectionError:
                pass
    traces = [read_trace(p) for p in sorted(storage.rglob("log.jsonl"))]
    manifest = select(traces, POLICY["sample_size"])
    (target / "review-required.json").write_text(json.dumps(manifest, indent=2)+"\n")
    approved = approve_from_policy(manifest)
    (target / "reviewed.json").write_text(json.dumps(approved, indent=2)+"\n")
    export_suite(approved, target / "suite", "burr.casesprout.support:replay")
    unique = {digest(c): c for c in traces}
    population = [unique[key] for key in sorted(unique)]
    def sample(seed):
        chosen = random.Random(seed).sample(population, POLICY["sample_size"])
        return approve_from_policy(select(chosen, POLICY["sample_size"]))["cases"]
    random_cases = sample(POLICY["random_seed"])
    random_report = dict(approved["report"])
    selected_signatures = {canonical([c["path"], c["error"]]) for c in random_cases}
    all_signatures = {canonical([c["path"], c["error"]]) for c in traces}
    random_report.update(selection="seeded random without replacement from same unique population",
        selected_paths=len({canonical(c["path"]) for c in random_cases}),
        selected_path_error_strata=len(selected_signatures),
        uncovered_strata=[json.loads(s) for s in sorted(all_signatures - selected_signatures)])
    export_suite({**approved, "report": random_report, "cases": random_cases}, target / "random-suite", "burr.casesprout.support:replay")
    sensitivity = [metrics(sample(seed)) for seed in range(POLICY["sensitivity_seeds"])]
    results = {"policy_sha256": digest(POLICY), "corpus_runs": len(traces), "unique_runs": len(unique),
               "method": "Equal size without replacement from same unique population; no expectations used for selection",
               "random_seed": POLICY["random_seed"], "sample_size": POLICY["sample_size"],
               "casesprout": metrics(approved["cases"]), "seeded_random": metrics(random_cases),
               "random_sensitivity": {"seeds": len(sensitivity),
                    "mean_paths_covered": sum(m["observed_paths_covered"] for m in sensitivity)/len(sensitivity),
                    "mean_regressions_detected": sum(m["injected_regressions_detected"] for m in sensitivity)/len(sensitivity),
                    "all_regressions_detected_samples": sum(m["injected_regressions_detected"] == len(POLICY["mutations"]) for m in sensitivity)},
               "limits": ["Synthetic controlled deterministic Burr runs; not model or production results",
                          "Mutations target rare known paths by design; path selection is favored by this workload",
                          "Observed paths only; no guarantee of semantic, branch or unseen-path coverage",
                          "Exact output equality suits this demo, not every nondeterministic agent"]}
    (target / "results.json").write_text(json.dumps(results, indent=2)+"\n")
    return results


def main():
    parser = argparse.ArgumentParser(description="Generate controlled Burr support traces and reviewed suite")
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    logging.disable(logging.CRITICAL)
    with contextlib.redirect_stderr(io.StringIO()):
        results = generate(args.output)
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
