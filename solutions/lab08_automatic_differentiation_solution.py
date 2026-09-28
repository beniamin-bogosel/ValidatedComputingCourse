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
# # Instructor solution · Lab 08 · Propagate derivatives explicitly
#
# **Preparation:** [Lecture 08](../notebooks/08_automatic_differentiation.ipynb).
#
# **Time:** about 2 hours. Implement a small scalar dual class and use two forward passes to enclose a Jacobian. The constructor and simple arithmetic are supplied.

# %%
from fractions import Fraction
from flint import arb, ctx
from vc.intervals import RationalInterval as Interval
from vc.arb_bridge import to_ball, from_ball
from vc.autodiff import Dual


# %% [markdown]
# ## Task A · Product and reciprocal rules (45 minutes)
#
# Complete the two missing methods. Use exact fractions for the first checks and intervals for the second. This student type needs only the displayed arithmetic operations; elementary functions are explored with the reviewed type in Task C.

# %%
class StudentDual:
    def __init__(self, value, derivative):
        self.value = value
        self.derivative = derivative

    def _operand(self, other):
        if isinstance(other, StudentDual):
            return other
        return StudentDual(other, self.derivative * 0)

    def __add__(self, other):
        other = self._operand(other)
        return StudentDual(self.value + other.value, self.derivative + other.derivative)

    def __radd__(self, other):
        return self + other

    def __neg__(self):
        return StudentDual(-self.value, -self.derivative)

    def __sub__(self, other):
        return self + (-self._operand(other))

    def __rsub__(self, other):
        return self._operand(other) - self

    def __mul__(self, other):
        other = self._operand(other)
        value = self.value * other.value
        first_term = self.derivative * other.value
        second_term = self.value * other.derivative
        return StudentDual(value, first_term + second_term)

    def __rmul__(self, other):
        return self * other

    def reciprocal(self):
        inverse = 1 / self.value
        derivative = -self.derivative * inverse * inverse
        return StudentDual(inverse, derivative)

    def __truediv__(self, other):
        return self * self._operand(other).reciprocal()


# %%
def polynomial(x):
    return (x+2)*(x-1)*(x-3)

for value in [Fraction(-2), Fraction(1, 3), Fraction(4)]:
    x = StudentDual(value, Fraction(1))
    result = polynomial(x)
    assert result.value == value**3 - 2*value**2 - 5*value + 6
    assert result.derivative == 3*value**2 - 4*value - 5
    quotient = (x+3)/(x+4)
    assert quotient.derivative == 1/(value+4)**2

X = Interval(1, 2)
result = polynomial(StudentDual(X, Interval(1)))
for value in [X.lo, X.midpoint(), X.hi]:
    assert result.derivative.contains(3*value*value - 4*value - 5)
print("Derivative enclosure:", result.derivative)


# %% [markdown]
# **Worked explanation:** The seed represents the independent variable and its derivative; constant tangents are zero. Each arithmetic rule is the corresponding differentiation rule, so induction along the expression propagates its derivative. Interval components must enclose every operation throughout the domain, including the denominator domain check. AD itself does not remove arithmetic rounding or interval dependency.

# %% [markdown]
# ## Task B · Two Jacobian columns (40 minutes)
#
# Complete the seeds and output assembly for the supplied system. Use your `StudentDual` class. Rows index output equations and columns index input variables.

# %%
def system(x, y):
    return [x*x + x*y, x-y]

def student_jacobian(box):
    x, y = box
    first = system(StudentDual(x, Interval(1)), StudentDual(y, Interval(0)))
    second = system(StudentDual(x, Interval(0)), StudentDual(y, Interval(1)))
    matrix = []
    for row in range(2):
        matrix.append([first[row].derivative, second[row].derivative])
    return matrix


# %%
box = [Interval(1, 2), Interval(3, 4)]
matrix = student_jacobian(box)
for row in matrix:
    print(row)
# Analytic Jacobian: [[2*x+y, x], [1, -1]].
expected_ranges = [[Interval(5, 8), Interval(1, 2)], [Interval(1), Interval(-1)]]
for row in range(2):
    for column in range(2):
        assert expected_ranges[row][column].is_subset_of(matrix[row][column])

# %% [markdown]
# **Worked explanation:** Each pass selects one input direction and differentiates every output in that direction, producing a column. Seeding both with one gives the directional derivative along (1,1), the sum of the two columns, which cannot in general recover them separately.

# %% [markdown]
# ## Task C · Arb and finite differences (30 minutes)
#
# Run the supplied Arb experiment, then compare point AD with forward differences. The exact reference derivative of x³−2x at 1 is 1.

# %%
with ctx.workprec(100):
    x = Dual(to_ball(Interval("-1/4", "1/4")), arb(1))
    result = x.exp() * x.sin()
    derivative_bound = from_ball(result.derivative)
assert derivative_bound.contains(1)
print("Interval derivative:", derivative_bound)

def cubic_expression(x):
    return x*x*x - 2*x

ad_result = cubic_expression(StudentDual(Fraction(1), Fraction(1)))
print("Exact rational AD derivative:", ad_result.derivative)
for exponent in [2, 5, 8, 11, 14, 16]:
    h = 10.0**(-exponent)
    estimate = (cubic_expression(1.0+h) - cubic_expression(1.0))/h
    print(exponent, estimate, abs(estimate-1))

# %% [markdown]
# **Worked explanation:** Forward differences have truncation and arithmetic error. Exact rational AD has neither for this polynomial at the exact input; float AD would still have arithmetic error. Interval AD encloses value and derivative but may overestimate through dependency. A midpoint branch says nothing about which branches apply elsewhere in an interval; nondifferentiability can also occur at the branch boundary.
