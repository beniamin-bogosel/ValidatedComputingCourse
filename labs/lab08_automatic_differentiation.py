# ---
# jupyter:
#   course:
#     kind: student_lab
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
# # Lab 08 · Propagate derivatives explicitly
#
# **Preparation:** [Lecture 08](../notebooks/08_automatic_differentiation.ipynb).
#
# **Time:** about 2 hours. Implement a small scalar dual class and use two forward passes to enclose a Jacobian. The constructor and simple arithmetic are supplied.

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
    working_folder = Path("/content/validated-course") / 'labs'
    working_folder.mkdir(parents=True, exist_ok=True)
    os.chdir(working_folder)
    print("Course helpers ready:", vc.__version__)


# %%
from fractions import Fraction
from flint import arb, ctx
from vc.intervals import RationalInterval as Interval
from vc.arb_bridge import to_ball, from_ball
from vc.autodiff import Dual


# %% [markdown]
# ## Task A · Product and reciprocal rules (45 minutes)
#
# Complete the two missing methods. Use exact fractions for the first checks and intervals for the second. This student type needs only the displayed arithmetic operations; elementary functions are explored with the reviewed type in Task C.

# %% tags=["exercise"]
class StudentDual:
    def __init__(self, value, derivative):
        self.value = value
        self.derivative = derivative

    def _operand(self, other):
        if isinstance(other, StudentDual):
            return other
        return StudentDual(other, self.derivative * 0)

    def __add__(self, other):
        other = self._operand(other)
        return StudentDual(self.value + other.value, self.derivative + other.derivative)

    def __radd__(self, other):
        return self + other

    def __neg__(self):
        return StudentDual(-self.value, -self.derivative)

    def __sub__(self, other):
        return self + (-self._operand(other))

    def __rsub__(self, other):
        return self._operand(other) - self

    def __mul__(self, other):
        raise NotImplementedError("Apply the product rule with named intermediate terms")

    def __rmul__(self, other):
        return self * other

    def reciprocal(self):
        raise NotImplementedError("Differentiate the reciprocal")

    def __truediv__(self, other):
        return self * self._operand(other).reciprocal()


# %% tags=["exercise"]
def polynomial(x):
    return (x+2)*(x-1)*(x-3)

for value in [Fraction(-2), Fraction(1, 3), Fraction(4)]:
    x = StudentDual(value, Fraction(1))
    result = polynomial(x)
    assert result.value == value**3 - 2*value**2 - 5*value + 6
    assert result.derivative == 3*value**2 - 4*value - 5
    quotient = (x+3)/(x+4)
    assert quotient.derivative == 1/(value+4)**2

X = Interval(1, 2)
result = polynomial(StudentDual(X, Interval(1)))
for value in [X.lo, X.midpoint(), X.hi]:
    assert result.derivative.contains(3*value*value - 4*value - 5)
print("Derivative enclosure:", result.derivative)


# %% [markdown]
# **Written response:** Give an induction argument for derivative propagation. Which extra premise is needed to turn these rules into interval derivative enclosures?

# %% [markdown]
# ## Task B · Two Jacobian columns (40 minutes)
#
# Complete the seeds and output assembly for the supplied system. Use your `StudentDual` class. Rows index output equations and columns index input variables.

# %% tags=["exercise"]
def system(x, y):
    return [x*x + x*y, x-y]

def student_jacobian(box):
    x, y = box
    raise NotImplementedError("Run once with tangents (1,0), once with (0,1)")


# %% tags=["exercise"]
box = [Interval(1, 2), Interval(3, 4)]
matrix = student_jacobian(box)
for row in matrix:
    print(row)
# Analytic Jacobian: [[2*x+y, x], [1, -1]].
expected_ranges = [[Interval(5, 8), Interval(1, 2)], [Interval(1), Interval(-1)]]
for row in range(2):
    for column in range(2):
        assert expected_ranges[row][column].is_subset_of(matrix[row][column])

# %% [markdown]
# **Written response:** Why do the two passes produce columns rather than rows? What would be wrong with seeding both variables with tangent 1 and calling the result a Jacobian?

# %% [markdown]
# ## Task C · Arb and finite differences (30 minutes)
#
# Run the supplied Arb experiment, then compare point AD with forward differences. The exact reference derivative of x³−2x at 1 is 1.

# %% tags=["exercise"]
with ctx.workprec(100):
    x = Dual(to_ball(Interval("-1/4", "1/4")), arb(1))
    result = x.exp() * x.sin()
    derivative_bound = from_ball(result.derivative)
assert derivative_bound.contains(1)
print("Interval derivative:", derivative_bound)

def cubic_expression(x):
    return x*x*x - 2*x

ad_result = cubic_expression(StudentDual(Fraction(1), Fraction(1)))
print("Exact rational AD derivative:", ad_result.derivative)
for exponent in [2, 5, 8, 11, 14, 16]:
    h = 10.0**(-exponent)
    estimate = (cubic_expression(1.0+h) - cubic_expression(1.0))/h
    print(exponent, estimate, abs(estimate-1))

# %% [markdown]
# **Written response:** Distinguish truncation error, arithmetic error, and dependency overestimation. Explain why branching at the midpoint is not a derivative proof for an interval crossing a branch boundary.

# %% [markdown]
# ## Submission
#
# Complete the code and written responses. Restart the kernel and run every cell. State the mathematical assumptions for each guarantee; retain failed or inconclusive examples and explain them.
