"""Compatibility checks for the arithmetic semantics used by the notebooks."""

from fractions import Fraction
import gmpy2
from flint import arb, ctx, fmpq
import pytest


def rational(x):
    n, d = x.as_integer_ratio()
    return Fraction(int(n), int(d))


def contains_exact_rational(ball, value):
    # contains(fmpq) may coerce the rational to an enclosing ball first.
    midpoint, radius = ball.mid().fmpq(), ball.rad().fmpq()
    return midpoint - radius <= value <= midpoint + radius


@pytest.mark.parametrize("value", [Fraction(1, 10), Fraction(-1, 10), Fraction(1, 3)])
def test_directed_mpfr_conversion_encloses_exact_input(value):
    original = gmpy2.get_context().precision, gmpy2.get_context().round
    q = gmpy2.mpq(value.numerator, value.denominator)
    with gmpy2.context(precision=53, round=gmpy2.RoundDown):
        lo = rational(gmpy2.mpfr(q))
    with gmpy2.context(precision=53, round=gmpy2.RoundUp):
        hi = rational(gmpy2.mpfr(q))
    assert lo <= value <= hi
    assert (gmpy2.get_context().precision, gmpy2.get_context().round) == original


def test_arb_distinguishes_float_input_from_intended_decimal():
    original = ctx.prec
    with ctx.workprec(200):
        assert contains_exact_rational(arb("0.1"), fmpq(1, 10))
        assert not contains_exact_rational(arb(0.1), fmpq(1, 10))
        assert contains_exact_rational(arb(1)/arb(3), fmpq(1, 3))
    assert ctx.prec == original


def test_contexts_restore_after_exceptions():
    mpfr_precision, arb_precision = gmpy2.get_context().precision, ctx.prec
    with pytest.raises(RuntimeError):
        with gmpy2.context(precision=137), ctx.workprec(139):
            raise RuntimeError("simulated failed experiment")
    assert gmpy2.get_context().precision == mpfr_precision
    assert ctx.prec == arb_precision
