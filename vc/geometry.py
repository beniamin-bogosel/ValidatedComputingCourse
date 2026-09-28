"""Readable orientation filter for exact rational or uncertain interval points."""
from dataclasses import dataclass
from fractions import Fraction
from flint import ctx
from vc.intervals import RationalInterval as Interval, exact_fraction
from vc.arb_bridge import to_ball, from_ball


def determinant(a, b, c):
    ab_x = b[0] - a[0]
    ab_y = b[1] - a[1]
    ac_x = c[0] - a[0]
    ac_y = c[1] - a[1]
    return ab_x * ac_y - ab_y * ac_x


def exact_point(point):
    if len(point) != 2:
        raise ValueError("A point must have two coordinates")
    return tuple(exact_fraction(value) for value in point)


def sign_of_interval(value):
    if value.lo > 0:
        return 1
    if value.hi < 0:
        return -1
    if value.lo == value.hi == 0:
        return 0
    return None


def orientation_bound(a, b, c, precision=80):
    """Input coordinates are RationalIntervals; preserve their whole sets."""
    if not isinstance(precision, int) or precision < 2:
        raise ValueError("precision must be an integer of at least two bits")
    with ctx.workprec(precision):
        ball_points = []
        for point in [a, b, c]:
            if len(point) != 2:
                raise ValueError("A point must have two coordinates")
            ball_points.append(tuple(to_ball(value) for value in point))
        return from_ball(determinant(*ball_points))


@dataclass
class OrientationResult:
    sign: int
    method: str
    attempts: list[tuple[int, Interval]]
    exact_determinant: Fraction | None = None


def orientation(a, b, c, precisions=(24, 53, 100, 200)):
    """Exact rational inputs: filter first, exact fallback if needed.

    Float inputs must be explicitly converted with Fraction.from_float.
    This function is not a fallback for uncertain measured coordinates.
    """
    points = [exact_point(point) for point in [a, b, c]]
    boxes = [tuple(Interval(value) for value in point) for point in points]
    attempts = []
    for precision in precisions:
        bound = orientation_bound(*boxes, precision=precision)
        attempts.append((precision, bound))
        sign = sign_of_interval(bound)
        if sign is not None:
            return OrientationResult(sign, "arb", attempts)
    value = determinant(*points)
    sign = (value > 0) - (value < 0)
    return OrientationResult(sign, "fraction", attempts, value)
