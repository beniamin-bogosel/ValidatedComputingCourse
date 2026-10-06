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

fig, ax = plt.subplots(figsize=(8.5, 2.0), layout="constrained")
points = np.linspace(0, 1, 301)
ax.axvspan(0, 0.5, color="#17678d", alpha=0.10)
ax.axvspan(0.5, 1, color="#2a815d", alpha=0.10)
ax.plot(points, points * (1-points), color="#202830", linewidth=1.6)
ax.plot([0, 0.5, 1], [0, 0.25, 0], "o", color="#b44e2b", markersize=5)
ax.text(0.19, 0.055, "nondecreasing\nf'(x) in [0, 1]", ha="center", color="#17678d")
ax.text(0.81, 0.055, "nonincreasing\nf'(x) in [-1, 0]", ha="center", color="#2a815d")
ax.set(xlim=(0, 1), ylim=(-0.01, 0.29), xticks=[0, 0.5, 1], yticks=[0, 0.125, 0.25],
       xlabel="x", ylabel="x(1-x)", title="Derivative signs justify endpoint bounds on each half")
fig.savefig(figures / "monotone_pieces.pdf")
plt.close(fig)

steps = np.logspace(-16, -1, 61)
errors = []
for step in steps:
    x = 1.0 + float(step)
    estimate = (x*x*x - 2*x + 1) / float(step)
    error = abs(estimate - 1)
    errors.append(error if error > 0 else np.nan)
fig, ax = plt.subplots(figsize=(8.5, 2.0), layout="constrained")
ax.loglog(steps, errors, "o-", markersize=2.5, linewidth=0.8, color="#17678d",
          label="binary64 difference (positive errors)")
ax.loglog(steps, 3*steps+steps**2, "--", color="#b44e2b", linewidth=1.1,
          label="exact-arithmetic truncation: 3h + h²")
ax.set(xlabel="step h", ylabel="absolute derivative error",
       title="Forward difference of x³ - 2x at x = 1")
ax.legend(fontsize=8, loc="upper center")
ax.grid(alpha=0.15)
fig.savefig(figures / "finite_difference_error.pdf")
plt.close(fig)

fig, ax = plt.subplots(figsize=(8.5, 2.0), layout="constrained")
points = np.linspace(1.2, 1.65, 301)
ax.axvspan(float(Fraction(11, 8)), float(Fraction(23, 16)),
           color="#2a815d", alpha=0.18, label="Newton interval")
ax.plot(points, points**2-2, color="#202830", linewidth=1.6, label="x² - 2")
for slope, color in [(2, "#17678d"), (4, "#b44e2b")]:
    ax.plot(points, 0.25+slope*(points-1.5), "--", linewidth=1, color=color,
            label=f"line of slope {slope}")
ax.axhline(0, color="#607080", linewidth=0.7)
ax.plot(1.5, 0.25, "o", color="#202830", markersize=4)
ax.annotate("(3/2, 1/4)", (1.5, 0.25), (1.54, 0.08), fontsize=9)
ax.set(xlim=(1.2, 1.65), ylim=(-0.8, 0.85), xlabel="x", ylabel="value",
       title="Slope bounds [2, 4] give zero crossings in [11/8, 23/16]")
ax.legend(fontsize=7.5, loc="upper left", ncol=2)
fig.savefig(figures / "interval_newton.pdf")
plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(8.5, 2.2), layout="constrained")
root_lower = Fraction(10039, 14200)
root_upper = Fraction(10043, 14200)
for ax, limits in zip(axes, [(0.695, 0.725), (0.7069, 0.70732)]):
    points = np.linspace(limits[0], limits[1], 301)
    ax.plot(points, np.sqrt(1-points*points), color="#17678d", label="circle")
    ax.plot(points, points, color="#b44e2b", label="line x = y")
    ax.add_patch(Rectangle((0.70, 0.70), 0.02, 0.02, fill=False,
                          edgecolor="#17678d", linewidth=1.4))
    ax.add_patch(Rectangle((float(root_lower), float(root_lower)),
                          float(root_upper-root_lower), float(root_upper-root_lower),
                          facecolor="#2a815d", edgecolor="#2a815d", alpha=0.25))
    ax.set(xlim=limits, ylim=limits, xlabel="x", ylabel="y")
    ax.set_aspect("equal")
    ax.ticklabel_format(useOffset=False)
    ax.tick_params(labelsize=8)
axes[0].set(title="Input box [0.70, 0.72]²")
axes[0].set_xticks([0.70, 0.71, 0.72])
axes[0].set_yticks([0.70, 0.71, 0.72])
axes[0].legend(fontsize=7, loc="upper right")
axes[1].set(title="Zoom: certified Krawczyk box")
axes[1].set_xticks([0.7070, 0.7072])
axes[1].set_yticks([0.7070, 0.7072])
fig.savefig(figures / "system_certificate.pdf")
plt.close(fig)

fig, ax = plt.subplots(figsize=(8.5, 2.0), layout="constrained")
points = np.linspace(-2, 2, 401)
ax.plot(points, points**4-2*points**2, color="#17678d", linewidth=1.5)
ax.axhline(-1, color="#607080", linewidth=0.8, linestyle="--")
ax.plot([-1, 1], [-1, -1], "o", color="#b44e2b", markersize=6)
ax.annotate("minimum at -1", (-1, -1), (-1.8, 2.8),
            arrowprops={"arrowstyle": "->", "color": "#b44e2b"}, fontsize=9)
