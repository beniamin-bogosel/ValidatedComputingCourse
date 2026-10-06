"""Make vector figures from the course examples; no generated artwork."""
from fractions import Fraction
from pathlib import Path
import os

ROOT = Path(__file__).resolve().parent
os.environ.setdefault("MPLCONFIGDIR", str(ROOT.parents[1] / "build" / "pdf_matplotlib"))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
import numpy as np

plt.rcParams.update({"font.size": 10, "axes.spines.top": False,
                     "axes.spines.right": False, "pdf.fonttype": 42})
figures = ROOT / "figures"
figures.mkdir(exist_ok=True)

fig, ax = plt.subplots(figsize=(8.5, 1.45), layout="constrained")
left = [1 + k/8 for k in range(8)]
right = [2 + k/4 for k in range(9)]
ax.hlines(0, 0.95, 4.08, color="#607080", linewidth=1)
ax.plot(left, [0]*len(left), "|", color="#17678d", markersize=17, markeredgewidth=2)
ax.plot(right, [0]*len(right), "|", color="#b44e2b", markersize=17, markeredgewidth=2)
ax.annotate("step = 1/8", xy=(1.5, 0.02), xytext=(1.5, 0.3), ha="center", color="#17678d")
ax.annotate("step = 1/4", xy=(3, 0.02), xytext=(3, 0.3), ha="center", color="#b44e2b")
ax.set(xlim=(0.92, 4.12), ylim=(-0.2, 0.62), yticks=[], xticks=[1, 1.5, 2, 3, 4],
       title="A toy format with four significant binary digits")
ax.spines[["left", "bottom"]].set_visible(False)
ax.tick_params(axis="x", length=0)
fig.savefig(figures / "toy_spacing.pdf")
plt.close(fig)

points = np.linspace(0.995, 1.005, 401)
expanded = points**6 - 6*points**5 + 15*points**4 - 20*points**3 + 15*points**2 - 6*points + 1
horner = np.ones_like(points)
for coefficient in [-6, 15, -20, 15, -6, 1]:
    horner = horner * points + coefficient
factored = (points - 1)**6
exact_values = [(Fraction.from_float(float(t)) - 1)**6 for t in points]
reference = np.array([float(value) for value in exact_values])
fig, axes = plt.subplots(1, 2, figsize=(9, 2.3), layout="constrained")
colors = ["#b44e2b", "#17678d", "#2a815d"]
for label, values, color in zip(["expanded", "Horner", "factored"],
                               [expanded, horner, factored], colors):
    axes[0].plot(points, values, color=color, label=label, linewidth=0.9, alpha=0.85)
    relative_errors = []
    for value, exact in zip(values, exact_values):
        if exact == 0:
            relative_errors.append(float("nan"))
        else:
            error = abs(Fraction.from_float(float(value)) - exact) / exact
            relative_errors.append(float(error) if error else float("nan"))
    axes[1].semilogy(points, relative_errors, color=color, linewidth=0.9)
axes[0].axhline(0, color="black", linewidth=0.4)
axes[0].set(title="Sampled binary64 values", ylabel="computed value", xlabel="t")
axes[0].legend(fontsize=8, loc="upper right", framealpha=0.95)
axes[0].ticklabel_format(axis="y", style="sci", scilimits=(0, 0))
axes[1].set(title="Error at the same stored input", ylabel="relative evaluation error", xlabel="t")
for ax in axes:
    ax.set_xticks([0.995, 1, 1.005])
    ax.grid(alpha=0.18)
fig.savefig(figures / "polynomial_cancellation.pdf")
plt.close(fig)

fig, ax = plt.subplots(figsize=(8.5, 1.65), layout="constrained")
for height in [0, 1]:
    ax.hlines(height, -0.15, 3.15, color="#bac3ca", linewidth=1)
for left, right in [(0, 1), (2, 3)]:
    ax.plot([left, right], [1, 1], "o-", color="#17678d", linewidth=5, markersize=6)
ax.plot([0, 3], [0, 0], "o-", color="#b44e2b", linewidth=5, markersize=6)
ax.text(1.5, 1.12, "gap excluded", ha="center", fontsize=9)
ax.set(xlim=(-0.2, 3.2), ylim=(-0.35, 1.5), xticks=[0, 1, 2, 3],
       yticks=[0, 1], yticklabels=["interval hull", "set union"])
ax.spines[["left", "bottom"]].set_visible(False)
ax.tick_params(length=0)
fig.savefig(figures / "interval_union_hull.pdf")
plt.close(fig)

fig, ax = plt.subplots(figsize=(8.5, 1.6), layout="constrained")
lower, exact, upper = Fraction(12, 128), Fraction(1, 10), Fraction(13, 128)
ax.hlines(0, 0.0925, 0.103, color="#607080", linewidth=1)
ax.plot([float(lower), float(upper)], [0, 0], "|-", color="#17678d",
        linewidth=3, markersize=22, markeredgewidth=2)
ax.plot(float(exact), 0, "o", color="#b44e2b", markersize=7)
ax.annotate("exact 1/10", (float(exact), 0.03), (0.0985, 0.55),
            arrowprops={"arrowstyle": "->", "color": "#b44e2b"},
            ha="center", color="#b44e2b")
ax.text(float(lower), -0.19, "down: 12/128", ha="center", color="#17678d")
ax.text(float(upper), -0.19, "up: 13/128", ha="center", color="#17678d")
ax.set(xlim=(0.0915, 0.104), ylim=(-0.48, 0.9), xticks=[], yticks=[],
       title="Outward enclosure with four significant binary digits")
ax.spines[["left", "bottom"]].set_visible(False)
fig.savefig(figures / "outward_rounding.pdf")
plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(9, 2.15), layout="constrained")
points = np.linspace(0, 1, 301)
for ax, count in zip(axes, [2, 8]):
    upper_bound = Fraction(0)
    for index in range(count):
        left = Fraction(index, count)
        right = Fraction(index + 1, count)
        lower = left * (1 - right)
        upper = right * (1 - left)
        upper_bound = max(upper_bound, upper)
        ax.add_patch(Rectangle((float(left), float(lower)), float(right - left),
                               float(upper - lower), facecolor="#17678d",
                               edgecolor="#17678d", alpha=0.20))
    ax.plot(points, points * (1 - points), color="#202830", linewidth=1.5)
    ax.axhline(float(upper_bound), color="#b44e2b", linestyle="--", linewidth=1)
    ax.set(xlim=(0, 1), ylim=(-0.02, 0.55), xticks=[0, 0.5, 1],
           yticks=[0, 0.25, 0.5], xlabel="input x",
           title=f"{count} pieces: global bound [0, {upper_bound}]")
axes[0].set_ylabel("function value")
fig.savefig(figures / "subdivision_enclosures.pdf")
plt.close(fig)
print("Generated the five vector figures.")
