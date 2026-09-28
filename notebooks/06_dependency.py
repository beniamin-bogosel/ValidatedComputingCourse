# ---
# jupyter:
#   course:
#     kind: lecture
#   jupytext:
#     cell_metadata_filter: tags
#     formats: ipynb,py:percent
#     notebook_metadata_filter: kernelspec,jupytext,course
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python (Validated Computing)
#     language: python
#     name: validated-computing
# ---

# %% [markdown]
# # 06 · Interval extensions, dependency, and subdivision
#
# **Time:** 100–120 minutes. **Prerequisites:** Lectures 04–05.
# **Lab:** [Compare range enclosures](../labs/lab06_dependency.ipynb).
#
# Objectives: distinguish the true range from an inclusion function, explain
# dependency, prove exclusion, and enclose a whole domain by a finite covering.

# %%
from fractions import Fraction
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from IPython.display import display
from vc.intervals import RationalInterval as Interval
from vc.enclosures import subdivide, range_enclosure
from vc.arb_bridge import evaluate_ball

# %% [markdown]
# ## THEORY · An enclosure need not be the exact range
#
# For a real function f, the range on X is $f(X)=\{f(x):x\in X\}$.
# An **inclusion function** F satisfies $f(X)\subseteq F(X)$ on its admissible
# intervals. A natural interval extension follows an expression's operations,
# replacing real operations by interval ones. Its width reflects both actual
# variation and any overestimation introduced by the computation.
#
# **Inclusion isotonicity** means $X\subseteq Y\Rightarrow F(X)\subseteq F(Y)$.
# Exact endpoint operations and their well-defined natural compositions have this
# property: restricting possible operands cannot introduce new real results, and
# the endpoint formulas preserve the order of the bounds. Inclusion of the true
# range follows by the composition argument from Lecture 04.
#
# These properties are distinct. A valid enclosure method need not be isotonic;
# changing arithmetic precision or representation need not give nested results.

# %% [markdown]
# ## EXPERIMENT · One polynomial, three extensions
#
# Over the reals, all three expressions below equal $f(x)=x(1-x)$. Over intervals,
# the repetition of an unknown and the chosen operations affect the result.

# %%
def expanded_form(X):
    return X - X.square()

def product_form(X):
    return X * (1 - X)

def vertex_form(X):
    shifted = X - Fraction(1, 2)
    return Fraction(1, 4) - shifted.square()

domain = Interval(0, 1)
print("x - x²:", expanded_form(domain))
print("x(1-x):", product_form(domain))
print("1/4 - (x-1/2)²:", vertex_form(domain))

# %% [markdown]
# On [0,1], $(x-1/2)^2$ lies in [0,1/4], with both extremes attained. Therefore
# the true range is [0,1/4]. The first two enclosures are valid but wider. Here
# the vertex form is sharp because it exposes a single squared variable.
#
# **EXERCISE (10 minutes):** predict the three results on [0,1/4], then check them.
# Will the same form always be best for every function and domain?

# %% [markdown]
# ## THEORY + EXPERIMENT · Exclusion is a one-way implication
#
# If $0\notin F(X)$, the function cannot vanish in X. **Proof:** a root would
# contribute the value zero to f(X), contradicting $f(X)\subseteq F(X)$.
#
# If zero belongs to F(X), the test is inconclusive. In particular, a wide natural
# evaluation can contain zero even when the function is strictly positive.

# %%
X = Interval(-1, 1)
wide = X * X + 1
sharp = X.square() + 1
print("Independent product:", wide, "contains zero:", wide.contains(0))
print("Dedicated square:", sharp, "contains zero:", sharp.contains(0))
assert sharp.lo > 0
print("Certificate: x² + 1 > 0 throughout [-1,1].")

# %% [markdown]
# ## THEORY · A finite covering gives a global enclosure
#
# Suppose $X=X_1\cup\cdots\cup X_n$ and each $F(X_i)$ encloses f on that piece.
# Then
#
# $$f(X)\subseteq\bigcup_i F(X_i)\subseteq
# [\min_i\operatorname{lo}F(X_i),\max_i\operatorname{hi}F(X_i)].$$
#
# **Proof.** Every x in X belongs to at least one piece, so its value belongs to
# that piece's image enclosure. Taking the hull can only enlarge the set.
# Shared endpoints cause no problem for a range bound. Omitting a gap would.
#
# The code uses exact rational midpoints to preserve domain coverage. More pieces
# cost more evaluations, and a wide final range may reflect genuine variation.

