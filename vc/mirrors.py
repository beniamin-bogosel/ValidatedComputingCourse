"""A conservative short ray certificate for disjoint circular mirrors.

The public experiment uses the integer lattice, radius 1/3, eastward unit speed,
x=1/2, and exact or interval initial y. All branches use Arb enclosures. Failure
returns the last certified state, never an invented final-time endpoint.
"""
from dataclasses import dataclass, field
from fractions import Fraction
import math
from flint import arb, ctx
from vc.intervals import RationalInterval as Interval, as_interval, exact_fraction
from vc.arb_bridge import to_ball, from_ball


def dot(left, right):
    return left[0]*right[0] + left[1]*right[1]


def lattice_centers(initial, final_time, radius=Fraction(1, 3)):
    """All lattice disks possibly reachable at speed one by final_time.

    A colliding center is at most final_time + radius away in each coordinate
    from some initial point. Centers outside this rectangle cannot be reached.
    """
    lower_x = math.ceil(initial[0].lo - final_time - radius)
    upper_x = math.floor(initial[0].hi + final_time + radius)
    lower_y = math.ceil(initial[1].lo - final_time - radius)
    upper_y = math.floor(initial[1].hi + final_time + radius)
    centers = []
    for x in range(lower_x, upper_x + 1):
        for y in range(lower_y, upper_y + 1):
            centers.append((x, y))
    return centers


@dataclass
class HitCheck:
    center: tuple[int, int]
    status: str
    time: Interval | None = None
    discriminant: Interval | None = None


def possible_hit(position, direction, center, radius):
    """Arb inputs; caller owns precision. The current mirror is handled separately."""
    offset = [position[index] - center[index] for index in range(2)]
    a = dot(direction, direction)
    b = 2*dot(offset, direction)
    c = dot(offset, offset) - radius*radius
    if not a > 0 or not c > 0:
        return HitCheck(center, "inconclusive_outside")
    if b >= 0:
        return HitCheck(center, "miss_moving_away")
    discriminant = b*b - 4*a*c
    bound = from_ball(discriminant)
    if discriminant < 0:
        return HitCheck(center, "miss_discriminant", discriminant=bound)
    if not discriminant > 0:
        return HitCheck(center, "inconclusive_tangent", discriminant=bound)
    # Rationalized smaller root avoids subtracting nearly equal positive values.
    time = 2*c / (-b + discriminant.sqrt())
    time_bound = from_ball(time)
    if time_bound.lo <= 0:
        return HitCheck(center, "inconclusive_time", time_bound, bound)
    return HitCheck(center, "hit", time_bound, bound)


def select_first(checks, remaining):
    """Certify a strict event order or a collision-free remainder of the flight."""
    if any(check.status.startswith("inconclusive") for check in checks):
        return "inconclusive_geometry", None
    hits = [check for check in checks if check.status == "hit"]
    if not hits or all(check.time.lo > remaining.hi for check in hits):
        return "finish", None
    first = min(hits, key=lambda check: check.time.lo)
    if any(first.time.hi >= other.time.lo for other in hits if other is not first):
        return "inconclusive_order", None
    if first.time.hi >= remaining.lo:
        return "inconclusive_horizon", None
    return "collision", first


@dataclass
class Collision:
    center: tuple[int, int]
    elapsed: Interval
    flight_time: Interval
    position: tuple[Interval, Interval]
    direction: tuple[Interval, Interval]
    departure: Interval


@dataclass
class Trajectory:
    initial: tuple[Interval, Interval]
    final_time: Fraction
    precision: int
    centers: list[tuple[int, int]]
    elapsed: Interval
    position: tuple[Interval, Interval]
    direction: tuple[Interval, Interval]
    status: str = "inconclusive"
    reason: str = ""
    collisions: list[Collision] = field(default_factory=list)
    checks: list[list[HitCheck]] = field(default_factory=list)


