"""Execute exported pytest against each predeclared mutant; exit nonzero if one survives.

Copyright 2026 CaseSprout contributors. Licensed under Apache-2.0.
"""
import json
import shutil
import subprocess
import sys
from pathlib import Path


def verify(demo):
    demo = Path(demo)
    outcomes = {}
    for variant in ("refund", "security", "outage"):
        target = demo / f"mutant-{variant}"
        target.mkdir(exist_ok=False)
        shutil.copyfile(demo / "suite/test_casesprout.py", target / "test_casesprout.py")
        fixture = json.loads((demo / "suite/cases.json").read_text())
        fixture["runner"] = f"burr.casesprout.support:replay_{variant}_bug"
        (target / "cases.json").write_text(json.dumps(fixture, indent=2)+"\n")
        result = subprocess.run([sys.executable, "-m", "pytest", "-q", str(target)], capture_output=True, text=True)
        (target / "pytest.log").write_text(result.stdout + result.stderr)
        outcomes[variant] = {"exit_code": result.returncode, "detected": result.returncode == 1}
    print(json.dumps(outcomes, indent=2))
    return all(v["detected"] for v in outcomes.values())


if __name__ == "__main__":
    sys.exit(0 if verify(sys.argv[1]) else 1)
