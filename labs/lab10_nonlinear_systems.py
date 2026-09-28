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
# # Lab 10 · Implement a local Krawczyk certificate
#
# **Preparation:** [Lecture 10](../notebooks/10_nonlinear_systems.ipynb).
#
# **Time:** about 2 hours. Matrix helpers and interval AD are supplied. Implement the Krawczyk image and the conservative decision test; no exhaustive search is required.

# %%
from fractions import Fraction
from vc.intervals import RationalInterval as Interval
from vc.autodiff import jacobian2
from vc.systems import matrix_product, matrix_vector, inverse2, midpoint_inverse, row_sum_bound

def system(x, y):
    return [x*x+y*y-1, x-y]

def jacobian(box):
    return jacobian2(system, box)


# %% [markdown]
# ## Task A · Enclose the fixed-point map (45 minutes)
#
# Given a point matrix R and box X, compute E=I−R J(X) and K=m−R F(m)+E(X−m). Return `(image, remainder)`. Use the provided matrix loops; keep the intermediate objects named.

# %% tags=["exercise"]
def student_image(function, jacobian, box, R):
    raise NotImplementedError("Build center, residual, remainder, correction, and spread")


# %% tags=["exercise"]
box = [Interval("0.7", "0.72"), Interval("0.7", "0.72")]
R = midpoint_inverse(jacobian(box))
image, remainder = student_image(system, jacobian, box, R)
print("K:", image)
print("E:", remainder)
for part in image:
    assert 2*part.lo**2 < 1 < 2*part.hi**2
assert row_sum_bound(remainder) == Fraction(1, 71)


# %% [markdown]
# **Written response:** Why must every root in X also lie in K(X)? Why is a point preconditioner allowed to be only an approximate inverse?

# %% [markdown]
# ## Task B · Classify the result (35 minutes)
#
# Reject a singular R using `inverse2(R)`. Return `(status, q)` with status `excluded` if one coordinate image misses its input interval; `unique_root` if every image coordinate is strictly inside and q<1; otherwise `inconclusive`. Use `row_sum_bound` for q. Assume a box with positive side widths.

# %% tags=["exercise"]
def classify(box, image, remainder, R):
    raise NotImplementedError("Check nonsingularity, disjointness, inclusion, and contraction")


# %% tags=["exercise"]
status, q = classify(box, image, remainder, R)
assert status == "unique_root" and q < 1
print(status, q)
negative_box = [Interval("-0.72", "-0.7"), Interval("-0.72", "-0.7")]
negative_R = midpoint_inverse(jacobian(negative_box))
negative_image, negative_remainder = student_image(system, jacobian, negative_box, negative_R)
assert classify(negative_box, negative_image, negative_remainder, negative_R)[0] == "unique_root"
outside_box = [Interval(2, 3), Interval(2, 3)]
outside_R = midpoint_inverse(jacobian(outside_box))
outside_image, outside_remainder = student_image(system, jacobian, outside_box, outside_R)
assert classify(outside_box, outside_image, outside_remainder, outside_R)[0] == "excluded"

# %% [markdown]
# **Written response:** State the hypotheses of the contraction theorem and the domain of its uniqueness conclusion. Do the two successful local certificates establish a global root count by themselves?

# %% [markdown]
# ## Task C · A zero residual that cannot establish uniqueness (35 minutes)
#
# Use the near-singular example below and inspect its exact midpoint residual and contraction bound. Verify both known roots by exact substitution.

# %% tags=["exercise"]
epsilon = Fraction(1, 10**6)
def near_system(x, y):
    return [x+y, x+(1+epsilon)*y+x*x]

def near_jacobian(box):
    return jacobian2(near_system, box)

near_box = [Interval("-1/100", "1/100"), Interval("-1/100", "1/100")]
near_R = midpoint_inverse(near_jacobian(near_box))
near_image, near_remainder = student_image(near_system, near_jacobian, near_box, near_R)
status, q = classify(near_box, near_image, near_remainder, near_R)
print("Residual:", near_system(Interval(0), Interval(0)))
print("Status and q:", status, q)
assert status == "inconclusive"
assert near_system(Fraction(0), Fraction(0)) == [0, 0]
assert near_system(epsilon, -epsilon) == [0, 0]

# %% [markdown]
# **Written response:** Explain why extra arithmetic precision cannot make a true uniqueness claim on this box. As an extension, try a much smaller box around the origin and recompute all checks.

# %% [markdown]
# ## Submission
#
# Complete the code and written responses. Restart the kernel and run every cell. State the mathematical assumptions for each guarantee; retain failed or inconclusive examples and explain them.
