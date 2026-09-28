"""One-dimensional branch-and-bound with explicit minimizer preservation.

The evaluator must enclose a continuous real function on every input interval.
The original domain is compact. Strict pruning retains ties and all minimizers.
"""

from dataclasses import dataclass
from fractions import Fraction
from vc.intervals import RationalInterval as Interval, exact_fraction
from vc.enclosures import RangePiece


@dataclass
class PrunedPiece:
    piece: RangePiece
    incumbent_upper: Fraction


@dataclass
class MinimumResult:
    domain: Interval
    minimum: Interval
    candidates: list[RangePiece]
    witness: Fraction
    witness_value: Interval
    pruned: list[PrunedPiece]
    splits: int
    status: str


def minimize(evaluate, domain, tolerance="1/1000", max_splits=128):
    tolerance = exact_fraction(tolerance)
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if not isinstance(max_splits, int) or max_splits < 0:
        raise ValueError("max_splits must be a nonnegative integer")
    witness = domain.midpoint()
    witness_value = evaluate(Interval(witness))
    # Endpoints are feasible points too; do not assume a minimum is stationary.
    for point in [domain.lo, domain.hi]:
        value = evaluate(Interval(point))
        if value.hi < witness_value.hi:
            witness, witness_value = point, value
    candidates = [RangePiece(domain, evaluate(domain))]
    pruned = []
    splits = 0
    while True:
        upper = witness_value.hi
        retained = []
        for piece in candidates:
            if piece.enclosure.lo > upper:
                pruned.append(PrunedPiece(piece, upper))
            else:
                retained.append(piece)
        candidates = retained
        if not candidates:
            raise ValueError("Inconsistent evaluator: every feasible candidate was pruned")
        best_index = 0
        for index in range(1, len(candidates)):
            current = candidates[index]
            best = candidates[best_index]
            if current.enclosure.lo < best.enclosure.lo:
                best_index = index
            elif current.enclosure.lo == best.enclosure.lo:
                if current.domain.width() > best.domain.width():
                    best_index = index
        best = candidates[best_index]
        lower = best.enclosure.lo
        if upper - lower <= tolerance:
            status = "gap_met"
            break
        if splits >= max_splits:
            status = "budget_exhausted"
            break
        if best.domain.width() == 0:
            status = "precision_limited"
            break
        left, right = best.domain.bisect()
        candidates.pop(best_index)
        for child in [left, right]:
            candidates.append(RangePiece(child, evaluate(child)))
            point = child.midpoint()
            value = evaluate(Interval(point))
            if value.hi < witness_value.hi:
                witness, witness_value = point, value
        splits += 1
    return MinimumResult(domain, Interval(lower, upper), candidates, witness,
                         witness_value, pruned, splits, status)
