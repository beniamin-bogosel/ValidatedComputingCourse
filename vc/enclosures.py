"""Readable one-dimensional range algorithms for Lectures 06–07.

Every evaluator and derivative evaluator must return a valid RationalInterval
enclosure on its whole input interval. These routines do not prove that premise.
"""

from dataclasses import dataclass
from fractions import Fraction

from vc.intervals import RationalInterval, exact_fraction


def subdivide(domain, depth):
    if not isinstance(depth, int) or depth < 0:
        raise ValueError("depth must be a nonnegative integer")
    pieces = [domain]
    for level in range(depth):
        next_pieces = []
        for piece in pieces:
            if piece.width() == 0:
                next_pieces.append(piece)
            else:
                left, right = piece.bisect()
                next_pieces.append(left)
                next_pieces.append(right)
        pieces = next_pieces
    return pieces


def range_enclosure(evaluate, domain, depth=0):
    pieces = subdivide(domain, depth)
    enclosure = evaluate(pieces[0])
    for piece in pieces[1:]:
        local_enclosure = evaluate(piece)
        enclosure = enclosure.hull(local_enclosure)
    return enclosure


def mean_value(evaluate, derivative, domain):
    """Enclose a C1 function using its value at the midpoint and slopes on domain."""
    center = RationalInterval(domain.midpoint())
    center_value = evaluate(center)
    slope_bounds = derivative(domain)
    displacement = domain - center
    return center_value + slope_bounds * displacement


def combined_enclosure(evaluate, derivative, domain):
    natural = evaluate(domain)
    centered = mean_value(evaluate, derivative, domain)
    common = natural.intersection(centered)
    if common is None:
        raise ValueError("Inconsistent enclosures: inspect the evaluators and derivative")
    return common


def monotone_enclosure(evaluate, derivative, domain):
    """Use the endpoint values when a C1 function's derivative has one sign."""
    slope = derivative(domain)
    if slope.lo >= 0 or slope.hi <= 0:
        left_value = evaluate(RationalInterval(domain.lo))
        right_value = evaluate(RationalInterval(domain.hi))
        return left_value.hull(right_value)
    return None  # The derivative test is inconclusive, not a proof of nonmonotonicity.


@dataclass
class RangePiece:
    domain: RationalInterval
    enclosure: RationalInterval


@dataclass
class RangeResult:
    enclosure: RationalInterval
    pieces: list[RangePiece]
    status: str
    tolerance: Fraction


def adaptive_range(evaluate, domain, tolerance, max_boxes=128):
    """Split the widest image until all local image widths meet a target.

    Even a budget-limited result encloses the whole original domain. The target
    concerns EACH LOCAL IMAGE, not the total range width and not root uniqueness.
    """
    tolerance = exact_fraction(tolerance)
    if tolerance <= 0:
        raise ValueError("tolerance must be positive")
    if not isinstance(max_boxes, int) or max_boxes < 1:
        raise ValueError("max_boxes must be a positive integer")
    pieces = [RangePiece(domain, evaluate(domain))]

    while True:
        widest_index = 0
        for index in range(1, len(pieces)):
            if pieces[index].enclosure.width() > pieces[widest_index].enclosure.width():
                widest_index = index
        widest = pieces[widest_index]

        if widest.enclosure.width() <= tolerance:
            status = "resolved"
            break
        if len(pieces) >= max_boxes:
            status = "budget_exhausted"
            break
        if widest.domain.width() == 0:
            status = "precision_limited"
            break

        left, right = widest.domain.bisect()
        left_piece = RangePiece(left, evaluate(left))
        right_piece = RangePiece(right, evaluate(right))
        pieces.pop(widest_index)
        pieces.append(left_piece)
        pieces.append(right_piece)

    enclosure = pieces[0].enclosure
    for piece in pieces[1:]:
        enclosure = enclosure.hull(piece.enclosure)
    return RangeResult(enclosure, pieces, status, tolerance)
