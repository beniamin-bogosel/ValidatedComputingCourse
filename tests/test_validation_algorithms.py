from fractions import Fraction

import pytest
from flint import arb, ctx

from vc.autodiff import Dual, jacobian2
from vc.arb_bridge import to_ball, from_ball
from vc.intervals import RationalInterval as I
from vc.roots import inspect_root, isolate_roots
from vc.systems import krawczyk, midpoint_inverse, inverse2
from vc.optimization import minimize
from vc.enclosures import combined_enclosure


def cubic(x):
    return (x + 2) * (x - 1) * (x - 3)


def cubic_derivative(X):
    return cubic(Dual(X, I(1))).derivative


@pytest.mark.parametrize("x", [Fraction(-2), Fraction(1, 3), Fraction(4)])
def test_dual_matches_independently_derived_polynomial_and_quotient(x):
    result = cubic(Dual(x, Fraction(1)))
    assert result.value == x**3 - 2*x**2 - 5*x + 6
    assert result.derivative == 3*x**2 - 4*x - 5
    result = (Dual(x, Fraction(1)) + 3) / (Dual(x, Fraction(1)) + 4)
    assert result.derivative == 1/(x + 4)**2
    assert (Dual(x, Fraction(1))**0).derivative == 0


@pytest.mark.parametrize("domain", [I(-3, -2), I(-1, 2), I("1/3", "2/3")])
def test_interval_ad_encloses_derivatives_at_exact_points(domain):
    derivative = cubic_derivative(domain)
    for x in [domain.lo, domain.midpoint(), domain.hi]:
        assert derivative.contains(3*x*x - 4*x - 5)


def test_arb_dual_chain_rules_and_context():
    original = ctx.prec
    with ctx.workprec(100):
        x = Dual(to_ball(I(0)), arb(1))
        result = x.exp() + x.sin() - x.cos()
        assert from_ball(result.value).contains(0)
        assert from_ball(result.derivative).contains(2)
    assert ctx.prec == original
    with pytest.raises(TypeError):
        bool(Dual(I(1), I(1)))
    with pytest.raises(ValueError):
        Dual(1, 1)**-1
    with pytest.raises(ZeroDivisionError):
        Dual(I(-1, 1), I(1)).reciprocal()


def circle_line(x, y):
    return [x*x + y*y - 1, x-y]


def circle_jacobian(box):
    return jacobian2(circle_line, box)


def test_jacobian_columns_are_not_rows():
    matrix = circle_jacobian([I(2), I(3)])
    expected = [[4, 6], [1, -1]]
    for row in range(2):
        for column in range(2):
            assert matrix[row][column].lo == matrix[row][column].hi == expected[row][column]


def test_root_certification_and_distinct_complete_cubic_search():
    result = isolate_roots(cubic, cubic_derivative, I(-3, 4))
    assert result.status == "complete"
    assert not result.unresolved
    assert len(result.certified) == 3
    for certificate, exact_root in zip(result.certified, [-2, 1, 3]):
        assert certificate.retained.contains(exact_root)
        assert not certificate.slopes.contains(0)
        assert certificate.domain.lo < certificate.newton.lo
        assert certificate.newton.hi < certificate.domain.hi
    for first, second in zip(result.certified, result.certified[1:]):
        assert first.retained.hi < second.retained.lo
    # Audit every discard/contract against independently known roots.
    for decision in result.decisions:
        for root in [-2, 1, 3]:
            if decision.domain.contains(root):
                assert not decision.status.startswith("excluded")
                if decision.retained is not None:
                    assert decision.retained.contains(root)


def test_newton_can_exclude_when_natural_image_contains_zero():
    # A deliberately coarse valid enclosure of f(x)=x+3 includes zero.
    # Exact midpoint information and the derivative can still exclude a root.
    def coarse(X):
        if X.width() == 0:
            return X + 3
        return I(-10, 10)
    decision = inspect_root(coarse, lambda X: I(1), I(0, 1))
    assert decision.status == "excluded_newton"


@pytest.mark.parametrize("budget", [1, 2, 5])
def test_root_budget_retains_each_known_root(budget):
    result = isolate_roots(cubic, cubic_derivative, I(-3, 4), max_steps=budget)
    possible = result.unresolved + [item.retained for item in result.certified]
    for root in [-2, 1, 3]:
        assert any(part.contains(root) for part in possible)
    assert result.status == "budget_exhausted"


def test_multiple_and_boundary_roots_remain_visible():
    multiple = isolate_roots(lambda X: X.square(), lambda X: 2*X, I(-1, 1), "1/100")
    assert multiple.status == "unresolved"
    assert not multiple.certified
    assert any(part.contains(0) for part in multiple.unresolved)
    boundary = isolate_roots(lambda X: X, lambda X: I(1), I(0, 1))
    assert boundary.status == "unresolved"
    assert any(part.contains(0) for part in boundary.unresolved)
    point = isolate_roots(lambda X: X, lambda X: I(1), I(0))
    assert point.status == "unresolved"


