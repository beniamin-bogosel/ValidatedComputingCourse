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
# # Lab 07 · Use derivatives and report honest stopping
#
# **Time:** about 2 hours. **Preparation:** [Lecture 07](../notebooks/07_better_enclosures.ipynb).
#
# Implement the mean-value form and a monotonicity test. Then audit an adaptive enclosure algorithm, including its budget-limited outcome.

# %%
from fractions import Fraction
from vc.intervals import RationalInterval as Interval
from vc.enclosures import adaptive_range

def f(X):
    return X * (1 - X)

def derivative(X):
    return 1 - 2*X


# %% [markdown]
# ## Task A · Mean-value form (40 minutes)
#
# Implement $F(m)+F\prime(X)(X-m)$ with the midpoint treated as a point interval. Intersect the result with the natural enclosure; raise an error if the intersection is empty. Both evaluators must enclose the indicated function on the whole input.

# %% tags=["exercise"]
def centered(evaluate, derivative, domain):
    raise NotImplementedError("Name the center, center value, slopes, and displacement")

def combined(evaluate, derivative, domain):
    raise NotImplementedError("Intersect two valid bounds")


# %% tags=["exercise"]
domain = Interval(Fraction(1, 4), Fraction(3, 4))
true_range = Interval(Fraction(3, 16), Fraction(1, 4))
natural = f(domain)
mean_value_bound = centered(f, derivative, domain)
result = combined(f, derivative, domain)
assert true_range.is_subset_of(result)
assert result.is_subset_of(natural)
assert result.is_subset_of(mean_value_bound)
print("Natural:", natural)
print("Mean value:", mean_value_bound)
print("Intersection:", result)


# %% [markdown]
# **Written answer:** Give the mean-value theorem argument. Explain why a nonempty intersection does not establish that a supplied derivative is correct.

# %% [markdown]
# ## Task B · Monotonicity and a tempting shortcut (35 minutes)
#
# Return the hull of endpoint value enclosures if the derivative interval is nonnegative or nonpositive. Otherwise return `None` to report an inconclusive test.

# %% tags=["exercise"]
def monotone_bound(evaluate, derivative, domain):
    raise NotImplementedError("Use a derivative sign valid throughout the interval")


# %% tags=["exercise"]
small = Interval(0, Fraction(1, 4))
bound = monotone_bound(f, derivative, small)
assert bound.lo == 0 and bound.hi == Fraction(3, 16)
assert monotone_bound(f, derivative, Interval(0, 1)) is None

def square(X):
    return X.square()

def midpoint_only_slope(X):
    # Deliberately invalid as a derivative enclosure on a non-point interval.
    return Interval(2 * X.midpoint())

wrong = centered(square, midpoint_only_slope, Interval(0, 1))
print("Incorrect shortcut:", wrong)
assert not wrong.contains(1)


# %% [markdown]
# **Written answer:** Why is evaluating the derivative at the midpoint insufficient? Does `None` prove that the function is not monotone?

# %% [markdown]
# ## Task C · Audit adaptive stopping (35 minutes)
#
# Use your combined enclosure as the evaluator in the supplied `adaptive_range`. Inspect its short implementation in `vc/enclosures.py`. Check coverage explicitly after sorting the returned pieces. Compare an attainable local image-width target with a deliberately exhausted budget.

# %% tags=["exercise"]
def evaluate(X):
    return combined(f, derivative, X)

resolved = adaptive_range(evaluate, Interval(0, 1), Fraction(1, 16), max_boxes=128)
limited = adaptive_range(evaluate, Interval(0, 1), Fraction(1, 10**6), max_boxes=2)
for result in [resolved, limited]:
    pieces = sorted(result.pieces, key=lambda piece: piece.domain.lo)
    assert pieces[0].domain.lo == 0
    assert pieces[-1].domain.hi == 1
    for index in range(len(pieces) - 1):
        assert pieces[index].domain.hi == pieces[index + 1].domain.lo
    assert Interval(0, Fraction(1, 4)).is_subset_of(result.enclosure)
    print(result.status, len(pieces), result.enclosure)
assert resolved.status == "resolved"
assert all(piece.enclosure.width() <= resolved.tolerance for piece in resolved.pieces)
assert limited.status == "budget_exhausted"

# %% [markdown]
# **Written answer:** State exactly what each status means. Why are both global enclosures still valid? Why would stopping at global range width ≤ 1/16 be impossible for this function?

# %% [markdown]
# ## Submission
#
# Complete every exercise, replace the written-answer prompts with your explanations, then restart the kernel and run all cells. Include the assumptions behind each certificate and describe any inconclusive result.
