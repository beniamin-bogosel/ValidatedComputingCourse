# Python Stack for a Validated Computing Course

## Goal

Use a **Python-first programming stack** for a Master's-level course on validated computing and interval arithmetic.

The intended progression is:

$$
\boxed{
\texttt{float}
\to
\texttt{Fraction/Decimal}
\to
\texttt{gmpy2.mpfr}
\to
\text{student-built endpoint intervals}
\to
\texttt{python-flint / Arb}
\to
\text{validated algorithms}
}
$$

The course should culminate in serious rigorous computations using **python-flint**, while students first learn the underlying ideas by implementing simpler interval arithmetic themselves.

---

# Why Python?

Python is a strong choice for this course because:

- most Master's CS students already know it;
- it gives direct access to ordinary floating-point arithmetic;
- it has exact integers and rationals;
- it has arbitrary-precision decimal arithmetic in the standard library;
- MPFR arbitrary-precision binary floating point is available through `gmpy2`;
- rigorous ball arithmetic is available through `python-flint`;
- Jupyter notebooks make experiments and labs easy to distribute;
- students can focus on numerical ideas rather than learning a new language.

The main caveat is:

> Python does not have a native interval type.

This is actually useful pedagogically. Students can first build a minimal interval class themselves and later switch to a trusted rigorous library.

---

# 1. Ordinary Floating Point: Python `float`

Python's built-in

```python
float
```

is the natural starting point.

On standard platforms it corresponds to IEEE 754 binary64 arithmetic.

This is ideal for studying:

- machine precision;
- rounding;
- neighboring floating-point numbers;
- overflow;
- underflow;
- cancellation;
- loss of significance;
- unstable algorithms.

Useful tools include:

```python
import math
import sys

print(sys.float_info)
print(math.nextafter(1.0, math.inf))
print(math.nextafter(1.0, -math.inf))
```

Typical examples:

```python
print(0.1 + 0.2 == 0.3)
```

and

```python
x = 1e16
print((x + 1) - x)
```

Students can also investigate when

```python
2.0**n + 1 == 2.0**n
```

becomes true.

---

# 2. Exact Arithmetic: `int` and `fractions.Fraction`

Python integers have arbitrary size:

```python
n = 10**1000
```

so integer arithmetic is exact unless memory is exhausted.

For rational arithmetic, use:

```python
from fractions import Fraction

x = Fraction(1, 10)
y = Fraction(1, 3)

print(x + y)
```

This provides exact rational arithmetic.

It is useful for showing the difference between:

```python
0.1
```

as a binary floating-point number and

```python
Fraction(1, 10)
```

as the exact rational number

$$
\frac{1}{10}.
$$

This supports an important distinction:

> Exact arithmetic is possible for some algebraic objects, but it does not replace validated numerical methods for general functions.

---

# 3. Arbitrary-Precision Decimal Arithmetic: `decimal.Decimal`

Python's standard library provides arbitrary-precision decimal floating point through:

```python
from decimal import Decimal, getcontext

getcontext().prec = 80

x = Decimal(1) / Decimal(7)
print(x)
```

Important capabilities:

- user-selected precision;
- explicit rounding modes;
- decimal representation;
- arithmetic suitable for controlled rounding experiments.

This is useful for teaching:

- arbitrary precision;
- the difference between precision and correctness;
- rounding modes;
- why simply increasing precision does not automatically produce a proof.

A key lesson is:

> Arbitrary precision can make a numerical approximation more accurate, but it does not by itself provide a rigorous enclosure.

---

# 4. Arbitrary-Precision Binary Floating Point: `gmpy2`

For binary arbitrary-precision arithmetic, use:

```bash
pip install gmpy2
```

and:

```python
import gmpy2

x = gmpy2.mpfr("0.1")
print(x)
```

`gmpy2` wraps GMP, MPFR, and MPC.

The most important type for this course is:

```python
gmpy2.mpfr
```

which provides correctly rounded arbitrary-precision binary floating-point arithmetic.

The precision can be changed:

```python
ctx = gmpy2.get_context()
ctx.precision = 200
```

and directed rounding can be selected, for example toward minus infinity or plus infinity.

Conceptually, this permits rigorous endpoint interval operations such as:

$$
\underline{x+y}
=
\operatorname{round}_{-\infty}
(\underline{x}+\underline{y}),
$$

and

$$
\overline{x+y}
=
\operatorname{round}_{+\infty}
(\overline{x}+\overline{y}).
$$

This makes `gmpy2` particularly useful when teaching how a genuine interval implementation works.

---

# 5. Important Input Subtlety