def test_sqrt_two_certificate_has_independent_exact_bounds():
    decision = inspect_root(lambda X: X.square()-2, lambda X: 2*X, I(1, 2))
    assert decision.status == "certified"
    assert decision.retained.lo**2 < 2 < decision.retained.hi**2


@pytest.mark.parametrize("sign", [-1, 1])
def test_krawczyk_certifies_both_circle_line_roots(sign):
    part = I("0.7", "0.72") if sign == 1 else I("-0.72", "-0.7")
    box = [part, part]
    result = krawczyk(circle_line, circle_jacobian, box, midpoint_inverse(circle_jacobian(box)))
    assert result.status == "unique_root"
    assert result.contraction_bound == Fraction(1, 71)
    for image in result.image:
        absolute = image if sign == 1 else -image
        assert 2*absolute.lo**2 < 1 < 2*absolute.hi**2


def test_system_exclusion_and_singular_preconditioner():
    box = [I(2, 3), I(2, 3)]
    result = krawczyk(circle_line, circle_jacobian, box, midpoint_inverse(circle_jacobian(box)))
    assert result.status == "excluded"
    with pytest.raises(ValueError, match="singular"):
        krawczyk(circle_line, circle_jacobian, box, [[1, 1], [1, 1]])
    with pytest.raises(TypeError):
        inverse2([[1.0, 0], [0, 1]])


def test_zero_residual_near_singular_system_does_not_imply_uniqueness():
    epsilon = Fraction(1, 10**6)
    def function(x, y):
        return [x+y, x+(1+epsilon)*y+x*x]
    def jacobian(box):
        return jacobian2(function, box)
    box = [I("-1/100", "1/100"), I("-1/100", "1/100")]
    result = krawczyk(function, jacobian, box, midpoint_inverse(jacobian(box)))
    assert all(value.lo == value.hi == 0 for value in result.residual)
    assert result.contraction_bound > 1
    assert result.status == "inconclusive"
    assert function(epsilon, -epsilon) == [0, 0]  # A second root is actually present.


def objective(X):
    return X.square().square() - 2*X.square()


def improved_objective(X):
    return combined_enclosure(objective, lambda X: 4*X*X*X-4*X, X)


@pytest.mark.parametrize("budget", [0, 1, 8, 64])
def test_optimization_preserves_all_minimizers_and_pruning_evidence(budget):
    result = minimize(improved_objective, I(-2, 2), "1/100", budget)
    assert result.minimum.contains(-1)
    for minimizer in [-1, 1]:
        assert any(piece.domain.contains(minimizer) for piece in result.candidates)
    assert result.domain.contains(result.witness)
    assert result.minimum.hi == result.witness_value.hi
    actual_value = result.witness**4 - 2*result.witness**2
    assert result.witness_value.contains(actual_value)
    for record in result.pruned:
        assert record.piece.enclosure.lo > record.incumbent_upper
        assert record.incumbent_upper >= -1
    terminal = [piece.domain for piece in result.candidates]
    terminal.extend(record.piece.domain for record in result.pruned)
    terminal.sort(key=lambda part: part.lo)
    assert terminal[0].lo == -2 and terminal[-1].hi == 2
    for left, right in zip(terminal, terminal[1:]):
        assert left.hi == right.lo
    if budget == 64:
        assert result.status == "gap_met"
        assert result.minimum.width() <= Fraction(1, 100)
    if budget == 0:
        assert result.status == "budget_exhausted"


def test_tied_minima_must_not_be_pruned_at_equality():
    result = minimize(lambda X: (X.square()-1).square(), I(-2, 2))
    assert result.status == "gap_met"
    assert result.minimum.lo == result.minimum.hi == 0
    for minimizer in [-1, 1]:
        assert any(piece.domain.contains(minimizer) for piece in result.candidates)
    assert len(result.candidates) == 2


def test_boundary_minimum_and_value_gap_without_localization():
    boundary = minimize(lambda X: X, I(0, 1))
    assert boundary.minimum.lo == boundary.minimum.hi == 0
    assert boundary.witness == 0
    assert boundary.candidates[0].domain.width() == 1
    constant = minimize(lambda X: I(3), I(-10, 10))
    assert constant.minimum.width() == 0
    assert constant.candidates[0].domain.width() == 20


def test_point_evaluator_can_be_precision_limited():
    result = minimize(lambda X: I(-1, 1), I(0), "1/100")
    assert result.status == "precision_limited"
    assert result.minimum.lo == -1 and result.minimum.hi == 1
