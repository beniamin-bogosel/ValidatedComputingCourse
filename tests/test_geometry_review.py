"""Regressions for geometry review, including uncertain complete trajectories."""
from fractions import Fraction

import gmpy2
import pytest
from flint import arb, ctx

from vc.intervals import RationalInterval as Interval
from vc.mirror_exploration import approximate_path
from vc.mirrors import final_distance, possible_hit, trace_lattice, trajectory_record


@pytest.mark.parametrize("precision", [24, 100])
def test_distance_of_complete_family_with_zero_containing_coordinate(precision):
    # No center is reachable before T=1/100: the exact endpoint family is
    # {(51/100, y): -1 <= y <= 1}. Its distance range starts at 51/100
    # and ends at sqrt((51/100)**2 + 1).
    result = trace_lattice("1/100", precision, initial_y=Interval(-1, 1))
    assert result.status == "complete"
    assert not result.collisions
    distance = final_distance(result)
    exact_x = Fraction(51, 100)
    largest_squared_distance = exact_x**2 + 1
    assert 0 <= distance.lo <= exact_x <= distance.hi
    assert distance.hi**2 >= largest_squared_distance
    assert distance.lo > Fraction(50, 100)
    assert distance.hi < Fraction(113, 100)


def test_translating_initial_height_translates_mirrors_and_endpoint():
    original = trace_lattice("3", 160)
    translated = trace_lattice("3", 160, initial_y="71/10")
    assert original.status == translated.status == "complete"
    original_sequence = [event.center for event in original.collisions]
    translated_sequence = [event.center for event in translated.collisions]
    assert translated_sequence == [(x, y + 7) for x, y in original_sequence]
    assert original.position[0].intersection(translated.position[0]) is not None
    assert (original.position[1] + 7).intersection(translated.position[1]) is not None


def test_geometric_misses_and_tangency_use_distinct_evidence():
    with ctx.workprec(100):
        radius = arb(1) / 3
        direction = [arb(1), arb(0)]
        moving_away = possible_hit([arb(1), arb(0)], direction, (0, 0), radius)
        misses_disk = possible_hit([arb(0), arb(1)], direction, (1, 0), radius)
        tangent = possible_hit([arb(0), radius], direction, (1, 0), radius)
        invalid_start = possible_hit([arb(0), arb(0)], direction, (0, 0), radius)
    assert moving_away.status == "miss_moving_away"
    assert misses_disk.status == "miss_discriminant"
    assert misses_disk.discriminant.hi < 0
    assert tangent.status == "inconclusive_tangent"
    assert tangent.discriminant.contains(0)
    assert invalid_start.status == "inconclusive_outside"


def test_incomplete_record_retains_last_event_time():
    result = trace_lattice("3", 100, max_collisions=1)
    record = trajectory_record(result)
    assert result.status == "inconclusive"
    assert record["reason"] == "collision_budget"
    assert len(record["collisions"]) == 1
    assert record["elapsed"] == record["collisions"][-1]["elapsed"]
    assert Fraction(record["elapsed"]["hi"]) < Fraction(record["final_time"])
    with pytest.raises(ValueError, match="incomplete"):
        final_distance(result)


@pytest.mark.parametrize("arguments", [{"precision": 2.5}, {"max_collisions": 0.5}])
def test_approximate_path_rejects_fractional_control_parameters(arguments):
    with pytest.raises(ValueError, match="integer"):
        approximate_path(**arguments)


def test_approximate_path_restores_arithmetic_context():
    before = gmpy2.get_context().copy()
    approximate_path("1/100", precision=24)
    after = gmpy2.get_context()
    assert after.precision == before.precision
    assert after.round == before.round
