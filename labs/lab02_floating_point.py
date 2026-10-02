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
# # Lab 02 · Inspect the machine
#
# **Time:** 2 hours; 60–90 minutes coding. **Preparation:**
# [Lecture 02](../notebooks/02_floating_point.ipynb).
#
# Investigate representation and rounding with exact references. Complete exercise
# cells, then run the diagnostic cells. Submit code, plots, and written explanations.

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
import sys
from fractions import Fraction
from decimal import Decimal, localcontext
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
from vc.environment import require_binary64

require_binary64()
print("Significand bits:", sys.float_info.mant_dig)

# %% [markdown]
# ## Task A · Predict neighboring gaps (30 minutes)
#
# Implement `neighbor_gaps(x)` for finite positive floats whose neighbors are also
# finite. Return the exact rational gaps below and above `x`. Convert neighbors
# to fractions **before** subtraction. Explain why these gaps differ at 1 and 2.

# %% tags=["exercise", "task-gaps"]
def neighbor_gaps(x):
    raise NotImplementedError("Return two Fractions using math.nextafter")

# %% tags=["exercise", "check-gaps"]
assert neighbor_gaps(1.0) == (Fraction(1, 2**53), Fraction(1, 2**52))
assert neighbor_gaps(1.5) == (Fraction(1, 2**52), Fraction(1, 2**52))
assert neighbor_gaps(2.0) == (Fraction(1, 2**52), Fraction(1, 2**51))
assert neighbor_gaps(math.nextafter(0.0, math.inf)) == (Fraction(1, 2**1074),)*2
for x in [0.5, 1.0, 1.5, 2.0]:
    print(x, neighbor_gaps(x))

# %% [markdown] tags=["answer-gaps"]
# **Written answer:** derive the upward gap at $2^e$ for normal binary64 values.
# Explain the change at a binade boundary and how subnormal spacing differs.

# %% [markdown]
# ## Task B · Lost increments (20 minutes)
#
# Find the smallest nonnegative integer `n` for which `(2.0**n + 1) == 2.0**n`.
# Use a bounded search and explain why the result follows from ties-to-even.
# Also evaluate `(2.0**n - 1) == 2.0**n` at that same exponent.

# %% tags=["exercise", "task-threshold"]
def first_lost_increment():
    raise NotImplementedError("Search n = 0, ..., 60")

# %% tags=["exercise", "check-threshold"]
n = first_lost_increment()
assert isinstance(n, int) and 0 < n <= 60
assert 2.0**n + 1 == 2.0**n
assert all(2.0**k + 1 != 2.0**k for k in range(n))
print("First exponent:", n)
print("Subtraction also lost?", 2.0**n - 1 == 2.0**n)

# %% [markdown] tags=["answer-threshold"]
# **Written answer:** distinguish machine epsilon from unit roundoff. Explain
# why the increment experiment is about rounding of arithmetic, not rounding of 1.

# %% [markdown]
# ## Task C · Audit decimal input (15 minutes)
#
# First predict which expression in each pair preserves a previously rounded
# float. Then run the cell and compare their exact rational values.

# %%
with localcontext() as context:
    context.prec = 60
    print("Decimal from string:", Decimal("0.3"))
    print("Decimal from float: ", Decimal(0.3))
print("Fraction from string:", Fraction("0.3"))
print("Fraction from float: ", Fraction.from_float(0.3))

# %% [markdown] tags=["answer-input"]
# **Written answer:** does switching to 60 digits after constructing `0.3` recover
# the intended decimal? Explain what should be stored if the original input is a
# measurement known only to lie in `[0.29, 0.31]`.

# %% [markdown]
# ## Task D · Bound a time-conversion error (35 minutes)
#
# This is a simplified model inspired by the Patriot example, not its full software.
# A counter records exact tenths of seconds. The conversion constant $1/10$ is
# truncated downward to `bits` binary fractional places.
#
# Implement `time_conversion_error(hours, bits)` for nonnegative **integer** hours
# and positive integer `bits`. Return the exact nonnegative error in seconds.
# Use integer arithmetic to construct the truncated constant; avoid converting
# `0.1` into a fraction. Compare 16, 23, and 32 fractional bits over 0–100 hours.

# %% tags=["exercise", "task-time"]
def time_conversion_error(hours, bits):
    raise NotImplementedError("Compute the exact bias multiplied by the integer tick count")

# %% tags=["exercise", "check-time"]
assert time_conversion_error(0, 23) == 0
assert isinstance(time_conversion_error(1, 23), Fraction)
assert time_conversion_error(100, 23) == 100 * time_conversion_error(1, 23)
for bits in [16, 23, 32]:
    assert 0 <= time_conversion_error(100, bits) < Fraction(100*3600*10, 2**bits)
print("100-hour error, 23 bits:", time_conversion_error(100, 23))

# %% tags=["exercise", "task-time-plot"]
hours_grid = list(range(101))
fig, ax = plt.subplots(figsize=(6, 3))
for bits in [16, 23, 32]:
    ax.plot(hours_grid, [float(time_conversion_error(h, bits)) for h in hours_grid], label=str(bits))
ax.set(xlabel="hours", ylabel="timing error (seconds)")
ax.legend(title="fractional bits")
display(fig)
plt.close(fig)

# %% [markdown] tags=["answer-time"]
# **Written answer:** derive an upper bound using only the number of bits and ticks.
# At 23 fractional bits, determine the largest integer operating time in hours
# for which the **exact model error** is at most 1/100 second. Explain what your
# conclusion assumes, and why this is not a historical system-operation recommendation.

# %% [markdown]
# ## Homework and an inconclusive case
#
# **Homework (20 minutes):** the exact number $2^{-1075}$ rounds to zero in
# binary64 under nearest-even. Compute its relative error and explain why the
# normal-range $u$ bound does not apply. State an absolute bound instead.
#
# **Optional:** write a binary64 decoder using `struct`, and reconstruct normal
# values as exact fractions. Extend it to subnormals, distinguishing finite values
# from infinities and NaNs rather than treating all exponent fields alike.
#
# **Conclusion:** could a plot of time-conversion error alone certify a bound at
# every duration? Identify the mathematical formula that makes the bound rigorous.

