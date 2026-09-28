from fractions import Fraction
import itertools
import pytest
from flint import ctx
from vc.geometry import determinant, orientation, orientation_bound, sign_of_interval
from vc.intervals import RationalInterval as I
from vc.mirrors import trace_lattice, final_distance, lattice_centers, HitCheck, select_first


@pytest.mark.parametrize('points', [((0,0),(1,0),(0,1)), ((0,0),(0,1),(1,0)),
                                   ((0,0),('1/3','2/3'),('2/3','4/3'))])
def test_filter_matches_exact_determinant_under_permutations(points):
    for ordered in itertools.permutations(points):
        exact = [tuple(Fraction(x) for x in point) for point in ordered]
        value = determinant(*exact)
        expected = (value > 0) - (value < 0)
        assert orientation(*ordered).sign == expected


def test_float_cancellation_and_exact_fallback():
    n = 2**27
    points = ((0,0), (n,n-1), (n+1,n))
    floats = [tuple(float(x) for x in point) for point in points]
    assert determinant(*floats) == 0
    assert determinant(*points) == 1
    result = orientation(*points, precisions=(24,))
    assert result.sign == 1 and result.method == 'fraction'
    assert result.exact_determinant == 1
    assert orientation(*points).sign == 1
    with pytest.raises(TypeError):
        orientation(*floats)


def test_uncertain_geometry_keeps_real_sign_ambiguity():
    a, b = (I(0), I(0)), (I(1), I(1))
    c = (I(2), I('1.999', '2.001'))
    for bits in [24,100,200]:
        bound = orientation_bound(a,b,c,bits)
        assert bound.lo < 0 < bound.hi
        assert sign_of_interval(bound) is None
    with pytest.raises(TypeError):
        orientation(a,b,c)


def test_mirror_first_hit_and_endpoint_have_independent_exact_solution():
    # Horizontal normal incidence: contact (2/3,0) at t=1/6, then reverse.
    result = trace_lattice('1/4', 100, initial_y=0)
    assert result.status == 'complete'
    assert len(result.collisions) == 1
    event = result.collisions[0]
    assert event.center == (1,0)
    assert event.flight_time.contains(Fraction(1,6))
    assert event.position[0].contains(Fraction(2,3))
    assert event.position[1].contains(0)
    assert event.direction[0].contains(-1)
    assert event.direction[1].contains(0)
    assert event.departure.lo > 0
    assert result.position[0].contains(Fraction(7,12))
    assert result.position[1].contains(0)
    assert final_distance(result).contains(Fraction(7,12))


def test_free_flight_endpoint_before_first_collision():
    result = trace_lattice('1/100', 100)
    assert result.status == 'complete' and not result.collisions
    assert result.position[0].contains(Fraction(51,100))
    assert result.position[1].contains(Fraction(1,10))


def test_standard_short_path_and_every_event_order():
    result = trace_lattice('3', 100)
    assert result.status == 'complete'
    assert [event.center for event in result.collisions] == [(1,0),(-1,1),(0,2)]
    previous_time = I(0)
    for event, checks in zip(result.collisions, result.checks):
        selected = next(check for check in checks if check.center == event.center)
        assert selected.status == 'hit'
        assert selected.time.lo > 0 and selected.discriminant.lo > 0
        assert selected.time.hi < result.final_time - previous_time.hi
        assert all(selected.time.hi < check.time.lo for check in checks
                   if check.status == 'hit' and check.center != event.center)
        assert not any(check.status.startswith('inconclusive') for check in checks)
        assert len(checks) == len(result.centers)
        previous_time = event.elapsed
    assert result.elapsed.lo == result.elapsed.hi == 3
    assert max(part.width() for part in result.position) < Fraction(1,10**20)
    final_status, _ = select_first(result.checks[-1], I(3)-previous_time)
    assert final_status == 'finish'


def test_reachable_lattice_rectangle_does_not_omit_nearby_centers():
    initial = (I('1/2'),I('0.09','0.11'))
    time, radius = Fraction(3), Fraction(1,3)
    centers = set(lattice_centers(initial,time,radius))
    for x in range(-6,7):
        for y in range(-6,7):
            if (x,y) not in centers:
                # At least one coordinate is strictly beyond the reachable band.
                assert (x < initial[0].lo-time-radius or x > initial[0].hi+time+radius
                        or y < initial[1].lo-time-radius or y > initial[1].hi+time+radius)


@pytest.mark.parametrize('kwargs', [{'precision':24}, {'max_collisions':0},
                                     {'initial_y':'1/3'}, {'final_time':'1/6','initial_y':0}])
def test_ambiguous_or_budget_limited_ray_does_not_claim_endpoint(kwargs):
    result = trace_lattice(**kwargs)
    assert result.status == 'inconclusive'
    assert result.reason
    with pytest.raises(ValueError, match='incomplete'):
        final_distance(result)


def test_uncertain_initial_data_are_not_erased_by_precision():
    y = I('0.099999','0.100001')
    for bits in [100,200]:
        result = trace_lattice('1/4',bits,y)
        assert result.status == 'complete'
        assert result.position[1].width() > Fraction(1,10**6)
    assert trace_lattice('3',100,y).status == 'inconclusive'


def test_event_selector_requires_separation_and_horizon_proof():
    checks = [HitCheck((0,0),'hit',I(1,2)),HitCheck((1,0),'hit',I('3/2','5/2'))]
    assert select_first(checks,I(4))[0] == 'inconclusive_order'
    checks = [HitCheck((0,0),'hit',I(1,2))]
    assert select_first(checks,I('3/2'))[0] == 'inconclusive_horizon'
    assert select_first(checks,I('1/2'))[0] == 'finish'
    assert select_first(checks,I(3))[0] == 'collision'


def test_arithmetic_context_restored_after_project_run():
    before = ctx.prec
    trace_lattice('1/4',100)
    assert ctx.prec == before
    orientation((0,0),(1,0),(0,1))
    assert ctx.prec == before


def test_exported_certificate_keeps_exact_endpoint_values():
    import json
    from vc.mirrors import trajectory_record
    result = trace_lattice('1/4',100,initial_y=0)
    record = json.loads(json.dumps(trajectory_record(result)))
    assert Fraction(record['position'][0]['lo']) == result.position[0].lo
    assert Fraction(record['position'][0]['hi']) == result.position[0].hi
    assert len(record['checks']) == len(result.collisions)+1
    assert record['status'] == 'complete'
