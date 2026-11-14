"""JMangaBench_Hard v1.0 static Pareto charts (2026-11-02), same style as JMangaBench_Read v1.3 (its figures/pareto_plot.py). Reads
interactive_data.json. Models flagged "more" (nar-small-R16) are left out. Points beyond the axis range are drawn at the edge as a triangle.
  pareto_image.png        score vs per-image latency (batch = 1, mean)
  pareto_throughput.png   score vs max throughput (best batch size per model)"""
import json
from pathlib import Path
import matplotlib
from textwrap import fill
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import FixedLocator

D = Path(__file__).resolve().parent
plt.rcParams["font.family"] = ["Helvetica Neue", "Arial", "sans-serif"]
SURF, INK, INK2, MUTED, GRID = "#fcfcfb", "#0b0b0b", "#52514e", "#a3a29c", "#e9e8e3"
COL = {"ours": "#2a78d6", "hayai": "#eb6834", "other": "#8a8984"}
NAME = {"ours": "By the authors", "hayai": "Hayai family (AR)", "other": "Other"}
SHORT = {"Hayai v2.7 Supernova p256": "Supernova p256", "Hayai v2.5 Nova p256": "Nova p256", "Hayai v2.5 Nova p384": "Nova p384", "Hayai v2.5 Nova p512": "Nova p512"}
rows = [r for r in json.load(open(D / "interactive_data.json")) if not r["more"] and r["lat"] is not None]  # 11-10: untimed rows not drawn
for r in rows: r["label"] = SHORT.get(r["name"], r["name"])
SUB = "JMangaBench_Hard v1.0  ·  3,015 text boxes  ·  RTX 4070, fp16"

def frontier(pts, low_x):
    better = (lambda a, b: a <= b) if low_x else (lambda a, b: a >= b)
    keep = [p for p in pts if not any(better(q[0], p[0]) and q[1] >= p[1] and q != p for q in pts)]
    return sorted(keep)

def draw(xkey, out, title, xlabel, xticks, xlim, ylim, yticks, labels, note, low_x=True):
    fig, ax = plt.subplots(figsize=(11, 7.2), facecolor=SURF)
    ax.set_facecolor(SURF); ax.set_xlim(*xlim); ax.set_ylim(*ylim)
    F = frontier([(r[xkey], r["score"]) for r in rows], low_x)
    ax.plot([min(p[0], xlim[1]) for p in F], [max(p[1], ylim[0]) for p in F], color=INK2, lw=1.3, zorder=2, solid_capstyle="round")
    for g in ["ours", "hayai", "other"]:
        S = [r for r in rows if r["group"] == g and r[xkey] <= xlim[1] and r["score"] >= ylim[0]]
        ax.scatter([r[xkey] for r in S], [r["score"] for r in S], s=46, color=COL[g], edgecolors=SURF, linewidths=1.4, zorder=3, label=NAME[g])
    for r in rows:
        dx, dy = labels.get(r["id"], (22, 16)); x, y, txt = r[xkey], r["score"], r["label"]
        if y < ylim[0]:
            y = ylim[0]
            ax.scatter([x], [y], marker="v", s=70, color=COL[r["group"]], edgecolors=SURF, linewidths=1.2, zorder=3, clip_on=False)
            txt = f"{r['label']}  (score {r['score']:.1f}, below range)"
        elif x > xlim[1]:
            x = xlim[1]
            ax.scatter([x], [y], marker=">", s=70, color=COL[r["group"]], edgecolors=SURF, linewidths=1.2, zorder=3, clip_on=False)
            txt = f"{r['label']}  ({r[xkey]:,.0f} →)"
        ax.annotate(txt, (x, y), xytext=(dx, dy), textcoords="offset points", fontsize=10, color=INK, zorder=4,
                    ha="left" if dx >= 0 else "right", va="center", arrowprops=dict(arrowstyle="-", color=MUTED, lw=0.7, shrinkA=2, shrinkB=4))
    ax.xaxis.set_major_locator(FixedLocator(xticks)); ax.yaxis.set_major_locator(FixedLocator(yticks))
    ax.grid(True, color=GRID, lw=0.8); ax.set_axisbelow(True)
    for s in ["top", "right", "left"]: ax.spines[s].set_visible(False)
    ax.spines["bottom"].set_color("#c3c2b7"); ax.tick_params(colors=INK2, labelsize=10.5, length=0, pad=6)
    ax.set_xlabel(xlabel, color=INK2, fontsize=11, labelpad=10); ax.set_ylabel("Score  (mean 1 − NED, all boxes)", color=INK2, fontsize=11, labelpad=10)
    fig.text(0.07, 0.95, title, fontsize=18, color=INK); fig.text(0.07, 0.912, SUB, fontsize=11, color=INK2)
    ax.legend(loc="center right" if low_x else "lower left", frameon=False, fontsize=10, labelcolor=INK2, handletextpad=0.4)
    fig.text(0.07, 0.008, "\n".join(fill(line, width=136) for line in note.splitlines()), fontsize=8.5, color=INK2)
    fig.subplots_adjust(left=0.08, right=0.93, top=0.865, bottom=0.12)
    fig.savefig(D / out, dpi=170, facecolor=SURF); plt.close(fig)

def fr(xk, low_x):
    F = frontier([(r[xk], r["score"]) for r in rows], low_x)
    return ", ".join(next(r["name"] for r in rows if (r[xk], r["score"]) == p) for p in F)
YL, YT = (80, 98.3), list(range(80, 99, 2))
IMG_LAB = {"ns3-98k": (19, 13), "hayai_supernova_p256": (18, 20), "ar_exp": (-18, -23), "cpt_flex": (24, 18), "nar_small": (34, 4), "charspot_small": (30, -16), "nar_small_distil": (26, -4),
           "charspot_nano": (22, -14), "preview": (-24, 18), "hayai_nova_p256": (-30, -22), "hayai_nova_p384": (22, 16), "hayai_nova_p512": (26, -12),
           "hayai_v2": (-20, 18), "baberu_v12": (-26, 16), "manga_ocr": (16, 18)}
draw("lat", "pareto_image.png", "Accuracy vs. per-image latency",
     "Per-image latency (ms, batch = 1, mean over 3,015 crops, preprocessing included)   ←  faster",
     [0, 10, 20, 30, 40, 50, 60, 70, 80, 90], (0, 92), YL, YT, IMG_LAB,
     "Scores from batch = 1 outputs. mangaOCR (55.67) is below the axis range.\nPareto frontier: " + fr("lat", True) + ".")
THR_LAB = {"ns3-98k": (-20, 16), "hayai_supernova_p256": (18, 9), "ar_exp": (20, 12), "cpt_flex": (-90, 12), "nar_small": (-12, 42), "charspot_small": (-26, -16), "nar_small_distil": (-30, -14),
           "charspot_nano": (20, -14), "preview": (20, 14), "hayai_nova_p256": (22, 14), "hayai_nova_p384": (22, -10), "hayai_nova_p512": (22, -14),
           "hayai_v2": (22, -12), "baberu_v12": (22, 12), "manga_ocr": (16, 18)}
draw("thr", "pareto_throughput.png", "Accuracy vs. max throughput",
     "Max throughput (images/s, best batch size per model, 4 preprocessing workers)   faster  →",
     [0, 50, 100, 150, 200, 250, 300, 350, 400], (0, 420), YL, YT, THR_LAB,
     "Scores from batch = 1 outputs. mangaOCR (55.67) is below the axis range.\nPareto frontier: " + fr("thr", False) + ".", low_x=False)
print("ok")
