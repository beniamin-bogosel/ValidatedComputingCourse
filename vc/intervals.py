"""Bounded rational intervals for Lectures 04, 06, and 07.

The arithmetic is exact. Float inputs must be converted explicitly with
Fraction.from_float when the stored binary value is the intended input.
Endpoints are public for inspection; do not change them after construction.
"""

from fractions import Fraction


def exact_fraction(value):
    """Accept an integer, Fraction, or exact rational/decimal string."""
    if not isinstance(value, (int, Fraction, str)):
        raise TypeError("Use an integer, Fraction, or string; convert floats explicitly")
    return Fraction(value)


class RationalInterval:
    """A nonempty closed interval with exact rational endpoints."""

    def __init__(self, lo, hi=None):
        if hi is None:
            hi = lo
        self.lo = exact_fraction(lo)
        self.hi = exact_fraction(hi)
        if self.lo > self.hi:
            raise ValueError("The lower endpoint must not exceed the upper endpoint")

    def __repr__(self):
        return f"[{self.lo}, {self.hi}]"

    def width(self):
        return self.hi - self.lo

    def midpoint(self):
        return (self.lo + self.hi) / 2

    def contains(self, value):
        value = exact_fraction(value)
        return self.lo <= value <= self.hi

    def is_subset_of(self, other):
        return other.lo <= self.lo and self.hi <= other.hi

    def hull(self, other):
        lower = min(self.lo, other.lo)
        upper = max(self.hi, other.hi)
        return RationalInterval(lower, upper)

    def intersection(self, other):
        lower = max(self.lo, other.lo)
        upper = min(self.hi, other.hi)
        if lower > upper:
            return None  # Empty intersection; never a fabricated nonempty interval.
        return RationalInterval(lower, upper)

    def bisect(self):
        if self.lo == self.hi:
            raise ValueError("A point interval cannot be split into smaller intervals")
        middle = self.midpoint()
        left = RationalInterval(self.lo, middle)
        right = RationalInterval(middle, self.hi)
        return left, right

    def __add__(self, other):
        other = as_interval(other)
        lower = self.lo + other.lo
        upper = self.hi + other.hi
        return RationalInterval(lower, upper)

    def __radd__(self, other):
        return self + other

    def __neg__(self):
        return RationalInterval(-self.hi, -self.lo)

    def __sub__(self, other):
        other = as_interval(other)
        lower = self.lo - other.hi
        upper = self.hi - other.lo
        return RationalInterval(lower, upper)

    def __rsub__(self, other):
        return as_interval(other) - self

    def __mul__(self, other):
        other = as_interval(other)
        products = [self.lo * other.lo, self.lo * other.hi,
                    self.hi * other.lo, self.hi * other.hi]
        return RationalInterval(min(products), max(products))

    def __rmul__(self, other):
        return self * other

    def reciprocal(self):
        if self.contains(0):
            raise ZeroDivisionError("Reciprocal requires an interval excluding zero")
        lower = 1 / self.hi
        upper = 1 / self.lo
        return RationalInterval(lower, upper)

    def __truediv__(self, other):
        other = as_interval(other)
        return self * other.reciprocal()

    def __rtruediv__(self, other):
        return as_interval(other) / self

    def square(self):
        """Range of x² for ONE variable, distinct from two-operand X * X."""
        endpoint_squares = [self.lo * self.lo, self.hi * self.hi]
        if self.contains(0):
            lower = Fraction(0)
        else:
            lower = min(endpoint_squares)
        upper = max(endpoint_squares)
        return RationalInterval(lower, upper)


def as_interval(value):
    if isinstance(value, RationalInterval):
        return value
    return RationalInterval(value)

