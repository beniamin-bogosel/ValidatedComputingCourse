"""Visible 2-by-2 Krawczyk calculations using exact interval operations.

Local certification only. The caller supplies a C1 function and an enclosure of
its Jacobian throughout the box. No exhaustive system search is claimed.
"""

from dataclasses import dataclass
from fractions import Fraction
from vc.intervals import RationalInterval as Interval, exact_fraction


def require_matrix2(matrix):
    """Reject extra rows or columns instead of silently ignoring equations."""
    if len(matrix) != 2 or any(len(row) != 2 for row in matrix):
        raise ValueError("Expected a 2-by-2 matrix")


def matrix_vector(matrix, vector):
    require_matrix2(matrix)
    if len(vector) != 2:
        raise ValueError("Expected two vector components")
    result = []
    for row in range(2):
        total = Interval(0)
        for column in range(2):
            total = total + matrix[row][column] * vector[column]
        result.append(total)
    return result


def matrix_product(left, right):
    require_matrix2(left)
    require_matrix2(right)
    result = []
    for row in range(2):
        result_row = []
        for column in range(2):
            total = Interval(0)
            for index in range(2):
                total = total + left[row][index] * right[index][column]
            result_row.append(total)
        result.append(result_row)
    return result


def inverse2(matrix):
    """Invert an exact rational point matrix, not an interval matrix."""
    require_matrix2(matrix)
    a, b = [exact_fraction(value) for value in matrix[0]]
    c, d = [exact_fraction(value) for value in matrix[1]]
    determinant = a*d - b*c
    if determinant == 0:
        raise ValueError("The point matrix is singular")
    return [[d/determinant, -b/determinant], [-c/determinant, a/determinant]]


def midpoint_inverse(jacobian):
    require_matrix2(jacobian)
    midpoint_matrix = []
    for row in jacobian:
        midpoint_matrix.append([entry.midpoint() for entry in row])
    return inverse2(midpoint_matrix)


def row_sum_bound(matrix):
    """Upper bound on the infinity norm of every represented real matrix."""
    largest_sum = Fraction(0)
    for row in matrix:
        total = Fraction(0)
        for entry in row:
            total = total + max(abs(entry.lo), abs(entry.hi))
        largest_sum = max(largest_sum, total)
    return largest_sum


@dataclass
class SystemCertificate:
    box: list[Interval]
    center: list[Interval]
    preconditioner: list
    jacobian: list
    residual: list[Interval]
    remainder: list
    image: list[Interval]
    contraction_bound: Fraction
    status: str


def krawczyk(function, jacobian, box, preconditioner):
    if len(box) != 2 or any(part.width() <= 0 for part in box):
        raise ValueError("Use a two-dimensional box with positive side widths")
    R = [[exact_fraction(entry) for entry in row] for row in preconditioner]
    inverse2(R)  # Exact nonsingularity check: fixed points must be roots of f.
    center = [Interval(part.midpoint()) for part in box]
    residual = function(*center)
    if len(residual) != 2:
        raise ValueError("The function must return exactly two output components")
    J = jacobian(box)
    product = matrix_product(R, J)
    remainder = []
    for row in range(2):
        remainder_row = []
        for column in range(2):
            identity_entry = 1 if row == column else 0
            remainder_row.append(identity_entry - product[row][column])
        remainder.append(remainder_row)
    correction = matrix_vector(R, residual)
    displacement = [box[index] - center[index] for index in range(2)]
    spread = matrix_vector(remainder, displacement)
    image = []
    for index in range(2):
        image.append(center[index] - correction[index] + spread[index])
    q = row_sum_bound(remainder)
    disjoint = any(image[index].intersection(box[index]) is None for index in range(2))
    inside = all(box[index].lo < image[index].lo and image[index].hi < box[index].hi
                 for index in range(2))
    if disjoint:
        status = "excluded"
    elif inside and q < 1:
        status = "unique_root"
    else:
        status = "inconclusive"
    return SystemCertificate(box, center, R, J, residual, remainder, image, q, status)
