# ---
# jupyter:
#   course:
#     kind: lecture
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
# # 04 · Interval arithmetic as arithmetic with sets
#
# **Time:** 100–120 minutes. **Prerequisites:** Lectures 01–03, inequalities.
# **Lab:** [Build a rational interval class](../labs/lab04_interval_basics.ipynb).
#
# Objectives: derive endpoint formulas, distinguish hull from union, implement
# basic operations, and explain what information an interval calculation retains.
# We use exact rational endpoints today so that rounding does not obscure the
# set argument. Machine endpoints come in Lecture 05.

# %%
from fractions import Fraction
from vc.intervals import RationalInterval as Interval

# %% [markdown]
# ## Motivation · Measurements describe sets
#
# A rectangle's sides are known to lie in [2.9, 3.1] and [4.8, 5.2]. The numbers
# are positive, so the smallest possible area uses both lower endpoints and the
# largest uses both upper endpoints. Strings preserve the exact decimal bounds.

# %%
length = Interval("2.9", "3.1")
width = Interval("4.8", "5.2")
area = length * width
print("Area enclosure:", area)
assert area.lo == Fraction("13.92")
assert area.hi == Fraction("16.12")

# %% [markdown]
# ## THEORY · Definitions and set operations
#
# A closed bounded interval is $X=[a,b]=\{x:a\leq x\leq b\}$ with $a\leq b$.
# It is a point interval when $a=b$. Its width is $b-a$, midpoint $(a+b)/2$,
# and radius $(b-a)/2$. These are exact real formulas, not rounding instructions.
#
# Containment is an endpoint comparison: $[a,b]\subseteq[c,d]$ exactly when
# $c\leq a$ and $b\leq d$. The **hull** of two intervals is the smallest interval
# containing both. It can include a gap absent from their union.
#
# $$\operatorname{hull}(X,Y)=[\min(a,c),\max(b,d)].$$
#
# Their intersection has endpoints $\max(a,c)$ and $\min(b,d)$ if these are
# ordered; otherwise it is empty. Our small class returns `None` for an empty
# intersection. It never constructs a reversed interval to represent emptiness.

# %%
X = Interval(0, 1)
Y = Interval(2, 3)
print("Hull:", X.hull(Y))
print("Intersection:", X.intersection(Y))
print("Touching intervals:", X.intersection(Interval(1, 2)))
print("Width and midpoint:", X.width(), X.midpoint())

# %% [markdown]
# **EXERCISE (5 minutes):** draw X, Y, their union, and their hull. Is 3/2 in
# the hull? Is it in the union? Does a one-point intersection count as empty?

# %% [markdown]
# ## THEORY · Arithmetic with two independent operands
#
# For a supported real operation $\circ$, define
# $X\circ Y=\{x\circ y:x\in X,\ y\in Y\}$. The two choices are independent.
# With $X=[a,b]$ and $Y=[c,d]$:
#
# $$X+Y=[a+c,b+d],\qquad X-Y=[a-d,b-c].$$
#
# **Proof for subtraction.** Since $x\geq a$ and $y\leq d$, we have $x-y\geq a-d$.
# Similarly $x-y\leq b-c$. Both bounds are attained at corner choices. Continuity
# on the rectangle between the corners fills the intermediate values.
#
# A short implementation exposes exactly those bounds:

# %%
def subtract_bounds(lower_x, upper_x, lower_y, upper_y):
    lower_result = lower_x - upper_y
    upper_result = upper_x - lower_y
    return lower_result, upper_result

print(subtract_bounds(Fraction(1), Fraction(4), Fraction(2), Fraction(5)))
print("Class operation:", Interval(1, 4) - Interval(2, 5))

# %% [markdown]
# ## THEORY · Multiplication needs four corners
#
# $$XY=[\min(ac,ad,bc,bd),\max(ac,ad,bc,bd)].$$
#
# **Proof sketch.** For a fixed y, the expression xy is linear in x, so its
# extrema occur at endpoints. Apply the same argument to y for each endpoint x.
# Thus extrema occur among the four products. The continuous image of the
# rectangle is an interval, so these extrema give the whole product range.
#
# Four products are easy to read and audit. Sign-based shortcuts can wait.