def trace_lattice(final_time="3", precision=100, initial_y="1/10", max_collisions=32,
                  choose=select_first):
    """The optional lab callback must satisfy select_first's enclosure contract."""
    final_time = exact_fraction(final_time)
    if final_time <= 0:
        raise ValueError("final_time must be positive")
    if not isinstance(precision, int) or precision < 2:
        raise ValueError("precision must be at least two bits")
    if not isinstance(max_collisions, int) or max_collisions < 0:
        raise ValueError("max_collisions must be nonnegative")
    initial = (Interval("1/2"), as_interval(initial_y))
    centers = lattice_centers(initial, final_time)
    result = Trajectory(initial, final_time, precision, centers, Interval(0),
                        initial, (Interval(1), Interval(0)))
    with ctx.workprec(precision):
        radius = arb(1)/3
        position = [to_ball(part) for part in initial]
        direction = [arb(1), arb(0)]
        elapsed = arb(0)
        horizon = to_ball(Interval(final_time))
        previous = None
        while True:
            remaining = horizon - elapsed
            checks = []
            for center in centers:
                if center == previous:
                    # The actual state lies ON this mirror and points strictly
                    # outward, as checked when the preceding reflection was made.
                    checks.append(HitCheck(center, "miss_departing"))
                else:
                    checks.append(possible_hit(position, direction, center, radius))
            result.checks.append(checks)
            action, hit = choose(checks, from_ball(remaining))
            if action == "finish":
                endpoint = [position[index] + remaining*direction[index] for index in range(2)]
                result.position = tuple(from_ball(value) for value in endpoint)
                result.elapsed = Interval(final_time)
                result.status = "complete"
                result.reason = "All collisions before the requested time were resolved"
                return result
            if action != "collision":
                result.reason = action
                return result
            if len(result.collisions) >= max_collisions:
                result.reason = "collision_budget"
                return result
            flight_time = to_ball(hit.time)
            contact = [position[index] + flight_time*direction[index] for index in range(2)]
            normal = [contact[index] - hit.center[index] for index in range(2)]
            scale = 2*dot(direction, normal)/(radius*radius)
            reflected = [direction[index] - scale*normal[index] for index in range(2)]
            departure = dot(reflected, normal)
            if not departure > 0:
                result.reason = "inconclusive_departure"
                return result
            elapsed = elapsed + flight_time
            position, direction = contact, reflected
            result.elapsed = from_ball(elapsed)
            result.position = tuple(from_ball(value) for value in position)
            result.direction = tuple(from_ball(value) for value in direction)
            result.collisions.append(Collision(hit.center, result.elapsed, hit.time,
                                               result.position, result.direction,
                                               from_ball(departure)))
            previous = hit.center


def final_distance(result):
    """Enclose distance from the origin for a completed trajectory family."""
    if result.status != "complete":
        raise ValueError("An incomplete path has no certified final-time distance")
    x, y = result.position
    squared_distance = x.square() + y.square()
    with ctx.workprec(result.precision):
        # Coordinate intervals may contain zero. Exact interval squares keep
        # their nonnegative ranges; repeated ball multiplication may not.
        # Bound the two square roots separately so converting [0, upper] to
        # a ball cannot introduce a negative argument through radius rounding.
        lower_root = to_ball(Interval(squared_distance.lo)).sqrt()
        upper_root = to_ball(Interval(squared_distance.hi)).sqrt()
        lower = max(Fraction(0), from_ball(lower_root).lo)
        upper = from_ball(upper_root).hi
        return Interval(lower, upper)


def trajectory_record(result):
    """JSON-ready exact endpoints and event evidence; no rounded float exports."""
    def interval(value):
        return {"lo": str(value.lo), "hi": str(value.hi)}

    def vector(values):
        return [interval(value) for value in values]

    collisions = []
    for event in result.collisions:
        collisions.append({"center": list(event.center), "elapsed": interval(event.elapsed),
                           "flight_time": interval(event.flight_time),
                           "position": vector(event.position), "direction": vector(event.direction),
                           "departure": interval(event.departure)})
    flights = []
    for checks in result.checks:
        records = []
        for check in checks:
            records.append({"center": list(check.center), "status": check.status,
                            "time": None if check.time is None else interval(check.time),
                            "discriminant": None if check.discriminant is None else interval(check.discriminant)})
        flights.append(records)
    return {"model": "integer-lattice circular mirrors, radius 1/3, initial velocity (1,0)",
            "initial": vector(result.initial), "final_time": str(result.final_time),
            "precision_bits": result.precision, "centers": [list(center) for center in result.centers],
            "status": result.status, "reason": result.reason,
            "elapsed": interval(result.elapsed), "position": vector(result.position),
            "direction": vector(result.direction), "collisions": collisions, "checks": flights}
