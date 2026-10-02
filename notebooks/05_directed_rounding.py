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
# # 05 · Machine intervals and outward rounding
#
# **Time:** 100–120 minutes. **Prerequisites:** Lectures 02 and 04.
# **Lab:** [Outward rounding](../labs/lab05_directed_rounding.ipynb).
#
# Objectives: expose an enclosure failure from ordinary rounding, round inputs and
# operations outward, manage precision locally, and compare endpoint intervals with
# Arb balls. Rational arithmetic remains our exact oracle for selected checks.

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
import gmpy2
from flint import arb, ctx
from vc.intervals import RationalInterval as Interval
from vc.mpfr_intervals import MPFRInterval, mpfr_fraction
from vc.arb_bridge import to_ball, from_ball

# %% [markdown]
# ## EXPERIMENT · An incorrect point interval
#
# Take the exact stored binary values of 0.1 and 0.3 as inputs. This isolates
# arithmetic rounding from decimal input error. The nearest-rounded sum is not
# their exact rational sum; treating it as both interval endpoints loses inclusion.

# %%
exact_x = Fraction.from_float(0.1)
exact_y = Fraction.from_float(0.3)
exact_sum = exact_x + exact_y
rounded_sum = Fraction.from_float(0.1 + 0.3)
naive_interval = Interval(rounded_sum)
print("Exact sum:", exact_sum)
print("Rounded singleton:", naive_interval)
print("Enclosed?", naive_interval.contains(exact_sum))
assert not naive_interval.contains(exact_sum)

# %% [markdown]
# ## THEORY · One-sided error is the required contract
#
# Let down(z) and up(z) be correctly directed roundings. Their defining properties
# are $\operatorname{down}(z)\leq z\leq\operatorname{up}(z)$. Thus, for addition,
#
# $$[a,b]+[c,d]\subseteq[\operatorname{down}(a+c),\operatorname{up}(b+d)].$$
#
# **Proof.** The exact result lies between a+c and b+d by Lecture 04. Directed
# rounding moves the lower bound down and the upper bound up, so containment
# is preserved. Apply the same argument to each endpoint formula.
#
# For multiplication, compute **every lower candidate downward** before taking
# the minimum, and **every upper candidate upward** before taking the maximum.
# Rounding only the already-computed nearest-rounded products is not the MPFR
# procedure we are proving here.

# %%
precision = 24
with gmpy2.context(precision=precision, round=gmpy2.RoundDown):
    lower = gmpy2.mpfr(1) / gmpy2.mpfr(10)
with gmpy2.context(precision=precision, round=gmpy2.RoundUp):
    upper = gmpy2.mpfr(1) / gmpy2.mpfr(10)

assert mpfr_fraction(lower) <= Fraction(1, 10) <= mpfr_fraction(upper)
print("Exact lower endpoint:", mpfr_fraction(lower))
print("Exact upper endpoint:", mpfr_fraction(upper))

# %% [markdown]
# ## THEORY · Inputs must be enclosed too
#
# Parsing a decimal string once with nearest rounding produces an approximation
# to its intended rational. Making both endpoints equal to that approximation
# does not enclose the original input. Parse downward for the lower endpoint and
# upward for the upper endpoint, or convert the exact rational in both directions.
#
# Our constructor uses exact rational parsing before MPFR conversion. The two
# operations have different jobs: identify the mathematical input, then enclose it.

# %%
X = MPFRInterval("0.1", precision=24)
print("Enclosure of the intended tenth:", X.exact_bounds())
assert X.contains(Fraction(1, 10))

with gmpy2.context(precision=100):
    from_float = gmpy2.mpfr(0.1)
    from_string = gmpy2.mpfr("0.1")
print("Exact value imported from float:", mpfr_fraction(from_float))
print("String parsing is still rounded:", mpfr_fraction(from_string) != Fraction(1, 10))