ax.annotate("minimum at +1", (1, -1), (0.9, 2.8),
            arrowprops={"arrowstyle": "->", "color": "#b44e2b"}, fontsize=9)
ax.set(xlim=(-2, 2), ylim=(-1.5, 8.5), xticks=[-2, -1, 0, 1, 2],
       yticks=[-1, 0, 4, 8], xlabel="x", ylabel="x⁴ - 2x²",
       title="One minimum value, two minimizing locations")
fig.savefig(figures / "two_minima.pdf")
plt.close(fig)

fig, axes = plt.subplots(1, 2, figsize=(8.5, 2.1), layout="constrained")
for ax, height, title in zip(axes, [1, -1], ["Positive orientation: D = 2", "Negative orientation: D = -2"]):
    ax.fill([0, 2, 1], [0, 0, height], color="#17678d", alpha=0.10)
    ax.plot([0, 1, 2], [0, height, 0], "o-", color="#17678d", linewidth=1)
    ax.annotate("", xy=(2, 0), xytext=(0, 0),
                arrowprops={"arrowstyle": "->", "color": "#b44e2b", "lw": 1.5})
    for label, point in [("A", (0,0)), ("B", (2,0)), ("C", (1,height))]:
        ax.annotate(label, point, xytext=(5,5), textcoords="offset points", fontsize=9)
    ax.set(xlim=(-0.2, 2.3), ylim=(-1.3, 1.3), xticks=[0, 1, 2], yticks=[-1, 0, 1],
           xlabel="x", ylabel="y", title=title)
    ax.set_aspect("equal")
fig.savefig(figures / "orientation_signs.pdf")
plt.close(fig)

fig, ax = plt.subplots(figsize=(8.5, 1.45), layout="constrained")
segments = [(-3, -2.25, "#9aa7ae", "excluded"),
            (-2.25, -1.75, "#2a815d", "one root certified"),
            (-1.75, 0, "#9aa7ae", None),
            (0, 4, "#d9a65a", "unresolved")]
for left, right, color, label in segments:
    ax.add_patch(Rectangle((left, 0), right-left, 0.3,
                          facecolor=color, edgecolor="white", label=label))
ax.set(xlim=(-3.2, 4.2), ylim=(-0.1, 0.5), yticks=[],
       xticks=[-3, -2.25, -1.75, 0, 4],
       xticklabels=["-3", "-9/4", "-7/4", "0", "4"],
       title="Terminal regions: a partial root certificate on [-3, 4]")
ax.spines[["left", "bottom"]].set_visible(False)
ax.tick_params(length=0)
ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.15), ncol=3,
          fontsize=9, frameon=False)
fig.savefig(figures / "audit_partition.pdf")
plt.close(fig)

c, s = Fraction(3, 5), Fraction(4, 5)
corners = [(Fraction(-1), Fraction(-1)), (Fraction(1), Fraction(-1)),
           (Fraction(1), Fraction(1)), (Fraction(-1), Fraction(1))]
radius = Fraction(1)
box_widths, true_widths = [], []
for step in range(16):
    x_values = [point[0] for point in corners]
    box_widths.append(2*radius)
    true_widths.append(max(x_values)-min(x_values))
    if step == 2:
        second_corners = list(corners)
        second_radius = radius
    new_corners = []
    for x, y in corners:
        new_corners.append((c*x-s*y, s*x+c*y))
    corners = new_corners
    radius = (abs(c)+abs(s))*radius
assert box_widths[2] == Fraction(98,25)
assert true_widths[2] == Fraction(62,25)
fig, axes = plt.subplots(1, 2, figsize=(8.5, 2.0), layout="constrained")
closed = second_corners + [second_corners[0]]
axes[0].fill([float(point[0]) for point in closed],
             [float(point[1]) for point in closed],
             color="#17678d", alpha=0.25, label="actual rotated square")
axes[0].add_patch(Rectangle((-float(second_radius), -float(second_radius)),
                            float(2*second_radius), float(2*second_radius),
                            fill=False, edgecolor="#b44e2b", linewidth=1.3,
                            linestyle="--", label="repeated box enclosure"))
axes[0].set(xlim=(-2.2, 2.2), ylim=(-2.2, 2.2), xticks=[-2, 0, 2], yticks=[-2, 0, 2],
            title="After two exact rotations", xlabel="x", ylabel="y")
axes[0].set_aspect("equal")
axes[1].semilogy(range(16), [float(width) for width in box_widths],
                 "o-", markersize=3, color="#b44e2b", label="repeated box enclosure")
axes[1].semilogy(range(16), [float(width) for width in true_widths],
                 "o-", markersize=3, color="#17678d", label="true coordinate width")
axes[1].set(xlabel="number of rotations", ylabel="width", xticks=[0, 5, 10, 15],
            title="All updates use exact fractions")
axes[1].legend(fontsize=8, loc="upper left")
axes[1].grid(alpha=0.15)
fig.savefig(figures / "exact_wrapping.pdf")
plt.close(fig)
print("Generated the thirteen vector figures.")
