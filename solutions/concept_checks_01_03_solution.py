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
# # Instructor key · Concept check 01–03
#
# **Instructor material. Total: 20 points.** Accept equivalent precise explanations.
#
# ## 1 · Agreement versus proof (3)
#
# Agreement is numerical evidence (1), possibly reflecting a shared error (1).
# A justified enclosure lying within a common decimal rounding bin can certify the
# rounded digits (1). Width alone is not enough near a rounding boundary.
#
# ## 2 · The two neighbors (4)
#
# Above 1: 2⁻⁵²; below 1: 2⁻⁵³ (1 each). The exact sum with 2⁻⁵³ is a midpoint;
# nearest-even selects 1 (1). Epsilon is the gap 2⁻⁵², while unit roundoff is 2⁻⁵³
# in the normal-range relative-error model (1).
#
# ## 3 · Residual (3)
#
# Residual is −10⁻¹² (1); root error is 1 (1). A derivative lower bound along
# a segment to a known root relates them; residual size alone does not prove
# existence or proximity (1).
#
# ## 4 · Equivalent formulas (4)
#
# Intermediate rounding errors overwhelm the small difference (1). Horner reduces
# operations but may retain cancellation (1). Conditioning is a property of the
# function and input uncertainty, not the chosen algebraic evaluation (1).
# Use absolute error at the zero reference value (1).
#
# ## 5 · Exact endpoint evidence (3)
#
# Differentiability implies continuity here (1), so opposite signs give at least
# one root by the intermediate value theorem (1). A derivative of constant strict
# sign throughout the interval gives strict monotonicity and uniqueness (1).
#
# ## 6 · Input provenance (3)
#
# The string denotes exact 1/10 (1); the float constructor retains the previously
# rounded binary value (1). More precision affects later operations, not the
# already-lost input information (1).