# %% [markdown]
# ## EXPERIMENT · Read the actual addition method
#
# The two contexts are intentionally written separately. At each arithmetic line
# we can see which direction is active. Constructing the result from these finite
# MPFR endpoints preserves their exact stored values at the same precision.

# %%
import inspect
print(inspect.getsource(MPFRInterval.__add__))

X = MPFRInterval(exact_x, precision=53)
Y = MPFRInterval(exact_y, precision=53)
result = X + Y
assert result.contains(exact_sum)
print("Repaired enclosure:", result.exact_bounds())

# %% [markdown]
# **EXERCISE (10 minutes):** use the subtraction formula to decide which endpoints
# and rounding modes are needed. Why does a downward-rounded lower product not
# necessarily come from the same corner as the upward-rounded upper product?

# %% [markdown]
# ## EXPERIMENT · Precision is not input certainty
#
# A point input like 1/3 needs a small rounding enclosure. More precision shrinks
# that enclosure. The measured interval [1,2] already has width one; more bits
# cannot legitimately erase its specified uncertainty.

# %%
for bits in [16, 32, 80, 160]:
    point = MPFRInterval("1/3", precision=bits)
    measurement = MPFRInterval(1, 2, precision=bits)
    print(bits, "bits: width around 1/3 ≈", float(point.width()),
          "; measurement width =", measurement.width())

# %% [markdown]
# Scoped contexts restore the previous settings, including after an exception.
# The teaching class rejects mixed-precision operands so a precision change is an
# explicit decision. Recompute from the exact original input to refine its enclosure;
# merely copying wide old endpoints at more bits does not recover information.

# %%
before = gmpy2.get_context().precision
try:
    with gmpy2.context(precision=137):
        raise RuntimeError("A simulated failed experiment")
except RuntimeError:
    pass
assert gmpy2.get_context().precision == before
print("Original MPFR precision restored:", before)

# %% [markdown]
# ## THEORY · Balls and endpoint intervals
#
# A ball $m\pm r$ represents [m−r,m+r]. Over exact reals, m=(a+b)/2 and
# r=(b−a)/2 convert an endpoint interval to a ball. On a machine, both the midpoint
# calculation and radius rounding require care. An incorrectly rounded radius
# can shrink the set even if m looks accurate.
#
# We use Arb's enclosing union of endpoint balls to build a safe input ball. The
# conversion may widen the interval. It is an inclusion-preserving bridge, not a
# promise that two representations will have identical endpoints.

# %%
domain = Interval("0.1", "0.3")
with ctx.workprec(100):
    ball = to_ball(domain)
    recovered = from_ball(ball)
    third = from_ball(arb(1) / arb(3))
print("Original endpoints:", domain)
print("Ball display:", ball)
assert domain.is_subset_of(recovered)
assert third.contains(Fraction(1, 3))
print("Exact containment checks passed.")

# %% [markdown]
# `from_ball` extracts the exact dyadic midpoint and radius and forms rational
# endpoints. It avoids conversion through Python float or a rounded display string.
# A failed comparison after implicit conversion is not automatically proof of
# noncontainment; know whether a predicate is comparing points or enclosing balls.
#
# **Implementation boundary:** [the MPFR class](../vc/mpfr_intervals.py) handles
# bounded intervals and basic arithmetic, rejecting division through zero and
# nonfinite results. It is a small teaching kernel, not a complete interval standard.
# Arb supplies elementary functions in the next lecture. Do not replace those with
# endpoint calls to `math.sin`, `math.exp`, or an assumed one-ulp adjustment.
#
# **Exit ticket:** list three places inclusion can be lost: input conversion,
# arithmetic, and output conversion. Explain why random containment tests alone
# cannot establish all-input correctness.
#
# **Reading:** Tucker §2.4 (Floating Point Interval Arithmetic), pp. 37–45,
# especially §2.4.2 on changing rounding modes;
# [gmpy2 contexts](https://gmpy2.readthedocs.io/en/stable/contexts.html).
# Next: [Lecture 06](06_dependency.ipynb).
