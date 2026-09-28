from fractions import Fraction
from flint import ctx
import pytest

from vc.intervals import RationalInterval as I
from vc.arb_bridge import to_ball, from_ball, evaluate_ball
from vc.enclosures import (subdivide, range_enclosure, mean_value,
                           combined_enclosure, monotone_enclosure, adaptive_range)


@pytest.mark.parametrize("precision", [8, 53, 100])
@pytest.mark.parametrize("domain", [I("0.1", "0.3"), I(-2, 3), I("1/3"), I(10**30, 10**30 + 1)])
def test_ball_bridge_encloses_original_domain(precision, domain):
    with ctx.workprec(precision):
        recovered = from_ball(to_ball(domain))
    assert domain.is_subset_of(recovered)


def test_ball_arithmetic_and_failure_restore_precision():
    original = ctx.prec
    result = evaluate_ball(lambda x: x*x + 1, I(-1, 2), precision=100)
    assert I(1, 5).is_subset_of(result)
    with pytest.raises(ValueError, match="Nonfinite"):
        evaluate_ball(lambda x: x.log(), I(-2, -1), precision=100)
    with pytest.raises(TypeError):
        evaluate_ball(lambda x: float(x.mid()), I(1))
    assert ctx.prec == original


def parabola(X):
    return X * (1 - X)


def derivative(X):
    return 1 - 2*X


def test_subdivision_has_exact_coverage():
    pieces = subdivide(I("1/3", "5/3"), 4)
    assert len(pieces) == 16
    assert pieces[0].lo == Fraction(1, 3)
    assert pieces[-1].hi == Fraction(5, 3)
    for left, right in zip(pieces, pieces[1:]):
        assert left.hi == right.lo


def test_dependency_subdivision_preserves_known_range():
    previous = range_enclosure(parabola, I(0, 1), 0)
    for depth in range(1, 7):
        result = range_enclosure(parabola, I(0, 1), depth)
        assert I(0, "1/4").is_subset_of(result)
        assert result.is_subset_of(previous)
        previous = result


def test_centered_forms_and_monotonicity():
    domain = I("1/4", "3/4")
    centered = mean_value(parabola, derivative, domain)
    assert I("3/16", "1/4").is_subset_of(centered)
    combined = combined_enclosure(parabola, derivative, domain)
    assert combined.is_subset_of(parabola(domain))
    assert combined.is_subset_of(centered)
    assert monotone_enclosure(parabola, derivative, I(0, 1)) is None
    result = monotone_enclosure(parabola, derivative, I(0, "1/4"))
    assert result.lo == 0 and result.hi == Fraction(3, 16)


@pytest.mark.parametrize("budget", [1, 4, 64])
def test_adaptive_results_retain_coverage_even_when_unresolved(budget):
    result = adaptive_range(parabola, I(0, 1), Fraction(1, 16), budget)
    pieces = sorted(result.pieces, key=lambda piece: piece.domain.lo)
    assert len(pieces) <= budget
    assert pieces[0].domain.lo == 0 and pieces[-1].domain.hi == 1
    for left, right in zip(pieces, pieces[1:]):
        assert left.domain.hi == right.domain.lo
    assert I(0, "1/4").is_subset_of(result.enclosure)
    if result.status == "resolved":
        assert all(piece.enclosure.width() <= Fraction(1, 16) for piece in pieces)
    else:
        assert result.status == "budget_exhausted"
    if budget == 1:
        assert result.status == "budget_exhausted"
    if budget == 64:
        assert result.status == "resolved"


def test_local_width_target_does_not_mean_small_total_range():
    result = adaptive_range(lambda X: X, I(0, 1), "1/4", 4)
    assert result.status == "resolved"
    assert result.enclosure.width() == 1


def test_point_domain_can_be_precision_limited():
    def coarse_evaluation(X):
        return I(-1, 1)
    result = adaptive_range(coarse_evaluation, I(0), "1/10", 8)
    assert result.status == "precision_limited"
    assert result.enclosure.contains(0)
