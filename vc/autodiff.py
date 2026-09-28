"""Small forward-mode dual numbers; the component arithmetic sets the guarantee.

Use floats for approximate experiments, rational intervals for polynomial bounds,
and Arb balls for elementary functions. Branches and nonsmooth operations are
outside this teaching implementation.
"""


class Dual:
    def __init__(self, value, derivative):
        self.value = value
        self.derivative = derivative

    def __repr__(self):
        return f"Dual(value={self.value}, derivative={self.derivative})"

    def _operand(self, other):
        if isinstance(other, Dual):
            return other
        zero = self.derivative * 0
        return Dual(other, zero)

    def __add__(self, other):
        other = self._operand(other)
        return Dual(self.value + other.value, self.derivative + other.derivative)

    def __radd__(self, other):
        return self + other

    def __neg__(self):
        return Dual(-self.value, -self.derivative)

    def __sub__(self, other):
        return self + (-self._operand(other))

    def __rsub__(self, other):
        return self._operand(other) - self

    def __mul__(self, other):
        other = self._operand(other)
        value = self.value * other.value
        first_term = self.derivative * other.value
        second_term = self.value * other.derivative
        return Dual(value, first_term + second_term)

    def __rmul__(self, other):
        return self * other

    def reciprocal(self):
        inverse = 1 / self.value
        derivative = -self.derivative * inverse * inverse
        return Dual(inverse, derivative)

    def __truediv__(self, other):
        return self * self._operand(other).reciprocal()

    def __rtruediv__(self, other):
        return self._operand(other) / self

    def __pow__(self, exponent):
        if not isinstance(exponent, int) or exponent < 0:
            raise ValueError("Only nonnegative integer powers are taught here")
        one = self.value * 0 + 1
        zero = self.derivative * 0
        result = Dual(one, zero)
        for step in range(exponent):
            result = result * self
        return result

    def exp(self):
        value = self.value.exp()  # Arb's enclosing elementary operation.
        return Dual(value, value * self.derivative)

    def sin(self):
        value = self.value.sin()
        derivative = self.value.cos() * self.derivative
        return Dual(value, derivative)

    def cos(self):
        value = self.value.cos()
        derivative = -self.value.sin() * self.derivative
        return Dual(value, derivative)

    def __bool__(self):
        raise TypeError("Branching on a dual number needs a separate analysis")


def jacobian2(function, box):
    """Two forward passes, one per input, for two outputs and two inputs.

    A constant output need not be wrapped in Dual; its derivative is zero.
    Other outputs must be computed using the supported dual-number operations.
    """
    if len(box) != 2:
        raise ValueError("Expected two input components")
    x, y = box
    zero_x, one_x = x * 0, x * 0 + 1
    zero_y, one_y = y * 0, y * 0 + 1
    first_column = function(Dual(x, one_x), Dual(y, zero_y))
    second_column = function(Dual(x, zero_x), Dual(y, one_y))
    if len(first_column) != 2 or len(second_column) != 2:
        raise ValueError("Expected two output components")
    matrix = []
    for row in range(2):
        first_output = first_column[row]
        second_output = second_column[row]
        if isinstance(first_output, Dual):
            first_derivative = first_output.derivative
        else:
            first_derivative = zero_x * first_output
        if isinstance(second_output, Dual):
            second_derivative = second_output.derivative
        else:
            second_derivative = zero_y * second_output
        matrix.append([first_derivative, second_derivative])
    return matrix
