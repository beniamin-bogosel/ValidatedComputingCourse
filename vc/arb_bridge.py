"""Explicit bridge between rational domain intervals and Arb evaluations."""

from fractions import Fraction
from flint import arb, ctx, fmpq

from vc.intervals import RationalInterval


def flint_rational(value):
    return fmpq(value.numerator, value.denominator)


def python_fraction(value):
    return Fraction(int(value.p), int(value.q))


def to_ball(interval):
    """Enclose the full interval, including rounding of both endpoint conversions.

    Uses the caller's Arb precision. The result may be wider than the interval.
    """
    lower_ball = arb(flint_rational(interval.lo))
    upper_ball = arb(flint_rational(interval.hi))
    return lower_ball.union(upper_ball)


def from_ball(ball):
    """Return exact rational bounds for a finite ball, without a float conversion."""
    if not ball.is_finite():
        raise ValueError("Nonfinite Arb result: check the function domain or precision")
    midpoint = python_fraction(ball.mid().fmpq())
    radius = python_fraction(ball.rad().fmpq())
    return RationalInterval(midpoint - radius, midpoint + radius)


def evaluate_ball(function, domain, precision=80):
    """Evaluate an Arb-valued function on an enclosure of the entire domain.

    The function must use rigorous Arb operations and be defined on the expanded
    input ball. A finite result is an enclosure, not necessarily a sharp range.
    """
    if not isinstance(precision, int) or precision < 2:
        raise ValueError("precision must be an integer of at least 2 bits")
    with ctx.workprec(precision):
        input_ball = to_ball(domain)
        result = function(input_ball)
        if not isinstance(result, arb):
            raise TypeError("The function must return an Arb ball")
        return from_ball(result)

