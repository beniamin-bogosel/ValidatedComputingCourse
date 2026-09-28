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
# # Concept check · Lectures 04–07 · Instructor key
#
# **20 points · 30–40 minutes.** Explain your answers; no execution or external reading is required.

# %% [markdown]
# ## 1 · Independent choices (4 points)
#
# For X = [−2, 3], give X − X and the range of x − x. Give X * X and the range of x². Explain why these answers differ.

# %% [markdown]
# **Marking key:** One point each: [−5, 5], {0}, [−6, 9], [0, 9], with the explanation of independent choices required for full credit. Interval binary operations allow different choices for their two operands; a repeated real variable denotes the same value.

# %% [markdown]
# ## 2 · Outward rounding (4 points)
#
# State directed endpoint formulas for addition. Explain why decimal input conversion is part of the proof. Does increasing precision remove uncertainty in a measured input [1, 2]?

# %% [markdown]
# **Marking key:** Two points: lower = down(a+c), upper = up(b+d), with the ordering argument. One point: the constructed interval must contain the intended decimal, not just a nearby float; conversion must preserve inclusion. One point: the original input width remains at least one.

# %% [markdown]
# ## 3 · Complete coverage (4 points)
#
# You enclose f on [0, 2/5] and [3/5, 1]. Does the hull of those two images enclose f([0, 1])? Give a counterexample using f(x)=x(1−x). What additional condition makes subdivision valid?

# %% [markdown]
# **Marking key:** One point: not necessarily. Two points: the exact images of the two outer intervals are both [0, 6/25], which miss f(1/2)=1/4. One point: retained pieces must cover the entire original domain and each local image must be a valid enclosure. Loose local bounds might accidentally cover the missing value, but the coverage argument is still absent.

# %% [markdown]
# ## 4 · Derivative bounds (4 points)
#
# State the hypotheses and formula for a mean-value enclosure. For f(x)=x² on [0, 1], show why substituting only f′(1/2) for a derivative bound is invalid.

# %% [markdown]
# **Marking key:** Two points: f is continuously differentiable on an interval containing X, m belongs to X, C encloses f(m), and D encloses every f′(x) on X; C+D(X−m) then encloses f(X). Two points: C={1/4}, the midpoint slope is 1, and the shortcut gives [−1/4, 3/4], missing f(1)=1. The full derivative interval [0, 2] is needed for that argument.

# %% [markdown]
# ## 5 · Stopping and conclusions (4 points)
#
# An adaptive routine keeps a covering list and stops when every local image has width ≤ 1/16, or when it reaches a box budget. Explain both outcomes. Must the final global image have width ≤ 1/16? What happens if difficult pieces are silently discarded?

# %% [markdown]
# **Marking key:** One point: success certifies the local width target. One point: budget exhaustion reports an unmet target while retaining a valid global enclosure. One point: no, a genuinely varying function can have a much wider range, such as x on [0, 1]. One point: discarding pieces destroys coverage and therefore the domain-wide certificate.
