# ---
# jupyter:
#   course:
#     kind: assessment
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
# # Concept check · Lectures 01–03
#
# **Time:** 25–30 minutes. **Total:** 20 points. No code execution required.
# Answer in Markdown cells. Justify each conclusion; unexplained yes/no answers
# receive at most half credit. This is a proposed first short conceptual assessment.
#
# ## 1 · Agreement versus proof (3 points)
#
# Two computations at different precisions print the same first twelve digits.
# What does this establish? What additional evidence would certify those digits?
#
# **Answer:**
#
# ## 2 · The two neighbors (4 points)
#
# For binary64 with nearest-even rounding, give the gaps immediately above and
# below 1. Explain `1.0 + 2.0**-53 == 1.0`. Define machine epsilon and unit roundoff.
#
# **Answer:**
#
# ## 3 · Residual (3 points)
#
# A program returns x = 0 for f(x) = 10⁻¹²(x−1). Compute residual and root error.
# What hypothesis is missing from a claim that small residual implies small error?
#
# **Answer:**
#
# ## 4 · Equivalent formulas (4 points)
#
# Expanded and factored evaluations of (t−1)⁶ disagree near 1. Explain cancellation,
# why Horner's rule may not fix it, and why better evaluation does not remove input
# sensitivity. What error measure would you use at t = 1?
#
# **Answer:**
#
# ## 5 · Exact endpoint evidence (3 points)
#
# For a differentiable function on [a,b], exact calculations give f(a)<0<f(b).
# Explain what follows. What further condition could establish uniqueness?
#
# **Answer:**
#
# ## 6 · Input provenance (3 points)
#
# Explain the difference between Decimal("0.1") and Decimal(0.1). Can raising
# precision after constructing the latter recover the intended exact tenth?
#
# **Answer:**