Students should explicitly study the difference between:

```python
gmpy2.mpfr(0.1)
```

and

```python
gmpy2.mpfr("0.1")
```

The first begins from the already-rounded Python binary64 value representing `0.1`.

The second parses the decimal string directly at the chosen MPFR precision.

This illustrates an important general rule:

> Increasing precision after a value has already been rounded does not recover the information that was lost.

The same phenomenon appears in other arbitrary-precision and interval libraries.

---

# 6. Student-Built Endpoint Interval Arithmetic

Before using a serious interval library, students should implement a minimal class such as:

```python
class Interval:
    def __init__(self, lo, hi):
        assert lo <= hi
        self.lo = lo
        self.hi = hi

    def __add__(self, other):
        ...

    def __sub__(self, other):
        ...

    def __mul__(self, other):
        ...

    def __truediv__(self, other):
        ...
```

Initially define the mathematical operations.

For example:

$$
[a,b]+[c,d]
=
[a+c,b+d].
$$

For multiplication:

$$
[a,b][c,d]
=
[
\min(ac,ad,bc,bd),
\max(ac,ad,bc,bd)
].
$$

Students should understand intervals as sets:

$$
X=[\underline{x},\overline{x}]
=
\{x\in\mathbb R:\underline{x}\le x\le \overline{x}\}.
$$

The central inclusion property is:

$$
x\in X,\qquad y\in Y
\quad\Longrightarrow\quad
x\circ y\in X\circ Y.
$$

---

# 7. Why Naive Floating-Point Endpoints Are Not Enough

A naive implementation such as:

```python
def __add__(self, other):
    return Interval(
        self.lo + other.lo,
        self.hi + other.hi
    )
```

is mathematically suggestive but not automatically rigorous if the endpoints are stored as ordinary Python floats.

Because each endpoint operation is rounded, one may accidentally round:

- the lower bound upward;
- the upper bound downward.

Then the true result may lie outside the computed interval.

This motivates **outward rounding**.

For every operation:

- lower bounds must be rounded toward

$$
-\infty;
$$

- upper bounds must be rounded toward

$$
+\infty.
$$

For teaching purposes, `gmpy2` is well suited to implementing this correctly.

---

# 8. A Simple Binary64 Teaching Implementation

For a very small teaching implementation, one can sometimes enlarge a computed binary64 endpoint using:

```python
math.nextafter
```

toward:

```python
-math.inf
```

or

```python
math.inf
```

This can help explain outward rounding.

However, this should be restricted to carefully controlled examples and basic arithmetic.

Rigorous implementations of:

- `sin`,
- `cos`,
- `exp`,
- `log`,
- special functions,

are more subtle.

Students should therefore not attempt to implement a complete rigorous elementary-function library themselves.

---

# 9. Serious Rigorous Computing: `python-flint`

The course should eventually move to:

```bash
pip install python-flint
```

`python-flint` provides Python access to FLINT and Arb.

For validated numerics, the key type is:

```python
flint.arb
```

Example:

```python
from flint import arb, ctx

ctx.dps = 50

x = arb(1) / arb(3)
print(x)
```

Arb represents a real number using **ball arithmetic**:

$$
m\pm r.
$$

This means the exact value is known to lie in:

$$
[m-r,m+r].
$$

All operations propagate rigorous error bounds.

This makes Arb suitable for:

- rigorous elementary functions;
- arbitrary-precision validated arithmetic;
- root-finding algorithms;
- nonlinear systems;
- global optimization;
- verified numerical integration;
- rigorous special-function evaluation.

---

# 10. Endpoint Intervals Versus Balls

Students should first learn traditional endpoint intervals:

$$
X=[a,b].
$$

Later, introduce the equivalent midpoint-radius representation:

$$
X=m\pm r,
$$

where

$$
m=\frac{a+b}{2},
$$

and

$$
r=\frac{b-a}{2}.
$$

Thus:

$$
[a,b]
\quad\longleftrightarrow\quad
m\pm r.
$$

This illustrates an important conceptual point:

> Interval arithmetic is fundamentally about rigorous set enclosures, not about one particular data structure.

Endpoint intervals are especially intuitive for teaching.

Ball arithmetic is especially effective for arbitrary-precision computation.

---

# 11. Input Conversion Is Again Important in Arb

Students should compare:

```python
arb(0.1)
```

with:

```python
arb("0.1")
```

The first starts from the binary64 approximation represented by the Python float.

The second parses the intended decimal number directly.

This is an excellent lecture/lab example because it reinforces the distinction between:

- an exact mathematical value;
- a floating-point approximation to that value;
- a rigorous enclosure containing a value.

