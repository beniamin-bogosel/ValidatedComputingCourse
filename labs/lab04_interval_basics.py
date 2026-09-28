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
# # Lab 04 · Build exact interval operations
#
# **Time:** about 2 hours. **Preparation:** [Lecture 04](../notebooks/04_interval_basics.ipynb).
#
# Build a small interval class using exact rational endpoints. The point is to justify the formulas before considering rounding. Do not import the reference interval class for Task A.

# %%
from fractions import Fraction

# Strings describe intended decimal values exactly.
assert Fraction("0.1") == Fraction(1, 10)


# %% [markdown]
# ## Task A · Four endpoint products (45 minutes)
#
# Complete multiplication, reciprocal, and square below. Accept only `StudentInterval` operands for multiplication. Reject reciprocals of intervals containing zero. The square should give the exact range of $x^2$ on the input interval, including intervals crossing zero.

# %% tags=["exercise"]
class StudentInterval:
    def __init__(self, lo, hi=None):
        if hi is None:
            hi = lo
        if isinstance(lo, float) or isinstance(hi, float):
            raise TypeError("Use integers, fractions, or decimal strings")
        self.lo = Fraction(lo)
        self.hi = Fraction(hi)
        if self.lo > self.hi:
            raise ValueError("Endpoints are reversed")

    def __repr__(self):
        return f"[{self.lo}, {self.hi}]"

    def __add__(self, other):
        return StudentInterval(self.lo + other.lo, self.hi + other.hi)

    def __sub__(self, other):
        return StudentInterval(self.lo - other.hi, self.hi - other.lo)

    def __mul__(self, other):
        raise NotImplementedError("Find the smallest and largest endpoint products")

    def reciprocal(self):
        raise NotImplementedError("Check the domain before taking reciprocals")

    def square(self):
        raise NotImplementedError("Separate the three sign cases")


# %% tags=["exercise"]
def check_endpoints(interval, lo, hi):
    assert interval.lo == Fraction(lo)
    assert interval.hi == Fraction(hi)

for lo, hi in [(-3, -1), (-2, 3), (0, 0), (1, 4)]:
    X = StudentInterval(lo, hi)
    for left, right in [(-4, -2), (-1, 2), (0, 0), (2, 5)]:
        Y = StudentInterval(left, right)
        product = X * Y
        for x in [X.lo, (X.lo + X.hi)/2, X.hi]:
            for y in [Y.lo, (Y.lo + Y.hi)/2, Y.hi]:
                assert product.lo <= x*y <= product.hi
check_endpoints(StudentInterval(-3, -1).reciprocal(), -1, Fraction(-1, 3))
check_endpoints(StudentInterval(2, 4).reciprocal(), Fraction(1, 4), Fraction(1, 2))
check_endpoints(StudentInterval(-2, 3).square(), 0, 9)
check_endpoints(StudentInterval(-3, -1).square(), 1, 9)
check_endpoints(StudentInterval(2, 4).square(), 4, 16)
try:
    StudentInterval(-1, 1).reciprocal()
except ZeroDivisionError:
    print("Expected rejection: denominator includes zero")
else:
    raise AssertionError("Division through zero must be rejected")

# %% [markdown]
# **Written answer:** Prove the multiplication formula using linearity with one argument fixed. Explain why the sample checks alone are insufficient.

# %% [markdown]
# ## Task B · Interpret a certificate (35 minutes)
#
# Use your class to bound the area of a rectangle with side lengths in [2.9, 3.1] and [4.8, 5.2], and evaluate $x+1/x$ on [2, 3].

# %% tags=["exercise"]
length = StudentInterval("2.9", "3.1")
width = StudentInterval("4.8", "5.2")
area = length * width
X = StudentInterval(2, 3)
value = X + X.reciprocal()
print("Area:", area)
print("x + 1/x:", value)

# %% tags=["exercise"]
check_endpoints(area, "13.92", "16.12")
check_endpoints(value, Fraction(7, 3), Fraction(7, 2))

# %% [markdown]
# **Written answer:** Is each enclosure the exact range? What does the repeated occurrence of x change? State the modeling assumption for the area.

# %% [markdown]
# ## Task C · Set language and dependency (30 minutes)
#
# For X = [-2, 3], compute X − X, X * X, and X.square(). On paper, find the hull and intersection of [0, 2] and [1, 3], and the intersection of [0, 1] and [2, 3].

# %% tags=["exercise"]
X = StudentInterval(-2, 3)
print("X - X:", X - X)
print("X * X:", X * X)
print("square(X):", X.square())

# %% [markdown]
# **Written answer:** Explain the difference between two independent choices from X and two occurrences of the same real number. Why is an empty intersection different from [0, 0]?

# %% [markdown]
# ## Submission
#
# Complete every exercise, replace the written-answer prompts with your explanations, then restart the kernel and run all cells. Include the assumptions behind each certificate and describe any inconclusive result.
