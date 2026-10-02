# ---
# jupyter:
#   course:
#     kind: instructor_solution
#   jupytext:
#     cell_metadata_filter: tags
#     formats: ipynb,py:percent
#     notebook_metadata_filter: kernelspec,jupytext,course
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python (Validated Computing)
#     language: python
#     name: validated-computing
# ---

# %% [markdown]
# # Lab 04 · Instructor solution
#
# Build a small interval class using exact rational endpoints. The point is to justify the formulas before considering rounding. Do not import the reference interval class for Task A.

# %% [markdown] tags=["colab-setup"]
# ## Google Colab setup — run this cell first
#
# **Local Jupyter:** this cell skips Colab setup; use your installed course environment.
#
# Use a **CPU Python runtime** (Python 3.12 or newer). Run the next cell and select
# **vc_runtime.zip** from this edition when prompted. It loads the course helpers
# and installs the arithmetic libraries. Repeat setup whenever you get a new runtime.
# No Drive mounting or local Python installation is required.
# Use this setup instead of the local installation and kernel-selection instructions
# in the original course text.
#
# Save a copy of this notebook in Drive, or download it after editing. Files created
# by the project are under `/content/validated-course/build/certificates/`; download
# those separately from Colab's Files panel. Runtime files are temporary.
#
# Open other course notebooks using **File → Upload notebook**, choosing them from
# the extracted course folder. Relative course links are intended for local Jupyter
# and do not open sibling notebooks automatically in Colab. In labs, complete exercise
# cells before running their diagnostics: `NotImplementedError` marks an unfinished task.
#

# %% tags=["colab-setup"]
try:
    import google.colab
except ImportError:
    print("Local Jupyter: using the installed course environment.")
else:
    import hashlib
    from pathlib import Path
    import subprocess
    import sys
    from google.colab import files

    if sys.version_info < (3, 12):
        raise RuntimeError("This course needs a Python 3.12 or newer Colab runtime.")

    # Upload the small companion file supplied with the Colab course edition.
    expected_hash = '833652c4a440f1c3a22bc6e68c59d533b41e6f9f1ff0b4af226f8fbee2244c1a'
    runtime_zip = Path("/content") / ("vc-course-" + expected_hash + ".zip")
    if not runtime_zip.exists():
        print("Select vc_runtime.zip from the extracted Colab course folder.")
        uploaded = files.upload()
        if len(uploaded) != 1:
            raise ValueError("Upload only vc_runtime.zip, then run this cell again.")
        archive_bytes = next(iter(uploaded.values()))
        if hashlib.sha256(archive_bytes).hexdigest() != expected_hash:
            raise ValueError("Wrong vc_runtime.zip: use the one supplied with this notebook.")
        runtime_zip.write_bytes(archive_bytes)

    if hashlib.sha256(runtime_zip.read_bytes()).hexdigest() != expected_hash:
        raise ValueError("The cached vc archive has changed; start a fresh runtime.")

    # Keep Colab's existing NumPy and plotting stack when they satisfy these bounds.
    # Install MPFR/Arb bindings, not the full local Jupyter environment.
    subprocess.check_call([
        sys.executable, "-m", "pip", "install", "--quiet",
        'numpy>=1.26', 'matplotlib>=3.8', 'gmpy2==2.3.1', 'python-flint==0.9.0', 'jupytext>=1.16'
    ])
    import gmpy2
    import flint
    if gmpy2.version() != "2.3.1" or flint.__version__ != "0.9.0":
        raise RuntimeError("Old arithmetic libraries are still loaded. Restart the session and run setup first.")

    if str(runtime_zip) not in sys.path:
        sys.path.insert(0, str(runtime_zip))

    import vc
    if not vc.__file__.startswith(str(runtime_zip) + "/"):
        raise RuntimeError("Another vc copy is already loaded. Start a fresh runtime.")

    # Preserve the relative output paths used by the project notebooks.
    import os
    working_folder = Path("/content/validated-course") / 'solutions'
    working_folder.mkdir(parents=True, exist_ok=True)
    os.chdir(working_folder)
    print("Course helpers ready:", vc.__version__)


# %%
from fractions import Fraction

# Strings describe intended decimal values exactly.
assert Fraction("0.1") == Fraction(1, 10)


# %% [markdown]
# ## Task A · Four endpoint products (45 minutes)
#
# Complete multiplication, reciprocal, and square below. Accept only `StudentInterval` operands for multiplication. Reject reciprocals of intervals containing zero. The square should give the exact range of $x^2$ on the input interval, including intervals crossing zero.

