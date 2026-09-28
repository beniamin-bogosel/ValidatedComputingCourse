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
# # Concept check · Lectures 08–11
#
# **20 points · 35–45 minutes.** Explain the mathematical claims; no computation is required.

# %% [markdown]
# ## 1 · Differentiation guarantees (4 points)
#
# Explain why forward-mode AD with float components is not automatically validated differentiation. State the additional assumptions needed for interval AD. What goes wrong with choosing one branch from an interval midpoint?

# %% [markdown]
# **Answer:**

# %% [markdown]
# ## 2 · Interval Newton (4 points)
#
# State the interval Newton image and its hypotheses. Explain what empty intersection proves and what strict interior inclusion proves. Does a derivative interval excluding zero alone prove existence?

# %% [markdown]
# **Answer:**

# %% [markdown]
# ## 3 · Search completeness (4 points)
#
# A search returns three certified intervals and two unresolved intervals. It contracts some boxes and reaches a step budget. What can it claim? Describe what must be preserved at contraction, splitting, and budget exhaustion. Can overlapping root enclosures simply be counted?

# %% [markdown]
# **Answer:**

# %% [markdown]
# ## 4 · A local system certificate (4 points)
#
# For T(x)=x−Rf(x), give the Krawczyk enclosure and the conservative test taught in the course. Explain the role of R and identify the region where uniqueness is established.

# %% [markdown]
# **Answer:**

# %% [markdown]
# ## 5 · Preserve all global minimizers (4 points)
#
# Given a feasible point z and an enclosure F(z)=[l,u], which endpoint is a safe incumbent? State the pruning rule when all minimizers must be retained. Explain why a zero value gap can coexist with wide candidate boxes, and what survives budget exhaustion.

# %% [markdown]
# **Answer:**
