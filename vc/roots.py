"""Conservative scalar interval Newton search with a record of every decision.

Premises: a continuously differentiable real function on a neighborhood of the
search interval, and valid function/derivative interval evaluators. Callbacks do
not establish these premises merely by returning the expected type.
"""

from dataclasses import dataclass, field
from vc.intervals import RationalInterval as Interval, exact_fraction


@dataclass
class RootDecision:
    domain: Interval
    image: Interval
    status: str
    slopes: Interval | None = None
    newton: Interval | None = None
    retained: Interval | None = None


def inspect_root(evaluate, derivative, domain):
    image = evaluate(domain)
    if not image.contains(0):
        return RootDecision(domain, image, "excluded_range")
    slopes = derivative(domain)
    if slopes.contains(0):
        return RootDecision(domain, image, "split", slopes)
    center = Interval(domain.midpoint())
    newton = center - evaluate(center) / slopes
    retained = domain.intersection(newton)
    if retained is None:
        return RootDecision(domain, image, "excluded_newton", slopes, newton)
    if domain.lo < newton.lo and newton.hi < domain.hi:
        return RootDecision(domain, image, "certified", slopes, newton, retained)
    if retained.width() < domain.width() / 2:
        return RootDecision(domain, image, "contract", slopes, newton, retained)
    return RootDecision(domain, image, "split", slopes, newton, retained)


@dataclass
class RootSearch:
    domain: Interval
    certified: list[RootDecision] = field(default_factory=list)
    unresolved: list[Interval] = field(default_factory=list)
    decisions: list[RootDecision] = field(default_factory=list)
    status: str = "unresolved"


def isolate_roots(evaluate, derivative, domain, tolerance="1/10000", max_steps=256,
                  inspect=inspect_root):
    """Certify simple roots; tolerance only stops unresolved small boxes.

    A certified interval need not have width <= tolerance. Root containment is
    retained by contraction, not literal coverage of every non-root point.
    The inspect callback is exposed for the lab and must obey the same theorem.
    """
    tolerance = exact_fraction(tolerance)
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if not isinstance(max_steps, int) or max_steps < 1:
        raise ValueError("max_steps must be a positive integer")
    result = RootSearch(domain)
    pending = [domain]
    while pending and len(result.decisions) < max_steps:
        current = pending.pop()
        decision = inspect(evaluate, derivative, current)
        result.decisions.append(decision)
        if decision.status.startswith("excluded_"):
            continue
        if decision.status == "certified":
            result.certified.append(decision)
        elif current.width() <= tolerance:
            result.unresolved.append(current)
        elif decision.status == "contract":
            pending.append(decision.retained)
        else:
            left, right = current.bisect()
            pending.append(right)
            pending.append(left)
    if pending:
        result.unresolved.extend(pending)
        result.status = "budget_exhausted"
    elif result.unresolved:
        result.status = "unresolved"
    else:
        result.status = "complete"
    result.certified.sort(key=lambda certificate: certificate.retained.lo)
    return result
