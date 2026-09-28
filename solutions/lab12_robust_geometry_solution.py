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
# # Instructor model · Lab 12 · Filter an orientation predicate
#
# **Time:** 90 minutes, followed by capstone work. **Preparation:** [Lecture 12](../notebooks/12_robust_geometry.ipynb). Implement the precision filter and exact fallback, and keep uncertain measured inputs separate.

# %%
from fractions import Fraction
from vc.intervals import RationalInterval as Interval
from vc.geometry import determinant, exact_point, orientation_bound, sign_of_interval, OrientationResult


# %% [markdown]
# ## Task A · Filter and fall back (45 minutes)
#
# Implement `student_orientation` for exact rational coordinates. Convert with `exact_point`, form singleton intervals, try the configured precisions, and return an `OrientationResult`. If all attempted bounds are inconclusive, evaluate the determinant using exact fractions. Use `sign_of_interval`: zero is conclusive only for the singleton [0,0].

# %%
def student_orientation(a, b, c, precisions = (24, 53, 100, 200)):
    points = [exact_point(point) for point in [a, b, c]]
    boxes = [tuple(Interval(value) for value in point) for point in points]
    attempts = []
    for precision in precisions:
        bound = orientation_bound(*boxes, precision = precision)
        attempts.append((precision, bound))
        sign = sign_of_interval(bound)
        if sign is not None:
            return OrientationResult(sign, "arb", attempts)
    value = determinant(*points)
    if value > 0:
        sign = 1
    elif value < 0:
        sign = -1
    else:
        sign = 0
    return OrientationResult(sign, "fraction", attempts, value)


# %%
n = 2 ** 27
points = ((0, 0), (n, n - 1), (n + 1, n))
assert determinant(*[tuple(float(x) for x in point) for point in points]) == 0
result = student_orientation(*points)
assert result.sign == 1
fallback = student_orientation(*points, precisions = (24,))
assert fallback.method == "fraction" and fallback.exact_determinant == 1
assert student_orientation(points[0], points[2], points[1]).sign == -1
assert student_orientation((0, 0), ("1/3", "2/3"), ("2/3", "4/3")).sign == 0
for precision, bound in result.attempts:
    print(precision, bound)
print("Final sign:", result.sign)

# %% [markdown]
# **Worked explanation:** Inclusion places the determinant inside the computed bound, so a strictly signed bound certifies that sign and [0,0] certifies zero. Exact rational arithmetic computes the determinant without rounding and settles the zero case. The filter establishes this predicate only; the surrounding algorithm still needs correct topology, coverage, and treatment of degeneracies.

# %% [markdown]
# ## Task B · State the intended inputs (20 minutes)
#
# Compare exact decimal input with the exact value of a stored float. The examples below intentionally specify two different mathematical triples.

# %%
decimal = student_orientation((0, 0), (1, "0.1"), (10, 1))
stored_tenth = Fraction.from_float(0.1)
stored = student_orientation((0, 0), (1, stored_tenth), (10, 1))
print("Intended decimal:", decimal.sign)
print("Stored binary tenth:", stored.sign)
assert decimal.sign == 0
assert stored.sign == -1

# %% [markdown]
# **Worked explanation:** The exact decimal 1/10 makes the three points collinear. The stored binary64 approximation exceeds 1/10, so 1−10·stored_tenth is strictly negative. The claim and input-encoding section must identify which coordinates define the problem; exact arithmetic cannot repair a wrongly specified problem.

# %% [markdown]
# ## Task C · Keep physical uncertainty (25 minutes)
#
# Enclose orientation for measured coordinates below at 24, 100, and 200 bits. Give two allowed exact realizations with opposite signs.

# %%
a = (Interval(0), Interval(0))
b = (Interval(1), Interval(1))
c = (Interval(2), Interval("1.999", "2.001"))
for precision in [24, 100, 200]:
    bound = orientation_bound(a, b, c, precision)
    print(precision, bound, sign_of_interval(bound))
    assert sign_of_interval(bound) is None
negative = student_orientation((0, 0), (1, 1), (2, "1.999"))
positive = student_orientation((0, 0), (1, 1), (2, "2.001"))
assert negative.sign == -1 and positive.sign == 1

# %% [markdown]
# **Worked explanation:** The allowed family actually has both orientations. Midpoint fallback would settle only a different exact triple. The correct conclusion is that a uniform sign is not available for these measured inputs; increasing arithmetic precision cannot eliminate the specified uncertainty.
