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
# # Lab 03 · Equivalent formulas, different answers
#
# **Time:** 2 hours plus 30–60 minutes homework. **Preparation:**
# [Lecture 03](../notebooks/03_stability.ipynb).
#
# Compare algorithms at the same inputs, quantify their error, and explain their
# limitations. Core tasks are polynomial evaluation and a quadratic reformulation;
# the summation case is a short supplied experiment.

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
import math
from fractions import Fraction
from decimal import Decimal, localcontext
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
from vc.environment import require_binary64

require_binary64()

def expanded(t):
    return t**6 - 6*t**5 + 15*t**4 - 20*t**3 + 15*t**2 - 6*t + 1

def factored(t):
    return (t - 1)**6

# %% [markdown]
# ## Task A · Audit the polynomial graph (40 minutes)
#
# Tucker's Example 1.6.2 compares the expanded polynomial above with $(t-1)^6$.
# Implement Horner evaluation. Then implement `exact_errors(t, method)`, returning
# `(absolute_error, relative_error)` as fractions. Define the reference to be the
# exact polynomial value at the **stored float** `t`. Return `None` for relative
# error when the reference is zero. Inputs and computed results are finite floats.

# %% tags=["exercise", "task-polynomial"]
def horner(t):
    raise NotImplementedError("Evaluate with Horner's rule")

def exact_errors(t, method):
    raise NotImplementedError("Compare the computed float with an exact rational reference")

# %% tags=["exercise", "check-polynomial"]
assert horner(Fraction(3, 2)) == Fraction(1, 64)
assert exact_errors(1.0, factored) == (Fraction(0), None)
assert exact_errors(1.0, lambda t: 1.0) == (Fraction(1), None)
for t in [0.999, 1.001, 1.01]:
    for name, method in [("expanded", expanded), ("Horner", horner), ("factored", factored)]:
        absolute, relative = exact_errors(t, method)
        assert absolute >= 0 and relative >= 0
        print(t, name, "abs≈", float(absolute), "rel≈", float(relative))

# %% tags=["exercise", "task-polynomial-plot"]
ts = np.linspace(0.995, 1.005, 401)
fig, ax = plt.subplots(figsize=(7, 3))
for name, method in [("expanded", expanded), ("Horner", horner), ("factored", factored)]:
    ax.plot(ts, [method(float(t)) for t in ts], label=name)
ax.set(xlabel="t", ylabel="computed p(t)")
ax.legend()
display(fig)
plt.close(fig)

# %% [markdown] tags=["answer-polynomial"]
# **Written answer:** explain the misleading signs or oscillations you observe.
# Distinguish evaluation error at the stored input from uncertainty in an intended
# input. Does a better formula change the condition number of the function?

# %% [markdown]
# ## Task B · Recover the smaller quadratic root (40 minutes)
#
# Consider $x^2-Bx+1=0$, where $B$ is an integer at least 3. The direct smaller
# root $(B-\sqrt{B^2-4})/2$ suffers cancellation for large $B$.
#
# Implement `small_root(B)` using the product of the roots. This restricted task
# does not need a general quadratic solver. Compare with the supplied 80-digit
# Decimal approximation for `B = 10, 10**4, 10**8`.

# %%
def decimal_small_root(B):
    # Approximate comparison reference, not a rigorous enclosure.
    with localcontext() as context:
        context.prec = 80
        Bd = Decimal(B)
        return (Bd - (Bd*Bd - 4).sqrt()) / 2

# %% tags=["exercise", "task-root"]
def small_root(B):
    raise NotImplementedError("Avoid subtracting nearly equal quantities")

# %% tags=["exercise", "check-root"]
for B in [10, 10**4, 10**8]:
    naive = (B - math.sqrt(B*B - 4)) / 2
    improved = small_root(B)
    assert 0 < improved < 1
    reference = decimal_small_root(B)
    with localcontext() as context:
        context.prec = 80
        for label, value in [("direct", naive), ("reformulated", improved)]:
            relative = abs((Decimal.from_float(value) - reference) / reference)
            print(B, label, value, "approximate relative error:", f"{relative:.3E}")
        assert abs((Decimal.from_float(improved) - reference) / reference) < Decimal("1e-14")

# %% [markdown] tags=["answer-root"]
# **Written answer:** derive your formula algebraically. Explain why agreement
# with the Decimal reference is not, by itself, a certificate. Does a small
# residual guarantee a small error for every quadratic and every candidate?

# %% [markdown]
# ## Task C · Summation: an improvement with limits (20 minutes)
#
# The implementations are supplied so you can focus on interpretation. The
# reference sum of the stored floats is computed exactly as a rational.

# %%
def naive_sum(values):
    total = 0.0
    for x in values:
        total += x
    return total

def kahan_sum(values):
    total = correction = 0.0
    for x in values:
        adjusted = x - correction
        updated = total + adjusted
        correction = (updated - total) - adjusted
        total = updated
    return total

examples = [[1.0] + [2.0**-54]*10000, [1e16, 1.0, -1e16]]
for values in examples:
    exact = sum((Fraction.from_float(x) for x in values), Fraction(0))
    for name, method in [("naive", naive_sum), ("Kahan", kahan_sum), ("fsum", math.fsum)]:
        result = method(values)
        print(name, result, "exact signed error:", Fraction.from_float(result) - exact)

# %% [markdown] tags=["answer-summation"]
# **Written answer:** what does the compensation help recover in the first case?
# What fails in the second? Why do these tests not prove accuracy on all inputs?

# %% [markdown]
# ## Homework · Turn an approximation into a certificate (30–45 minutes)
#
# For $B=10$, find positive rational endpoints `lo < hi < 1` enclosing the smaller
# root of $x^2-10x+1$. Verify opposite endpoint signs exactly, then explain why the
# derivative has a constant nonzero sign there. Give the midpoint and its error
# bound. A width at most $10^{-6}$ is enough; high digit counts are not the goal.

# %% tags=["exercise", "task-root-certificate"]
# Replace with exact rational endpoints and exact sign checks.
lo = None
hi = None

# %% tags=["exercise", "check-root-certificate"]
assert isinstance(lo, Fraction) and isinstance(hi, Fraction)
assert 0 < lo < hi < 1
assert hi - lo <= Fraction(1, 10**6)
assert (lo*lo - 10*lo + 1) > 0 > (hi*hi - 10*hi + 1)
print("Certified bracket arithmetic:", lo, hi)

# %% [markdown] tags=["answer-root-certificate"]
# **Certificate:** write the complete existence/uniqueness argument, including
# the interval and exact arithmetic evidence. State precisely which root is enclosed.

# %% [markdown]
# ## Optional extensions
#
# - Reproduce Rump's example from the lecture at several MPFR precisions. Compare
#   with the exact rational answer; record the evaluation order.
# - Compare forward and centered finite differences for $x^2$ at $x=1$.
#   Use the exact derivative 2 as a reference. Identify a range where smaller
#   steps worsen the result, and discuss truncation and rounding separately.
#
# **Reading:** Tucker §1.6, Examples 1.6.1–1.6.2, pp. 19–21.