---

# 12. `mpmath`

`mpmath` is useful for arbitrary-precision exploratory computation:

```python
from mpmath import mp

mp.dps = 100

print(mp.pi)
```

It also has an interval module:

```python
from mpmath import iv

x = iv.mpf([1, 2])
print(iv.sin(x))
```

However, it should probably **not** be the main rigorous validation engine for the course.

A reasonable role is:

- use `mpmath` for arbitrary-precision demonstrations;
- perhaps show `mpmath.iv` briefly;
- use `python-flint` for serious validated computation.

The course should avoid creating the impression that every function provided by an arbitrary-precision numerical library automatically gives a rigorous certificate.

---

# 13. SageMath as an Optional Alternative

SageMath provides very mature interval and ball arithmetic.

Examples include:

```python
RIF = RealIntervalField(100)
x = RIF(1, 2)
```

and ball arithmetic through `RealBallField`.

This is technically powerful, but Sage is a much larger environment.

For a Master's CS audience, a standard Python environment is likely simpler and more familiar.

Therefore:

- Sage may be mentioned;
- perhaps one optional demonstration can use it;
- it need not be a course requirement.

---

# 14. Recommended Course Software Progression

A possible lecture/software mapping is:

| Lectures | Main software |
|---|---|
| 1–3 | Python `float`, `math`, NumPy |
| 2–3 | `Fraction`, `Decimal`, optionally `mpmath` |
| 4 | student-written `Interval` class |
| 5 | student interval class + `gmpy2` directed rounding |
| 6–7 | student interval algorithms + `python-flint` comparison |
| 8 | simple student-built forward-mode automatic differentiation |
| 9 | student implementation of interval Newton |
| 10 | student implementation of Krawczyk / interval Newton for systems |
| 11 | student implementation of interval branch-and-bound |
| 12–14 | serious experiments and capstones using `python-flint` |

The arithmetic library should be trusted.

The **validated algorithms should still be written by the students**.

For example:

```python
def interval_newton(f, df, X):
    ...
```

and:

```python
def branch_and_bound(f, domain):
    ...
```

The point is that students learn:

- why the algorithm is correct;
- which enclosure property it uses;
- what the final certificate means.

---

# 15. Recommended Minimal Installation

A compact environment could be:

```bash
pip install numpy matplotlib gmpy2 python-flint
```

Optionally:

```bash
pip install jupyter mpmath
```

This gives:

- `numpy`: conventional numerical computing;
- `matplotlib`: visualization;
- `gmpy2`: MPFR arbitrary-precision arithmetic and directed rounding;
- `python-flint`: serious rigorous ball arithmetic;
- `mpmath`: convenient arbitrary-precision experimentation;
- Jupyter: notebook-based lectures and labs.

---

# 16. Recommended Conceptual Tower

The course can explicitly use the following hierarchy:

```text
Python float
    ↓
understand IEEE 754 and numerical error
    ↓
Fraction / Decimal
    ↓
understand exact and arbitrary-precision arithmetic
    ↓
gmpy2.mpfr
    ↓
understand arbitrary-precision binary arithmetic and directed rounding
    ↓
student-written endpoint intervals
    ↓
understand inclusion and outward rounding
    ↓
python-flint / Arb
    ↓
trusted rigorous arithmetic
    ↓
student-written validated algorithms
    ↓
rigorous computational certificates
```

In mathematical shorthand:

$$
\boxed{
\texttt{float}
\to
\texttt{Fraction/Decimal}
\to
\texttt{MPFR}
\to
\text{intervals}
\to
\text{Arb}
\to
\text{validated algorithms}
}
$$

---

# 17. Main Pedagogical Principle

Do not hide interval arithmetic behind a library from the beginning.

A better sequence is:

1. students see floating-point failures;
2. they implement mathematical interval operations;
3. they discover that naive floating-point endpoints are not rigorous;
4. they learn outward rounding;
5. they use MPFR to understand directed rounding;
6. they move to Arb for robust arithmetic;
7. they implement actual validated algorithms themselves.

This lets the course culminate naturally with `python-flint` while preserving understanding of what the library is guaranteeing.

---

# Suggested Final Position

For this course, a Python-first stack is recommended.

The simplest overall choice is:

```text
Python
+ NumPy
+ Decimal / Fraction
+ gmpy2
+ python-flint
```

with Jupyter notebooks for teaching and labs.

The final validated-computing environment should rely primarily on **python-flint / Arb**, while the earlier part of the course should deliberately expose the details of floating-point and endpoint interval arithmetic so that students understand what rigorous numerical software is doing for them.
