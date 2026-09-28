"""Regressions for certificate and classroom edge cases found in final review."""

import pytest

from vc.autodiff import jacobian2
from vc.intervals import RationalInterval as I
from vc.systems import inverse2, krawczyk, matrix_product, matrix_vector


def identity_jacobian(box):
    return [[I(1), I(0)], [I(0), I(1)]]


def test_system_certificate_rejects_an_extra_inconsistent_equation():
    # The first two equations have a root, but the full system has none.
    # Truncation used to give a false unique-root certificate.
    def inconsistent_system(x, y):
        return [x, y, I(1)]

    box = [I(-1, 1), I(-1, 1)]
    with pytest.raises(ValueError, match="exactly two output components"):
        krawczyk(inconsistent_system, identity_jacobian, box, [[1, 0], [0, 1]])


@pytest.mark.parametrize("matrix", [
    [[1, 0], [0, 1], [0, 0]],
    [[1, 0, 0], [0, 1, 0]],
    [[1, 0], [0]],
])
def test_point_inverse_rejects_every_non_2_by_2_shape(matrix):
    with pytest.raises(ValueError, match="2-by-2"):
        inverse2(matrix)


def test_system_certificate_rejects_an_oversized_jacobian():
    def oversized_jacobian(box):
        return [[I(1), I(0)], [I(0), I(1)], [I(0), I(0)]]

    box = [I(-1, 1), I(-1, 1)]
    with pytest.raises(ValueError, match="2-by-2"):
        krawczyk(lambda x, y: [x, y], oversized_jacobian, box, [[1, 0], [0, 1]])


def test_matrix_operations_do_not_silently_truncate_inputs():
    identity = [[1, 0], [0, 1]]
    with pytest.raises(ValueError, match="two vector components"):
        matrix_vector(identity, [I(0), I(0), I(1)])
    with pytest.raises(ValueError, match="2-by-2"):
        matrix_product(identity, [[1, 0, 0], [0, 1, 0]])


def test_jacobian_allows_a_constant_output_component():
    matrix = jacobian2(lambda x, y: [x + 2*y, 1], [I(-1, 1), I(2, 3)])
    expected = [[1, 2], [0, 0]]
    for row in range(2):
        for column in range(2):
            entry = matrix[row][column]
            assert entry.lo == entry.hi == expected[row][column]


def test_jacobian_does_not_treat_a_missing_output_as_a_constant():
    with pytest.raises(TypeError):
        jacobian2(lambda x, y: [x, None], [I(-1, 1), I(2, 3)])
