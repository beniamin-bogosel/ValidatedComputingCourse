"""Nearest-rounded ray exploration. Outputs are approximations, not certificates."""
from fractions import Fraction
import gmpy2
from vc.intervals import RationalInterval as Interval, exact_fraction
from vc.mirrors import lattice_centers


def approximate_path(final_time="3", precision=53, initial_y="1/10", max_collisions=100):
    final_time = exact_fraction(final_time)
    initial_y = exact_fraction(initial_y)
    if final_time <= 0:
        raise ValueError("final_time must be positive")
    if not isinstance(precision, int) or precision < 2:
        raise ValueError("precision must be an integer of at least two bits")
    if not isinstance(max_collisions, int) or max_collisions < 0:
        raise ValueError("max_collisions must be a nonnegative integer")
    initial = (Interval("1/2"), Interval(initial_y))
    centers = lattice_centers(initial, final_time)
    with gmpy2.context(precision=precision, round=gmpy2.RoundToNearest):
        def number(value):
            value = Fraction(value)
            return gmpy2.mpfr(gmpy2.mpq(value.numerator, value.denominator))
        x, y = number(Fraction(1, 2)), number(initial_y)
        vx, vy = number(1), number(0)
        radius = number(Fraction(1, 3))
        time = number(0)
        target = number(final_time)
        points = [(x, y)]
        sequence = []
        previous = None
        while True:
            best_time = None
            best_center = None
            for center in centers:
                if center == previous:
                    continue
                dx, dy = x-center[0], y-center[1]
                a = vx*vx + vy*vy
                b = 2*(dx*vx + dy*vy)
                c = dx*dx + dy*dy - radius*radius
                discriminant = b*b - 4*a*c
                if c <= 0:
                    raise ArithmeticError("Approximate state is not outside another mirror")
                if b >= 0 or discriminant <= 0:
                    continue
                flight = 2*c/(-b+gmpy2.sqrt(discriminant))
                if flight > 0 and (best_time is None or flight < best_time):
                    best_time, best_center = flight, center
            remaining = target-time
            if best_time is None or best_time >= remaining:
                x, y = x+remaining*vx, y+remaining*vy
                points.append((x, y))
                return {"endpoint": (x, y), "points": points, "sequence": sequence,
                        "precision": precision}
            if len(sequence) >= max_collisions:
                raise ArithmeticError("Approximate collision budget exhausted")
            x, y = x+best_time*vx, y+best_time*vy
            dx, dy = x-best_center[0], y-best_center[1]
            scale = 2*(vx*dx + vy*dy)/(radius*radius)
            vx, vy = vx-scale*dx, vy-scale*dy
            time = time + best_time
            points.append((x, y))
            sequence.append(best_center)
            previous = best_center