# %%
class StudentInterval:
    def __init__(self, lo, hi=None):
        if hi is None:
            hi = lo
        if isinstance(lo, float) or isinstance(hi, float):
            raise TypeError("Use integers, fractions, or decimal strings")
        self.lo = Fraction(lo)
        self.hi = Fraction(hi)
        if self.lo > self.hi:
            raise ValueError("Endpoints are reversed")

    def __repr__(self):
        return f"[{self.lo}, {self.hi}]"

    def __add__(self, other):
        return StudentInterval(self.lo + other.lo, self.hi + other.hi)

    def __sub__(self, other):
        return StudentInterval(self.lo - other.hi, self.hi - other.lo)

    def __mul__(self, other):
        products = [self.lo * other.lo, self.lo * other.hi,
                    self.hi * other.lo, self.hi * other.hi]
        return StudentInterval(min(products), max(products))

    def reciprocal(self):
        if self.lo <= 0 <= self.hi:
            raise ZeroDivisionError("The interval contains zero")
        return StudentInterval(1 / self.hi, 1 / self.lo)

    def square(self):
        if self.lo >= 0:
            return StudentInterval(self.lo**2, self.hi**2)
        if self.hi <= 0:
            return StudentInterval(self.hi**2, self.lo**2)
        upper = max(self.lo**2, self.hi**2)
        return StudentInterval(0, upper)


# %%
def check_endpoints(interval, lo, hi):
    assert interval.lo == Fraction(lo)
    assert interval.hi == Fraction(hi)

for lo, hi in [(-3, -1), (-2, 3), (0, 0), (1, 4)]:
    X = StudentInterval(lo, hi)
    for left, right in [(-4, -2), (-1, 2), (0, 0), (2, 5)]:
        Y = StudentInterval(left, right)
        product = X * Y
        for x in [X.lo, (X.lo + X.hi)/2, X.hi]:
            for y in [Y.lo, (Y.lo + Y.hi)/2, Y.hi]:
                assert product.lo <= x*y <= product.hi
check_endpoints(StudentInterval(-3, -1).reciprocal(), -1, Fraction(-1, 3))
check_endpoints(StudentInterval(2, 4).reciprocal(), Fraction(1, 4), Fraction(1, 2))
check_endpoints(StudentInterval(-2, 3).square(), 0, 9)
check_endpoints(StudentInterval(-3, -1).square(), 1, 9)
check_endpoints(StudentInterval(2, 4).square(), 4, 16)
try:
    StudentInterval(-1, 1).reciprocal()
except ZeroDivisionError:
    print("Expected rejection: denominator includes zero")
else:
    raise AssertionError("Division through zero must be rejected")

# %% [markdown]
# **Worked explanation:** For fixed $y$, a linear function of $x$ reaches both extrema at endpoints; applying the same argument in $y$ reduces the extrema to four corners. Sampling can catch errors but cannot replace this argument. Reciprocal reverses order on each component of its domain; zero must be excluded.

# %% [markdown]
# ## Task B · Interpret a certificate (35 minutes)
#
# Use your class to bound the area of a rectangle with side lengths in [2.9, 3.1] and [4.8, 5.2], and evaluate $x+1/x$ on [2, 3].

# %%
length = StudentInterval("2.9", "3.1")
width = StudentInterval("4.8", "5.2")
area = length * width
X = StudentInterval(2, 3)
value = X + X.reciprocal()
print("Area:", area)
print("x + 1/x:", value)

# %%
check_endpoints(area, "13.92", "16.12")
check_endpoints(value, Fraction(7, 3), Fraction(7, 2))

# %% [markdown]
# **Worked explanation:** The area interval is the exact range if every pair of side lengths in the rectangle of admissible data is allowed. For $x+1/x$, the result [7/3, 7/2] is an enclosure, while monotonicity gives the tighter true range [5/2, 10/3]. Interval addition loses the relation between $x$ and $1/x$.

# %% [markdown]
# ## Task C · Set language and dependency (30 minutes)
#
# For X = [-2, 3], compute X − X, X * X, and X.square(). On paper, find the hull and intersection of [0, 2] and [1, 3], and the intersection of [0, 1] and [2, 3].

# %%
X = StudentInterval(-2, 3)
print("X - X:", X - X)
print("X * X:", X * X)
print("square(X):", X.square())

# %% [markdown]
# **Worked explanation:** X − X = [−5, 5] and X * X = [−6, 9] allow independent choices. The functions x − x and x² have ranges {0} and [0, 9]. The hull is [0, 3], the first intersection is [1, 2], and the disjoint intersection is empty. [0, 0] contains the real number zero, so it cannot represent the empty set.
