# ---
# jupyter:
#   course:
#     kind: lecture
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
# # 12 · Geometry that makes reliable decisions
#
# **Time:** 90–110 minutes. **Preparation:** interval arithmetic, Arb, determinants. **Lab:** [An orientation filter](../labs/lab12_robust_geometry.ipynb).
#
# Objectives: turn a determinant enclosure into a geometric decision, escalate precision when useful, and fall back to exact arithmetic for exact inputs. This is the final core programming lab; allow time to discuss capstones.

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
    working_folder = Path("/content/validated-course") / 'notebooks'
    working_folder.mkdir(parents=True, exist_ok=True)
    os.chdir(working_folder)
    print("Course helpers ready:", vc.__version__)


# %%
from fractions import Fraction
import matplotlib.pyplot as plt
from IPython.display import display
from vc.intervals import RationalInterval as Interval
from vc.geometry import determinant, orientation, orientation_bound, sign_of_interval

# %% [markdown]
# ## THEORY · Orientation is a sign question
#
# For points A, B, C in the plane, define
#
# $$D=(B_x-A_x)(C_y-A_y)-(B_y-A_y)(C_x-A_x).$$
#
# If D>0, C lies to the left of the directed line from A to B; if D<0, it lies to the right. If D=0, the points are collinear, including degenerate cases where points coincide. D is twice the signed area of the triangle. Swapping B and C reverses its sign.
#
# A geometric algorithm may use this sign to choose a branch. A small arithmetic error near zero can therefore change its combinatorial decision, not just the last digit of a coordinate.

# %%
A, B, C_point = (0, 0), (2, 0), (1, 1)
print("Determinant:", determinant(A, B, C_point))
fig, ax = plt.subplots(figsize = (5, 3))
ax.plot([0, 2, 1, 0], [0, 0, 1, 0], "o-")
for name, point in [("A", A), ("B", B), ("C", C_point)]:
    ax.annotate(name, point, xytext = (5, 5), textcoords = "offset points")
ax.set(xlabel = "x", ylabel = "y", title = "Positive orientation")
ax.set_aspect("equal")
display(fig)
plt.close(fig)

# %% [markdown]
# ## EXPERIMENT · Exactly represented inputs, wrong zero
#
# Let n=2²⁷ and use A=(0,0), B=(n,n−1), C=(n+1,n). Every input coordinate is exactly representable in binary64. The exact determinant is n²−(n−1)(n+1)=1, but the two products round to the same binary64 value. This failure is arithmetic cancellation, without any input-conversion ambiguity.

# %%
n = 2 ** 27
points = ((0, 0), (n, n - 1), (n + 1, n))
float_points = [tuple(float(value) for value in point) for point in points]
naive = determinant(*float_points)
exact = determinant(*points)
print("Float determinant:", naive)
print("Exact determinant:", exact)
assert naive == 0 and exact == 1

# %% [markdown]
# ## THEORY · A filter answers only when its bound decides
#
# Construct enclosing balls for all exact coordinates, evaluate the determinant through Arb, and convert its result to exact rational endpoints. A strictly positive or negative enclosure proves the corresponding sign. The exact singleton [0,0] proves zero. Every other zero-containing bound is inconclusive.
#
# **Proof:** the determinant of the stated points belongs to the computed enclosure by compositional inclusion. An interval entirely on one side of zero determines its sign. Containing zero does not make the true value zero.
#
# If the first bound is inconclusive, repeat from the exact input at a higher precision. If the configured list is exhausted, evaluate the determinant with `Fraction`. For finite exact rational inputs this supplies its exact sign, including collinearity. It is a fallback for a specified exact problem.

# %%
result = orientation(*points)
for precision, bound in result.attempts:
    print(precision, "bits:", bound)
print("Decision:", result.sign, "method:", result.method)
assert result.sign == 1

fallback = orientation(*points, precisions = (24,))
print("Short precision budget:", fallback.method, fallback.exact_determinant)
assert fallback.method == "fraction" and fallback.exact_determinant == 1
collinear = orientation((0, 0), ("1/3", "2/3"), ("2/3", "4/3"))
print("Collinear case:", collinear.sign, collinear.method)
assert collinear.sign == 0

# %% [markdown]
# Read [vc/geometry.py](../vc/geometry.py). The filter keeps its attempted precisions and bounds in the result. It rejects implicit float input: use exact decimal strings for intended decimals, or explicitly convert a stored binary float with `Fraction.from_float` when that is the chosen input semantics.
#
# **CHECKPOINT (10 minutes):** why is an arbitrary tolerance such as “abs(D)<10⁻¹⁰ means collinear” not a reliable exact orientation predicate? What happens under coordinate rescaling?

# %% [markdown]
# ## Failure of a proposed repair · Measurements remain uncertain
#
# Suppose A=(0,0), B=(1,1), and C has x=2 but y in [1.999,2.001]. Both clockwise and counterclockwise triples are physically allowed. No number of arithmetic digits can certify one uniform sign for this entire family.
#
# Use `orientation_bound` for interval coordinates and report its sign test. Do not replace measured intervals by their midpoints and call the exact fallback: that changes the problem.

# %%
a = (Interval(0), Interval(0))
b = (Interval(1), Interval(1))
c = (Interval(2), Interval("1.999", "2.001"))
for precision in [24, 100, 200]:
    bound = orientation_bound(a, b, c, precision)
    print(precision, bound, "sign:", sign_of_interval(bound))
    assert bound.lo < 0 < bound.hi
print("Allowed negative determinant:", determinant((0, 0), (1, 1), (2, Fraction("1.999"))))
print("Allowed positive determinant:", determinant((0, 0), (1, 1), (2, Fraction("2.001"))))

# %% [markdown]
# ## Application scope and capstone bridge
#
# A correct orientation predicate supports reliable decisions in geometry algorithms, but it does not prove an entire triangulation or collision simulator correct. Coverage, degeneracies, and other branch conditions need their own arguments.
#
# The [mirror project](../projects/mirror_trajectory.ipynb) uses the same discipline for a more involved decision: which circle is hit first? Its reflection formula alone is insufficient without certified collision ordering.
#
# **Reading:** J. R. Shewchuk's [robust predicates introduction and papers](https://www.cs.cmu.edu/~quake/robust.html) explain the role of determinant signs and adaptive exact predicates in computational geometry. Our teaching filter uses Arb and rational fallback; it does not implement Shewchuk's expansion arithmetic.
#
# **Exit ticket:** distinguish exact collinearity, a zero-containing arithmetic bound, and a family of uncertain inputs allowing several orientations. Next: [certificate audit](13_certificate_audit.ipynb).
