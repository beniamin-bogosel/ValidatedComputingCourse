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
# # Lab 01 · Numerical crime scene
#
# **Time:** 2 hours, including discussion; about 45 minutes of coding.
# **Preparation:** [Lecture 01](../notebooks/01_intro.ipynb).
# **Submit:** this notebook with implementations, executed checks, and written answers.
#
# The aim is to state what the evidence supports. Use exact rational arithmetic
# when possible. `float(...)` is acceptable for displaying an error, not for making
# an exact comparison. Cells tagged **exercise** need completion; diagnostic cells
# with the same tag should be run after the corresponding implementation.

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
from vc.environment import require_binary64

require_binary64()
print("Setup complete.")

# %% [markdown]
# ## Case A · Where did the tenth go? (25 minutes)
#
# **Claim to investigate:** “The literal `0.1` equals the rational $1/10$.”
# First run the ordinary computation. Explain the difference between what is shown
# on screen and the exact value stored.

# %%
print("Short display:", 0.1)
print("Longer display:", format(0.1, ".55f"))
print("Apparent equality:", 0.1 == 1 / 10)

# %% [markdown]
# Implement `representation_error(value, intended)` to return the **signed exact
# error** of a finite float relative to a `Fraction`. Then determine the sign of
# the errors for 0.1, 0.3, and 0.5. A useful tool is `Fraction.from_float`.

# %% tags=["exercise", "task-representation"]
def representation_error(value, intended):
    raise NotImplementedError("Return an exact Fraction; do not compare rounded decimals")

# %% tags=["exercise", "check-representation"]
assert representation_error(0.5, Fraction(1, 2)) == 0
error = representation_error(0.1, Fraction(1, 10))
assert isinstance(error, Fraction)
assert Fraction.from_float(0.1) == Fraction(1, 10) + error
for value, intended in [(0.1, Fraction(1, 10)), (0.3, Fraction(3, 10)), (0.5, Fraction(1, 2))]:
    print(value, representation_error(value, intended))

# %% [markdown] tags=["answer-representation"]
# **Written answer:** Why does `0.1 == 1/10` fail to test the stated claim?
# What does your exact calculation establish? Replace this paragraph with your answer.

# %% [markdown]
# ## Case B · The reassuring residual (25 minutes)
#
# **Claim to investigate:** “A residual smaller than $10^{-10}$ means the root
# error is smaller than $10^{-10}$.” Use $h(x)=10^{-12}(x-1)$ at $x=0$ to test
# the claim exactly. Compare residual and distance to the unique root.

# %% tags=["exercise", "task-residual"]
# Assign exact Fraction values. No approximate root finder is needed.
residual = None
root_error = None

# %% tags=["exercise", "check-residual"]
assert isinstance(residual, Fraction) and isinstance(root_error, Fraction)
assert abs(residual) < Fraction(1, 10**10)
assert root_error > Fraction(1, 10**10)
print("Residual:", residual, "distance to the root:", root_error)

# %% [markdown] tags=["answer-residual"]
# **Written answer:** Identify an additional hypothesis that could connect a
# residual with root error. Does that hypothesis alone prove a root exists?

# %% [markdown]
# ## Case C · Produce a certificate (35 minutes)
#
# **Claim:** $x^2-3$ has exactly one root in $[1.732,1.733]$.
# Store these endpoints as exact rationals. Implement the endpoint checks below.
# The function should return True only for ordered positive endpoints with strict
# opposite signs. For this lab it accepts `Fraction` endpoints and only handles
# the function $x^2-3$; it is not a general root-isolation algorithm.

# %% tags=["exercise", "task-certificate"]
def sqrt3_bracket_verified(a, b):
    raise NotImplementedError("Check ordering, positivity, and exact endpoint signs")

# %% tags=["exercise", "check-certificate"]
lo, hi = Fraction(1732, 1000), Fraction(1733, 1000)
assert sqrt3_bracket_verified(lo, hi)
assert not sqrt3_bracket_verified(hi, lo)
assert not sqrt3_bracket_verified(Fraction(2), Fraction(3))
assert not sqrt3_bracket_verified(Fraction(-2), Fraction(2))
print("Endpoint checks passed for:", lo, hi)

# %% [markdown] tags=["answer-certificate"]
# **Certificate:** State the function and domain, the exact signs, the continuity
# argument, and the uniqueness argument. Give a midpoint and a rigorous absolute
# error bound. Explain why the rejected interval `[-2, 2]` need not be root-free.

# %% [markdown]
# ## Case D · A positive grid (15 minutes)
#
# Run the exact samples below. Explain why they do not prove strict positivity of
# the function throughout `[0, 1]`. State a counterexample point exactly.

# %%
grid = [Fraction(k, 10) for k in range(11)]
sample_values = [(t - Fraction(2, 7))**2 for t in grid]
assert all(v > 0 for v in sample_values)
print("All grid values are positive; smallest sampled value:", min(sample_values))

# %% [markdown] tags=["answer-grid"]
# **Written answer:** Give the missing point and distinguish evidence from a
# domain-wide statement. Would using 1,000 samples automatically repair the proof?

# %% [markdown]
# ## Homework and optional extension
#
# **Homework (20 minutes):** choose one false claim above and rewrite it as a true,
# precisely scoped statement. Identify the mathematical argument and the trusted
# arithmetic supporting it.
#
# **Optional:** enclose $\sqrt{3}$ more tightly with rational endpoints. Derive a
# stopping criterion from interval width; do not use matching printed digits as
# the criterion. This anticipates later validated root-finding labs.
#
# **Submission checklist:** restart and run all cells; retain outputs; replace the
# four written-answer placeholders; identify any unresolved task honestly.

