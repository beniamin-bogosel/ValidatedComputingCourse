# ---
# jupyter:
#   course:
#     kind: student_lab
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
# # Lab 01 · Numerical crime scene
#
# **Time:** 2 hours, including discussion; about 45 minutes of coding.
# **Preparation:** [Lecture 01](../notebooks/01_intro.ipynb).
# **Submit:** this notebook with implementations, executed checks, and written answers.
#
# The aim is to state what the evidence supports. Use exact rational arithmetic
# when possible. `float(...)` is acceptable for displaying an error, not for making
# an exact comparison. Cells tagged **exercise** need completion; diagnostic cells
# with the same tag should be run after the corresponding implementation.

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

# %% tags=["exercise", "task-representation"]
def representation_error(value, intended):
    raise NotImplementedError("Return an exact Fraction; do not compare rounded decimals")

# %% tags=["exercise", "check-representation"]
assert representation_error(0.5, Fraction(1, 2)) == 0
error = representation_error(0.1, Fraction(1, 10))
assert isinstance(error, Fraction)
assert Fraction.from_float(0.1) == Fraction(1, 10) + error
for value, intended in [(0.1, Fraction(1, 10)), (0.3, Fraction(3, 10)), (0.5, Fraction(1, 2))]:
    print(value, representation_error(value, intended))

# %% [markdown] tags=["answer-representation"]
# **Written answer:** Why does `0.1 == 1/10` fail to test the stated claim?
# What does your exact calculation establish? Replace this paragraph with your answer.

# %% [markdown]
# ## Case B · The reassuring residual (25 minutes)
#
# **Claim to investigate:** “A residual smaller than $10^{-10}$ means the root
# error is smaller than $10^{-10}$.” Use $h(x)=10^{-12}(x-1)$ at $x=0$ to test
# the claim exactly. Compare residual and distance to the unique root.

# %% tags=["exercise", "task-residual"]
# Assign exact Fraction values. No approximate root finder is needed.
residual = None
root_error = None

# %% tags=["exercise", "check-residual"]
assert isinstance(residual, Fraction) and isinstance(root_error, Fraction)
assert abs(residual) < Fraction(1, 10**10)
assert root_error > Fraction(1, 10**10)
print("Residual:", residual, "distance to the root:", root_error)

# %% [markdown] tags=["answer-residual"]
# **Written answer:** Identify an additional hypothesis that could connect a
# residual with root error. Does that hypothesis alone prove a root exists?

# %% [markdown]
# ## Case C · Produce a certificate (35 minutes)
#
# **Claim:** $x^2-3$ has exactly one root in $[1.732,1.733]$.
# Store these endpoints as exact rationals. Implement the endpoint checks below.
# The function should return True only for ordered positive endpoints with strict
# opposite signs. For this lab it accepts `Fraction` endpoints and only handles
# the function $x^2-3$; it is not a general root-isolation algorithm.

# %% tags=["exercise", "task-certificate"]
def sqrt3_bracket_verified(a, b):
    raise NotImplementedError("Check ordering, positivity, and exact endpoint signs")

# %% tags=["exercise", "check-certificate"]
lo, hi = Fraction(1732, 1000), Fraction(1733, 1000)
assert sqrt3_bracket_verified(lo, hi)
assert not sqrt3_bracket_verified(hi, lo)
assert not sqrt3_bracket_verified(Fraction(2), Fraction(3))
assert not sqrt3_bracket_verified(Fraction(-2), Fraction(2))
print("Endpoint checks passed for:", lo, hi)

# %% [markdown] tags=["answer-certificate"]
# **Certificate:** State the function and domain, the exact signs, the continuity
# argument, and the uniqueness argument. Give a midpoint and a rigorous absolute
# error bound. Explain why the rejected interval `[-2, 2]` need not be root-free.

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
# **Written answer:** Give the missing point and distinguish evidence from a
# domain-wide statement. Would using 1,000 samples automatically repair the proof?

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

