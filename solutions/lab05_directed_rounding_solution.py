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
# # Lab 05 · Instructor solution
#
# Implement two directed operations, then audit conversion to Arb. Exact fractions are used to inspect endpoint bounds; float conversions are only for display.

# %%
from fractions import Fraction
import gmpy2
from flint import ctx
from vc.mpfr_intervals import MPFRInterval
from vc.intervals import RationalInterval as Interval
from vc.arb_bridge import to_ball, from_ball

left = MPFRInterval("0.1", precision=24)
right = MPFRInterval("0.3", precision=24)
print(left)
print(right)


# %% [markdown]
# ## Task A · Directed addition (30 minutes)
#
# Complete addition for two MPFR intervals at the same precision. Use separate `gmpy2.context` blocks with `RoundDown` and `RoundUp`; return an `MPFRInterval`. Its constructor accepts MPFR endpoints without a float conversion. Reject mismatched precisions.

# %%
def add_outward(left, right):
    if left.precision != right.precision:
        raise ValueError("Use the same precision for both operands")
    precision = left.precision
    with gmpy2.context(precision=precision, round=gmpy2.RoundDown):
        lower = left.lo + right.lo
    with gmpy2.context(precision=precision, round=gmpy2.RoundUp):
        upper = left.hi + right.hi
    return MPFRInterval(lower, upper, precision=precision)


# %%
result = add_outward(left, right)
assert result.contains(Fraction(2, 5))
exact_sum = left.exact_bounds() + right.exact_bounds()
assert exact_sum.is_subset_of(result.exact_bounds())
print("Enclosure:", result.exact_bounds())
try:
    add_outward(left, MPFRInterval(1, precision=80))
except ValueError:
    print("Expected precision mismatch")
else:
    raise AssertionError("Mismatched precision was accepted")


# %% [markdown]
# **Worked explanation:** For all admissible a and b, down(left.lo + right.lo) ≤ left.lo + right.lo ≤ a+b ≤ left.hi + right.hi ≤ up(left.hi + right.hi). Nearest rounding may move the lower endpoint up or the upper endpoint down, losing an extreme value.

# %% [markdown]
# ## Task B · Products with mixed signs (45 minutes)
#
# Implement multiplication by computing all four endpoint products in each directed context. Keep the two product lists visible. Use exact interval arithmetic on the stored bounds as a diagnostic oracle.

# %%
def multiply_outward(left, right):
    if left.precision != right.precision:
        raise ValueError("Use the same precision for both operands")
    precision = left.precision
    with gmpy2.context(precision=precision, round=gmpy2.RoundDown):
        lower_products = [left.lo * right.lo, left.lo * right.hi,
                          left.hi * right.lo, left.hi * right.hi]
    with gmpy2.context(precision=precision, round=gmpy2.RoundUp):
        upper_products = [left.lo * right.lo, left.lo * right.hi,
                          left.hi * right.lo, left.hi * right.hi]
    lower = min(lower_products)
    upper = max(upper_products)
    return MPFRInterval(lower, upper, precision=precision)


# %%
original_precision = gmpy2.get_context().precision
original_rounding = gmpy2.get_context().round
for precision in [8, 24, 80]:
    for lo, hi in [("-2.3", "-0.1"), ("-1.2", "3.4"), ("0.1", "0.7")]:
        X = MPFRInterval(lo, hi, precision=precision)
        Y = MPFRInterval("-0.3", "1.1", precision=precision)
        exact_product = X.exact_bounds() * Y.exact_bounds()
        computed = multiply_outward(X, Y).exact_bounds()
        assert exact_product.is_subset_of(computed)
        print(precision, "extra width ≈", float(computed.width() - exact_product.width()))
assert gmpy2.get_context().precision == original_precision
assert gmpy2.get_context().round == original_rounding

# %% [markdown]
# **Worked explanation:** The multiplication extrema depend on endpoint signs; selecting only lower×lower and upper×upper fails for mixed or negative signs. Computing all corners handles every bounded sign case. Local contexts prevent one calculation from silently changing later calculations or library calls.

# %% [markdown]
# ## Task C · Conversion audit (35 minutes)
#
# Run the exact endpoint audit below at several precisions. Then compare the semantics of a decimal string and a stored float. The helper deliberately converts Arb midpoint and radius back to exact fractions.

# %%
domain = Interval("0.1", "0.3")
for precision in [24, 80, 160]:
    with ctx.workprec(precision):
        ball = to_ball(domain)
        recovered = from_ball(ball)
    assert domain.is_subset_of(recovered)
    print(precision, "extra width ≈", float(recovered.width() - domain.width()))

intended = MPFRInterval("0.1", precision=100)
stored = MPFRInterval(Fraction.from_float(0.1), precision=100)
print("Intended decimal:", intended.exact_bounds())
print("Stored binary float:", stored.exact_bounds())
assert intended.contains(Fraction(1, 10))
assert not stored.contains(Fraction(1, 10))

# %% [markdown]
# **Worked explanation:** Nearest binary64 conversion can move a certified endpoint inward. Exact midpoint/radius conversion preserves the actual Arb ball. More precision reduces representation error, but the original width 1/5 remains. Ball conversion can widen the domain; the function must be defined throughout that ball, and a nonfinite result cannot be used as a finite certificate.
