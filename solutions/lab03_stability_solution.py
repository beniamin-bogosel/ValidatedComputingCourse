# ---
# jupyter:
#   course:
#     kind: instructor_solution
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
# # Instructor solution · Lab 03 · Equivalent formulas, different answers
#
# **Time:** 2 hours plus 30–60 minutes homework. **Preparation:**
# [Lecture 03](../notebooks/03_stability.ipynb).
#
# Compare algorithms at the same inputs, quantify their error, and explain their
# limitations. Core tasks are polynomial evaluation and a quadratic reformulation;
# the summation case is a short supplied experiment.
#
# **Instructor copy.** Contains solutions and marking guidance. Do not distribute with the student lab.

# %%
import math
from fractions import Fraction
from decimal import Decimal, localcontext
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
from vc.environment import require_binary64

require_binary64()

def expanded(t):
    return t**6 - 6*t**5 + 15*t**4 - 20*t**3 + 15*t**2 - 6*t + 1

def factored(t):
    return (t - 1)**6

# %% [markdown]
# ## Task A · Audit the polynomial graph (40 minutes)
#
# Tucker's Example 1.6.2 compares the expanded polynomial above with $(t-1)^6$.
# Implement Horner evaluation. Then implement `exact_errors(t, method)`, returning
# `(absolute_error, relative_error)` as fractions. Define the reference to be the
# exact polynomial value at the **stored float** `t`. Return `None` for relative
# error when the reference is zero. Inputs and computed results are finite floats.

# %% tags=["task-polynomial"]
def horner(t):
    coefficients = [1, -6, 15, -20, 15, -6, 1]
    result = coefficients[0]
    for coefficient in coefficients[1:]:
        result = result * t + coefficient
    return result

def exact_errors(t, method):
    reference = (Fraction.from_float(t) - 1)**6
    computed = Fraction.from_float(float(method(t)))
    absolute = abs(computed - reference)
    relative = absolute / abs(reference) if reference != 0 else None
    return absolute, relative

# %% tags=["check-polynomial"]
assert horner(Fraction(3, 2)) == Fraction(1, 64)
assert exact_errors(1.0, factored) == (Fraction(0), None)
assert exact_errors(1.0, lambda t: 1.0) == (Fraction(1), None)
for t in [0.999, 1.001, 1.01]:
    for name, method in [("expanded", expanded), ("Horner", horner), ("factored", factored)]:
        absolute, relative = exact_errors(t, method)
        assert absolute >= 0 and relative >= 0
        print(t, name, "abs≈", float(absolute), "rel≈", float(relative))

# %% tags=["task-polynomial-plot"]
ts = np.linspace(0.995, 1.005, 401)
fig, ax = plt.subplots(figsize=(7, 3))
for name, method in [("expanded", expanded), ("Horner", horner), ("factored", factored)]:
    ax.plot(ts, [method(float(t)) for t in ts], label=name)
ax.set(xlabel="t", ylabel="computed p(t)")
ax.legend()
display(fig)
plt.close(fig)

# %% [markdown] tags=["answer-polynomial"]
# **Answer.** The expanded terms are much larger than their exact sum
# near t = 1. Errors in intermediate results dominate that sum; even Horner's rule
# can produce misleading signs. Exact rational evaluation confirms the identity,
# and the squared-even-power form proves nonnegativity. Factoring reduces evaluation
# error at a given stored input. It does not change the mathematical relative condition
# number |6t/(t−1)| for t ≠ 1. Uncertainty in the original input remains a separate issue.
# At the root, relative output error is undefined; use absolute error.

# %% [markdown]
# ## Task B · Recover the smaller quadratic root (40 minutes)
#
# Consider $x^2-Bx+1=0$, where $B$ is an integer at least 3. The direct smaller
# root $(B-\sqrt{B^2-4})/2$ suffers cancellation for large $B$.
#
# Implement `small_root(B)` using the product of the roots. This restricted task
# does not need a general quadratic solver. Compare with the supplied 80-digit
# Decimal approximation for `B = 10, 10**4, 10**8`.

# %%
def decimal_small_root(B):
    # Approximate comparison reference, not a rigorous enclosure.
    with localcontext() as context:
        context.prec = 80
        Bd = Decimal(B)
        return (Bd - (Bd*Bd - 4).sqrt()) / 2

# %% tags=["task-root"]
def small_root(B):
    if not isinstance(B, int) or B < 3:
        raise ValueError("This example requires an integer B >= 3")
    # Intended for the moderate test values; not an arbitrary-scale solver.
    larger = (B + math.sqrt(B*B - 4)) / 2
    return 1 / larger

