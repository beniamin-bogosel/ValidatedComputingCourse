"""Small directed-rounding endpoint implementation for Lecture 05.

Only bounded intervals and basic arithmetic are supported. There are no
elementary functions, unbounded intervals, or IEEE interval decorations here.
Do not mutate endpoints or precision after construction.
"""

from fractions import Fraction
import gmpy2

from vc.intervals import RationalInterval, exact_fraction


def mpfr_fraction(value):
    """Recover the exact rational represented by a finite MPFR value."""
    if not gmpy2.is_finite(value):
        raise ValueError("This teaching kernel requires finite endpoints")
    numerator, denominator = value.as_integer_ratio()
    return Fraction(int(numerator), int(denominator))


def input_fraction(value):
    if isinstance(value, gmpy2.mpfr):
        return mpfr_fraction(value)
    return exact_fraction(value)


def round_fraction(value, precision, rounding):
    exact_value = gmpy2.mpq(value.numerator, value.denominator)
    with gmpy2.context(precision=precision, round=rounding):
        result = gmpy2.mpfr(exact_value)
    if not gmpy2.is_finite(result):
        raise ValueError("Endpoint overflow is outside this teaching kernel's scope")
    return result


class MPFRInterval:
    def __init__(self, lo, hi=None, precision=80):
        if not isinstance(precision, int) or precision < 2:
            raise ValueError("precision must be an integer of at least 2 bits")
        if hi is None:
            hi = lo
        lower_input = input_fraction(lo)
        upper_input = input_fraction(hi)
        if lower_input > upper_input:
            raise ValueError("The lower endpoint must not exceed the upper endpoint")
        self.precision = precision
        self.lo = round_fraction(lower_input, precision, gmpy2.RoundDown)
        self.hi = round_fraction(upper_input, precision, gmpy2.RoundUp)

    def __repr__(self):
        # Rounded decimal display is not the serialization of the endpoints.
        return f"MPFRInterval({self.lo!r}, {self.hi!r}, precision={self.precision})"

    def exact_bounds(self):
        return RationalInterval(mpfr_fraction(self.lo), mpfr_fraction(self.hi))

    def contains(self, value):
        return self.exact_bounds().contains(input_fraction(value))

    def width(self):
        return self.exact_bounds().width()

    def _operand(self, other):
        if isinstance(other, MPFRInterval):
            if other.precision != self.precision:
                raise ValueError("Use the same explicit precision for both operands")
            return other
        return MPFRInterval(other, precision=self.precision)

    def __add__(self, other):
        other = self._operand(other)
        with gmpy2.context(precision=self.precision, round=gmpy2.RoundDown):
            lower = self.lo + other.lo
        with gmpy2.context(precision=self.precision, round=gmpy2.RoundUp):
            upper = self.hi + other.hi
        return MPFRInterval(lower, upper, self.precision)

    def __radd__(self, other):
        return self + other

    def __sub__(self, other):
        other = self._operand(other)
        with gmpy2.context(precision=self.precision, round=gmpy2.RoundDown):
            lower = self.lo - other.hi
        with gmpy2.context(precision=self.precision, round=gmpy2.RoundUp):
            upper = self.hi - other.lo
        return MPFRInterval(lower, upper, self.precision)

    def __rsub__(self, other):
        return self._operand(other) - self

    def __mul__(self, other):
        other = self._operand(other)
        with gmpy2.context(precision=self.precision, round=gmpy2.RoundDown):
            lower_products = [self.lo * other.lo, self.lo * other.hi,
                              self.hi * other.lo, self.hi * other.hi]
        with gmpy2.context(precision=self.precision, round=gmpy2.RoundUp):
            upper_products = [self.lo * other.lo, self.lo * other.hi,
                              self.hi * other.lo, self.hi * other.hi]
        lower = min(lower_products)
        upper = max(upper_products)
        return MPFRInterval(lower, upper, self.precision)

    def __rmul__(self, other):
        return self * other

    def reciprocal(self):
        if self.contains(0):
            raise ZeroDivisionError("Reciprocal requires an interval excluding zero")
        one = gmpy2.mpfr(1)  # The integer one is exact at every supported precision.
        with gmpy2.context(precision=self.precision, round=gmpy2.RoundDown):
            lower = one / self.hi
        with gmpy2.context(precision=self.precision, round=gmpy2.RoundUp):
            upper = one / self.lo
        return MPFRInterval(lower, upper, self.precision)

    def __truediv__(self, other):
        other = self._operand(other)
        return self * other.reciprocal()

    def __rtruediv__(self, other):
        return self._operand(other) / self