# %%
def enclosure_by_pieces(evaluate, domain, depth):
    pieces = subdivide(domain, depth)
    result = evaluate(pieces[0])
    for piece in pieces[1:]:
        local_result = evaluate(piece)
        result = result.hull(local_result)
    return result

for depth in range(6):
    bound = enclosure_by_pieces(product_form, domain, depth)
    excess_width = bound.width() - Fraction(1, 4)
    print("depth:", depth, "pieces:", 2**depth,
          "range:", bound, "excess width:", excess_width)
    assert Interval(0, "1/4").is_subset_of(bound)

# %% [markdown]
# We know the exact range here, so we can quantify overestimation. For a general
# function, a sample minimum and maximum are not an exact reference range.

# %%
pieces = subdivide(domain, 3)
fig, ax = plt.subplots(figsize=(7, 3.5))
for piece in pieces:
    image = product_form(piece)
    rectangle = Rectangle((float(piece.lo), float(image.lo)),
                          float(piece.width()), float(image.width()),
                          facecolor="tab:blue", edgecolor="tab:blue", alpha=0.2)
    ax.add_patch(rectangle)
xs = np.linspace(0, 1, 201)
ax.plot(xs, xs*(1-xs), color="black", label="sampled curve (illustration)")
ax.set(xlim=(0, 1), ylim=(-0.03, 0.4), xlabel="x", ylabel="f(x)",
       title="Each rectangle encloses the graph over its domain piece")
ax.legend()
display(fig)
plt.close(fig)

# %% [markdown]
# ## EXPERIMENT · More arithmetic bits do not remove dependency
#
# Even exact rational endpoint arithmetic produced [0,1] for the product form on
# [0,1]. Thus that width was not caused by rounding. Increasing precision cannot
# recover the relation between the occurrences of x. Reformulation and subdivision
# attack a different source of overestimation than arithmetic precision does.

# %% [markdown]
# ## EXPERIMENT · Elementary functions through Arb
#
# For f(x) = (sin(x) − x² + 1) cos(x) on [0,1/2], an elementary inclusion
# computation can already exclude zero. This is adapted from Tucker, Example 3.1.4.
# The callback must use Arb operations throughout; the bridge returns rational
# endpoint bounds so our certificate comparisons remain exact.

# %%
def trigonometric_function(x):
    sine = x.sin()
    cosine = x.cos()
    return (sine - x*x + 1) * cosine

trig_domain = Interval(0, "1/2")
bound = evaluate_ball(trigonometric_function, trig_domain, precision=100)
assert bound.lo > 0
print("Rigorous lower bound, displayed approximately:", float(bound.lo))
print("Certificate: the function is positive on [0,1/2].")

# %% [markdown]
# The assertion uses the exact rational lower endpoint, not its decimal display.
# The claim depends on Arb's rigorous operations and the function's being defined
# on the input ball, which may be slightly wider than the original interval.
#
# ## Failure case · A mathematical domain restriction
#
# The expression x/x equals 1 for nonzero x, but the original expression is
# undefined at zero. Replacing it by a constant on a domain containing zero would
# change the mathematical problem. Similarly, interval evaluation of log requires
# a suitable positive input enclosure.

# %%
def logarithm(x):
    return x.log()

try:
    evaluate_ball(logarithm, Interval(-2, -1))
except ValueError as error:
    print("No finite real enclosure returned:", error)

# %% [markdown]
# ## Recap and reading
#
# An enclosure is a set guarantee; sharpness is a separate question. A useful
# range method combines valid local evaluations with complete domain coverage.
# A failure to exclude zero does not prove a root, and numerical samples do not
# replace covering arguments.
#
# **Exit ticket:** explain which of precision, reformulation, and subdivision
# addresses rounding error, variable dependency, and actual function variation.
#
# **Reading:** Tucker §3.1, pp. 46–54; Examples 3.1.1–3.1.4 and Theorem 3.8.
# Next: [Lecture 07](07_better_enclosures.ipynb).