# %% tags=["check-root"]
for B in [10, 10**4, 10**8]:
    naive = (B - math.sqrt(B*B - 4)) / 2
    improved = small_root(B)
    assert 0 < improved < 1
    reference = decimal_small_root(B)
    with localcontext() as context:
        context.prec = 80
        for label, value in [("direct", naive), ("reformulated", improved)]:
            relative = abs((Decimal.from_float(value) - reference) / reference)
            print(B, label, value, "approximate relative error:", f"{relative:.3E}")
        assert abs((Decimal.from_float(improved) - reference) / reference) < Decimal("1e-14")

# %% [markdown] tags=["answer-root"]
# **Answer.** The product of the two roots is 1. The larger root is
# (B + √(B²−4))/2, obtained without subtracting close quantities, so the smaller
# root is 2/(B + √(B²−4)). The Decimal reference is a high-precision approximation,
# not a proved enclosure. Near a multiple root, a small residual can coexist with
# a much larger root error; a derivative lower bound or another validation theorem
# is needed to relate the two. The reformulation does not certify the discriminant.

# %% [markdown]
# ## Task C · Summation: an improvement with limits (20 minutes)
#
# The implementations are supplied so you can focus on interpretation. The
# reference sum of the stored floats is computed exactly as a rational.

# %%
def naive_sum(values):
    total = 0.0
    for x in values:
        total += x
    return total

def kahan_sum(values):
    total = correction = 0.0
    for x in values:
        adjusted = x - correction
        updated = total + adjusted
        correction = (updated - total) - adjusted
        total = updated
    return total

examples = [[1.0] + [2.0**-54]*10000, [1e16, 1.0, -1e16]]
for values in examples:
    exact = sum((Fraction.from_float(x) for x in values), Fraction(0))
    for name, method in [("naive", naive_sum), ("Kahan", kahan_sum), ("fsum", math.fsum)]:
        result = method(values)
        print(name, result, "exact signed error:", Fraction.from_float(result) - exact)

# %% [markdown] tags=["answer-summation"]
# **Answer.** Each small term in the first example is lost by the naive
# addition to 1, while the compensation collects their effect. In [10¹⁶, 1, −10¹⁶],
# the compensation can itself be lost during the next operation, and Kahan returns
# 0 rather than the exact sum 1. These are particular executions checked against
# exact sums; they do not establish an all-input error theorem for any method.

# %% [markdown]
# ## Homework · Turn an approximation into a certificate (30–45 minutes)
#
# For $B=10$, find positive rational endpoints `lo < hi < 1` enclosing the smaller
# root of $x^2-10x+1$. Verify opposite endpoint signs exactly, then explain why the
# derivative has a constant nonzero sign there. Give the midpoint and its error
# bound. A width at most $10^{-6}$ is enough; high digit counts are not the goal.

# %% tags=["task-root-certificate"]
lo = Fraction(1010205, 10**7)
hi = Fraction(1010206, 10**7)

# %% tags=["check-root-certificate"]
assert isinstance(lo, Fraction) and isinstance(hi, Fraction)
assert 0 < lo < hi < 1
assert hi - lo <= Fraction(1, 10**6)
assert (lo*lo - 10*lo + 1) > 0 > (hi*hi - 10*hi + 1)
print("Certified bracket arithmetic:", lo, hi)

# %% [markdown] tags=["answer-root-certificate"]
# **Certificate.** Let a = 1010205/10⁷ and b = 1010206/10⁷.
# The checks above establish 0 < a < b < 1 and f(a) > 0 > f(b), where
# f(x) = x² − 10x + 1. Continuity gives a root in (a,b). On this interval,
# f′(x) = 2x − 10 < −8, so f is strictly decreasing and the root is unique there.
# Both roots are positive and their product is 1; a root below 1 is the smaller root.
# The midpoint is 2020411/20000000, and its absolute error is at most 1/20000000.
# This certificate uses exact arithmetic and stated analytic facts, rather than the
# unverified decimal approximation used to find candidate endpoints.

# %% [markdown]
# ## Optional extensions
#
# - Reproduce Rump's example from the lecture at several MPFR precisions. Compare
#   with the exact rational answer; record the evaluation order.
# - Compare forward and centered finite differences for $x^2$ at $x=1$.
#   Use the exact derivative 2 as a reference. Identify a range where smaller
#   steps worsen the result, and discuss truncation and rounding separately.
#
# **Reading:** Tucker §1.6, Examples 1.6.1–1.6.2, pp. 19–21.
