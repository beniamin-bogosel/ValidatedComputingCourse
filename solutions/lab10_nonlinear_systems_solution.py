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
# # Instructor solution · Lab 10 · Implement a local Krawczyk certificate
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

# %%
def student_image(function, jacobian, box, R):
    center = [Interval(part.midpoint()) for part in box]
    residual = function(*center)
    J = jacobian(box)
    product = matrix_product(R, J)
    remainder = []
    for row in range(2):
        entries = []
        for column in range(2):
            identity_entry = 1 if row == column else 0
            entries.append(identity_entry - product[row][column])
        remainder.append(entries)
    correction = matrix_vector(R, residual)
    displacement = [box[index] - center[index] for index in range(2)]
    spread = matrix_vector(remainder, displacement)
    image = []
    for index in range(2):
        image.append(center[index] - correction[index] + spread[index])
    return image, remainder


# %%
box = [Interval("0.7", "0.72"), Interval("0.7", "0.72")]
R = midpoint_inverse(jacobian(box))
image, remainder = student_image(system, jacobian, box, R)
print("K:", image)
print("E:", remainder)
for part in image:
    assert 2*part.lo**2 < 1 < 2*part.hi**2
assert row_sum_bound(remainder) == Fraction(1, 71)


# %% [markdown]
# **Worked explanation:** A root is a fixed point of T(x)=x−Rf(x), so the interval enclosure of T(X) must contain it. The theorem requires a fixed nonsingular R and verified inclusion/contraction inequalities, not equality with the Jacobian inverse. A good inverse proposal helps those inequalities pass; its quality is checked by the rigorous remainder.

# %% [markdown]
# ## Task B · Classify the result (35 minutes)
#
# Reject a singular R using `inverse2(R)`. Return `(status, q)` with status `excluded` if one coordinate image misses its input interval; `unique_root` if every image coordinate is strictly inside and q<1; otherwise `inconclusive`. Use `row_sum_bound` for q. Assume a box with positive side widths.

# %%
def classify(box, image, remainder, R):
    inverse2(R)
    q = row_sum_bound(remainder)
    disjoint = any(image[index].intersection(box[index]) is None for index in range(2))
    inside = all(box[index].lo < image[index].lo and image[index].hi < box[index].hi
                 for index in range(2))
    if disjoint:
        return "excluded", q
    if inside and q < 1:
        return "unique_root", q
    return "inconclusive", q


# %%
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
# **Worked explanation:** The function is C¹ on a neighborhood of the closed box, the Jacobian enclosure is valid throughout it, R is fixed and nonsingular, K is strictly inside the box, and q<1. The enclosed map is a contraction mapping that box into itself, so it has exactly one fixed point there, hence one root. Two local certificates alone leave the rest of the plane unexamined; algebra settles the global count for this particular circle-line example.

# %% [markdown]
# ## Task C · A zero residual that cannot establish uniqueness (35 minutes)
#
# Use the near-singular example below and inspect its exact midpoint residual and contraction bound. Verify both known roots by exact substitution.

# %%
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
# **Worked explanation:** The box actually contains two roots, so no correct theorem can certify uniqueness there. Exact rational arithmetic already removes rounding error from this polynomial example. Reducing the box can isolate the origin from the other root and reduce Jacobian variation; it changes the claim being certified, rather than changing the mathematical facts in the original box.
