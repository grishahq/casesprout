"""Plot saved measurements without inventing values.
Copyright 2026 CaseSprout contributors. Licensed under Apache-2.0.
"""
import json
from pathlib import Path
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

root = Path(__file__).resolve().parents[1]
data = json.loads((root / "evidence/demo/results.json").read_text())
plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 13})
fig, axes = plt.subplots(1, 2, figsize=(13, 6), facecolor="#f5f3ed")
for ax, metric, title, maximum in zip(axes,
    ["observed_paths_covered", "injected_regressions_detected"],
    ["Observed paths covered (out of 5)", "Injected regressions detected (out of 3)"], [5, 3]):
    values = [data["casesprout"][metric], data["seeded_random"][metric]]
    bars = ax.bar(["CaseSprout", "Random · seed 7"], values, color=["#235a47", "#bd843a"], width=.58)
    ax.set_ylim(0, maximum+1)
    ax.set_yticks(range(maximum+1))
    ax.set_title(title, fontsize=15, pad=18)
    ax.set_facecolor("#f5f3ed")
    ax.spines[["top", "right"]].set_visible(False)
    for bar, value in zip(bars, values):
        ax.text(bar.get_x()+bar.get_width()/2, value+.12, str(value), ha="center", fontsize=23, weight="bold", color="#173d36")
fig.suptitle("Five tests each. Different observed coverage.", fontsize=23, weight="bold", color="#173d36", y=.97)
fig.text(.5,.07,"110 controlled Burr runs → 100 unique · same population · five cases each\nSynthetic workload targets rare paths; no claim of general superiority.", ha="center", fontsize=12, color="#173d36")
fig.subplots_adjust(top=.78, bottom=.25, wspace=.35)
fig.savefig(root / "campaign/assets/04-equal-budget-experiment.png", dpi=170)