# %%
def multiplication_bounds(X, Y):
    products = [X.lo * Y.lo, X.lo * Y.hi, X.hi * Y.lo, X.hi * Y.hi]
    lower_result = min(products)
    upper_result = max(products)
    return lower_result, upper_result

X = Interval(-2, 3)
Y = Interval(-4, -1)
print("Four-corner bounds:", multiplication_bounds(X, Y))
print("Class operation:", X * Y)

# %% [markdown]
# ## THEORY · Reciprocal and division
#
# If $0\notin[c,d]$, the reciprocal function is decreasing on that interval:
#
# $$1/[c,d]=[1/d,1/c],\qquad X/Y=X(1/Y).$$
#
# This works on a wholly negative interval as well as a positive one. If the
# denominator contains zero, our bounded-interval arithmetic rejects division.
# Even when nonzero real values remain in the denominator set, their reciprocals
# need not form a bounded interval. Extended interval arithmetic is a later topic.

# %%
print("Negative reciprocal:", Interval(-4, -2).reciprocal())
print("Division:", Interval(1, 2) / Interval(-4, -2))
try:
    Interval(1) / Interval(-1, 1)
except ZeroDivisionError as error:
    print("Explicitly unsupported:", error)

# %% [markdown]
# ## EXPERIMENT · Repeated variables are different information
#
# For X = [−2,3], the expression X*X allows different values in its two factors.
# Squaring a single real x uses the same value twice. A dedicated square operation
# can preserve that relation and return the sharper range.

# %%
X = Interval(-2, 3)
print("Two independent factors:", X * X)
print("One variable squared:", X.square())
print("Independent subtraction:", X - X)
assert (X * X).lo == -6
assert X.square().lo == 0

# %% [markdown]
# The interval X−X is wide but correct: it contains every value of x−x, including
# zero. It also includes combinations from different choices of the operands.
# Arithmetic does not automatically remember that two occurrences name the same
# unknown. This **dependency problem** will become central in Lecture 06.
#
# **EXERCISE (10 minutes):** derive square bounds in three cases: X nonnegative,
# X nonpositive, and X containing zero. Explain why `X*X` is still an enclosure.

# %% [markdown]
# ## THEORY · Inclusion survives composition
#
# **Proposition.** If each elementary operation encloses all results from its input
# sets, then an expression composed of these operations encloses the corresponding
# real result for every admissible choice of inputs.
#
# **Proof.** Start with an input belonging to its declared interval. Each operation
# takes enclosed intermediate values to another enclosed value. Repeat this argument
# along the finite expression, provided each operation is defined on its input set.
#
# This proves inclusion, not sharpness. It also explains why the domain check on
# division cannot be ignored.

# %%
X = Interval(2, 3)
enclosure = X + 1 / X
print("For every x in [2,3], x + 1/x belongs to", enclosure)
assert enclosure.lo == Fraction(7, 3)
assert enclosure.hi == Fraction(7, 2)
print("In particular, the expression is strictly positive on the entire interval.")

# %% [markdown]
# ## Implementation scope and lab
#
# The reviewed class in [vc/intervals.py](../vc/intervals.py) has short, explicit
# methods. Scalars become point intervals; `square()` is deliberately named.
# Float inputs are rejected: use a string for an intended decimal, or
# `Fraction.from_float` when the stored binary value is intended. Keep endpoints
# unchanged after construction.
#
# In the lab you build a small class yourself, using exact rational operations.
# Later notebooks import the reviewed class so an unfinished earlier lab does not
# prevent progress. The lab's diagnostics can reveal mistakes; the derivations above
# explain why correctly implemented formulas enclose every admissible input.
#
# **Exit ticket:** explain independent choices, a disconnected union, and why
# division by an interval containing zero is outside today's scope.
#
# **Reading:** Tucker §§2.1–2.2, printed pp. 24–30. Next:
# [Lecture 05](05_directed_rounding.ipynb).

