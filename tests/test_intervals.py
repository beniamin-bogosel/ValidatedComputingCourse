from fractions import Fraction
import operator

import gmpy2
import pytest

from vc.intervals import RationalInterval as I
from vc.mpfr_intervals import MPFRInterval


DOMAINS = [(-3, -1), (-2, 3), (0, 0), (0, 2), (1, 4)]


@pytest.mark.parametrize("a,b", DOMAINS)
@pytest.mark.parametrize("c,d", DOMAINS)
def test_exact_operations_cover_corner_values(a, b, c, d):
    X, Y = I(a, b), I(c, d)
    for operation in [operator.add, operator.sub, operator.mul]:
        result = operation(X, Y)
        values = []
        for x in [Fraction(a), Fraction(b)]:
            for y in [Fraction(c), Fraction(d)]:
                values.append(operation(x, y))
        assert result.lo == min(values)
        assert result.hi == max(values)


def test_square_keeps_one_variable_dependency():
    X = I(-2, 3)
    assert (X * X).lo == -6
    assert X.square().lo == 0
    assert X.square().hi == 9
    assert I(-3, -2).square().lo == 4


def test_set_operations_and_boundary_contact():
    assert I(0, 1).intersection(I(2, 3)) is None
    contact = I(0, 1).intersection(I(1, 2))
    assert contact.lo == contact.hi == 1
    hull = I(0, 1).hull(I(2, 3))
    assert hull.lo == 0 and hull.hi == 3
    left, right = I("0.1", "0.3").bisect()
    assert left.hi == right.lo == Fraction(1, 5)


def test_domain_errors_are_explicit():
    with pytest.raises(ZeroDivisionError):
        I(1) / I(-1, 1)
    with pytest.raises(ValueError):
        I(2, 1)
    with pytest.raises(TypeError):
        I(0.1)
    with pytest.raises(ValueError):
        I(1).bisect()


@pytest.mark.parametrize("precision", [8, 24, 80])
@pytest.mark.parametrize("a,b", DOMAINS)
@pytest.mark.parametrize("c,d", [(-4, -1), (1, 3)])
def test_mpfr_operations_enclose_exact_rational_results(precision, a, b, c, d):
    X = I(Fraction(a, 3), Fraction(b, 3))
    Y = I(Fraction(c, 7), Fraction(d, 7))
    MX = MPFRInterval(X.lo, X.hi, precision)
    MY = MPFRInterval(Y.lo, Y.hi, precision)
    for operation in [operator.add, operator.sub, operator.mul, operator.truediv]:
        exact = operation(X, Y)
        computed = operation(MX, MY).exact_bounds()
        assert exact.is_subset_of(computed)


def test_mpfr_input_rounding_and_context_restoration():
    before = gmpy2.get_context().precision, gmpy2.get_context().round
    X = MPFRInterval("0.1", precision=8)
    assert X.contains(Fraction(1, 10))
    assert X.width() > 0
    with pytest.raises(ValueError):
        X + MPFRInterval(1, precision=9)
    with pytest.raises(TypeError):
        MPFRInterval(0.1)
    with pytest.raises(ZeroDivisionError):
        MPFRInterval(-1, 1).reciprocal()
    assert before == (gmpy2.get_context().precision, gmpy2.get_context().round)


def test_exact_positive_sum_can_escape_a_naive_float_interval():
    x = Fraction.from_float(0.1)
    y = Fraction.from_float(0.3)
    computed = Fraction.from_float(0.1 + 0.3)
    assert x + y != computed
    result = MPFRInterval(x) + MPFRInterval(y)
    assert result.contains(x + y)

