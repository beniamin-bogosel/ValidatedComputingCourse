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
# # Capstone peer audit
#
# **Reviewer:** [name] · **Author:** [name] · **Project notebook:** [path] · **Date:** [date]
#
# **Time:** 45–60 minutes for the first review, followed by author revisions. Use [Lecture 13](../notebooks/13_certificate_audit.ipynb) as guidance. This notebook is a record of your review, not an automatic correctness checker.

# %% [markdown]
# ## 1 · Claim as understood by the reviewer
#
# Restate the mathematical claim, domain, inputs, uncertainty model, and accuracy target. Separate local and global conclusions. Identify the meaning of every status in the author's final report.

# %% [markdown]
# ## 2 · Reproduction
#
# Record the interpreter and library versions, input encoding, precision, and runtime. Restart the project kernel and run all cells. Record discrepancies and the exact notebook/cell involved. Do saved certificate data agree with a newly generated run?

# %% [markdown]
# ## 3 · Proof conditions
#
# Name the theorem or invariant. For each premise, identify its source: problem assumption, analytic proof, or computed bound. Inspect input conversion, elementary-function domains, rounding/enclosure operations, and output conversion. Check a limiting or inconclusive example as well as the successful case.

# %% [markdown]
# ## 4 · Coverage and decisions
#
# For a search, account for retained, certified, excluded, and unresolved regions. For geometry, distinguish exact and uncertain coordinates. For mirrors, check all candidate mirrors, the reachable-region argument, collision ordering, departure, and the final-time comparison. Explain what prevents an omitted branch from invalidating the claim.

# %% [markdown]
# ## 5 · Findings
#
# | Cell or record | Finding and evidence | Effect on the claim | Suggested correction |
# |---|---|---|---|
# | [reference] | [observation] | [which conclusion is affected] | [specific action] |
#
# Distinguish a false mathematical claim from a claim whose supplied proof is incomplete.

# %% [markdown]
# ## 6 · Review outcome
#
# Choose and justify: **supported under stated assumptions**, **needs correction**, or **inconclusive**. State precisely which code, computations, and arguments you checked; list any remaining review limits.

# %% [markdown]
# ## 7 · Author response and final revision
#
# Respond to each finding. Record the changed cells or certificate fields, rerun results, and any narrowing of the final claim. Include the revised conclusion here so that the audit and final submission agree.
