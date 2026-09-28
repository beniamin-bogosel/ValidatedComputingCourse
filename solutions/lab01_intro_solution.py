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
# # Instructor solution · Lab 01 · Numerical crime scene
#
# **Time:** 2 hours, including discussion; about 45 minutes of coding.
# **Preparation:** [Lecture 01](../notebooks/01_intro.ipynb).
# **Submit:** this notebook with implementations, executed checks, and written answers.
#
# The aim is to state what the evidence supports. Use exact rational arithmetic
# when possible. `float(...)` is acceptable for displaying an error, not for making
# an exact comparison. Cells tagged **exercise** need completion; diagnostic cells
# with the same tag should be run after the corresponding implementation.
#
# **Instructor copy.** Contains solutions and marking guidance. Do not distribute with the student lab.

# %%
import math
from fractions import Fraction
from vc.environment import require_binary64

require_binary64()
print("Setup complete.")

# %% [markdown]
# ## Case A · Where did the tenth go? (25 minutes)
#
# **Claim to investigate:** “The literal `0.1` equals the rational $1/10$.”
# First run the ordinary computation. Explain the difference between what is shown
# on screen and the exact value stored.

# %%
print("Short display:", 0.1)
print("Longer display:", format(0.1, ".55f"))
print("Apparent equality:", 0.1 == 1 / 10)

# %% [markdown]
# Implement `representation_error(value, intended)` to return the **signed exact
# error** of a finite float relative to a `Fraction`. Then determine the sign of
# the errors for 0.1, 0.3, and 0.5. A useful tool is `Fraction.from_float`.

# %% tags=["task-representation"]
def representation_error(value, intended):
    return Fraction.from_float(value) - intended

# %% tags=["check-representation"]
assert representation_error(0.5, Fraction(1, 2)) == 0
error = representation_error(0.1, Fraction(1, 10))
assert isinstance(error, Fraction)
assert Fraction.from_float(0.1) == Fraction(1, 10) + error
for value, intended in [(0.1, Fraction(1, 10)), (0.3, Fraction(3, 10)), (0.5, Fraction(1, 2))]:
    print(value, representation_error(value, intended))

# %% [markdown] tags=["answer-representation"]
# **Answer.** Both sides of `0.1 == 1/10` are floats representing the same
# rounded rational. That equality does not compare either side with exact 1/10.
# The exact error is positive for 0.1, negative for 0.3, and zero for 0.5.
# The calculation establishes the signed representation error for each stored value.

# %% [markdown]
# ## Case B · The reassuring residual (25 minutes)
#
# **Claim to investigate:** “A residual smaller than $10^{-10}$ means the root
# error is smaller than $10^{-10}$.” Use $h(x)=10^{-12}(x-1)$ at $x=0$ to test
# the claim exactly. Compare residual and distance to the unique root.

# %% tags=["task-residual"]
residual = Fraction(1, 10**12) * (Fraction(0) - 1)
root_error = abs(Fraction(0) - 1)

# %% tags=["check-residual"]
assert isinstance(residual, Fraction) and isinstance(root_error, Fraction)
assert abs(residual) < Fraction(1, 10**10)
assert root_error > Fraction(1, 10**10)
print("Residual:", residual, "distance to the root:", root_error)

# %% [markdown] tags=["answer-residual"]
# **Answer.** The exact residual is −1/10¹²; the root distance is 1.
# If a root is known to exist and the derivative magnitude is bounded below by
# m > 0 along the segment joining the candidate to that root, the mean value theorem
# gives distance ≤ |residual|/m. Here m = 10⁻¹², which gives 1, not 10⁻¹⁰.
# A derivative lower bound alone does not establish existence.

# %% [markdown]
# ## Case C · Produce a certificate (35 minutes)
#
# **Claim:** $x^2-3$ has exactly one root in $[1.732,1.733]$.
# Store these endpoints as exact rationals. Implement the endpoint checks below.
# The function should return True only for ordered positive endpoints with strict
# opposite signs. For this lab it accepts `Fraction` endpoints and only handles
# the function $x^2-3$; it is not a general root-isolation algorithm.

# %% tags=["task-certificate"]
def sqrt3_bracket_verified(a, b):
    return 0 < a < b and a*a - 3 < 0 < b*b - 3

# %% tags=["check-certificate"]
lo, hi = Fraction(1732, 1000), Fraction(1733, 1000)
assert sqrt3_bracket_verified(lo, hi)
assert not sqrt3_bracket_verified(hi, lo)
assert not sqrt3_bracket_verified(Fraction(2), Fraction(3))
assert not sqrt3_bracket_verified(Fraction(-2), Fraction(2))
print("Endpoint checks passed for:", lo, hi)

# %% [markdown] tags=["answer-certificate"]
# **Certificate.** Let a = 433/250 and b = 1733/1000. Exact arithmetic
# gives a² − 3 = −11/62500 and b² − 3 = 3289/1000000. Continuity establishes
# a root in (a,b); the derivative 2x is positive throughout [a,b], establishing
# uniqueness. The midpoint is 693/400 and the absolute error is at most 1/2000.
# This proves exactly one root in that interval, not exactly one real root overall.
# The rejected interval [−2,2] contains both ±√3: our positive-bracket test is a
# sufficient test with restricted scope, not a complete decision procedure.

# %% [markdown]
# ## Case D · A positive grid (15 minutes)
#
# Run the exact samples below. Explain why they do not prove strict positivity of
# the function throughout `[0, 1]`. State a counterexample point exactly.

# %%
grid = [Fraction(k, 10) for k in range(11)]
sample_values = [(t - Fraction(2, 7))**2 for t in grid]
assert all(v > 0 for v in sample_values)
print("All grid values are positive; smallest sampled value:", min(sample_values))

# %% [markdown] tags=["answer-grid"]
# **Answer.** The value at the exact point 2/7 is zero. The finite grid misses
# it. A grid of k/1000 also misses 2/7, and in any case sample positivity is not
# positivity everywhere. This function is nonnegative everywhere by its squared
# form, but it is not strictly positive on [0,1].

# %% [markdown]
# ## Homework and optional extension
#
# **Homework (20 minutes):** choose one false claim above and rewrite it as a true,
# precisely scoped statement. Identify the mathematical argument and the trusted
# arithmetic supporting it.
#
# **Optional:** enclose $\sqrt{3}$ more tightly with rational endpoints. Derive a
# stopping criterion from interval width; do not use matching printed digits as
# the criterion. This anticipates later validated root-finding labs.
#
# **Submission checklist:** restart and run all cells; retain outputs; replace the
# four written-answer placeholders; identify any unresolved task honestly.

