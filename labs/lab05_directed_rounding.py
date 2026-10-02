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
# # Lab 05 · Make machine bounds trustworthy
#
# **Time:** about 2 hours. **Preparation:** [Lecture 05](../notebooks/05_directed_rounding.ipynb).
#
# Implement two directed operations, then audit conversion to Arb. Exact fractions are used to inspect endpoint bounds; float conversions are only for display.

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
import gmpy2
from flint import ctx
from vc.mpfr_intervals import MPFRInterval
from vc.intervals import RationalInterval as Interval
from vc.arb_bridge import to_ball, from_ball

left = MPFRInterval("0.1", precision=24)
right = MPFRInterval("0.3", precision=24)
print(left)
print(right)


# %% [markdown]
# ## Task A · Directed addition (30 minutes)
#
# Complete addition for two MPFR intervals at the same precision. Use separate `gmpy2.context` blocks with `RoundDown` and `RoundUp`; return an `MPFRInterval`. Its constructor accepts MPFR endpoints without a float conversion. Reject mismatched precisions.

# %% tags=["exercise"]
def add_outward(left, right):
    raise NotImplementedError("Round the lower bound down and the upper bound up")


# %% tags=["exercise"]
result = add_outward(left, right)
assert result.contains(Fraction(2, 5))
exact_sum = left.exact_bounds() + right.exact_bounds()
assert exact_sum.is_subset_of(result.exact_bounds())
print("Enclosure:", result.exact_bounds())
try:
    add_outward(left, MPFRInterval(1, precision=80))
except ValueError:
    print("Expected precision mismatch")
else:
    raise AssertionError("Mismatched precision was accepted")


# %% [markdown]
# **Written answer:** Give the chain of inequalities proving inclusion. Explain why rounding to nearest at both endpoints does not suffice.

# %% [markdown]
# ## Task B · Products with mixed signs (45 minutes)
#
# Implement multiplication by computing all four endpoint products in each directed context. Keep the two product lists visible. Use exact interval arithmetic on the stored bounds as a diagnostic oracle.

# %% tags=["exercise"]
def multiply_outward(left, right):
    raise NotImplementedError("Round four candidates down and four candidates up")


# %% tags=["exercise"]
original_precision = gmpy2.get_context().precision
original_rounding = gmpy2.get_context().round
for precision in [8, 24, 80]:
    for lo, hi in [("-2.3", "-0.1"), ("-1.2", "3.4"), ("0.1", "0.7")]:
        X = MPFRInterval(lo, hi, precision=precision)
        Y = MPFRInterval("-0.3", "1.1", precision=precision)
        exact_product = X.exact_bounds() * Y.exact_bounds()
        computed = multiply_outward(X, Y).exact_bounds()
        assert exact_product.is_subset_of(computed)
        print(precision, "extra width ≈", float(computed.width() - exact_product.width()))
assert gmpy2.get_context().precision == original_precision
assert gmpy2.get_context().round == original_rounding

# %% [markdown]
# **Written answer:** Why can the minimum product use different corners for different sign patterns? What does restoring the context protect?

# %% [markdown]
# ## Task C · Conversion audit (35 minutes)
#
# Run the exact endpoint audit below at several precisions. Then compare the semantics of a decimal string and a stored float. The helper deliberately converts Arb midpoint and radius back to exact fractions.

# %% tags=["exercise"]
domain = Interval("0.1", "0.3")
for precision in [24, 80, 160]:
    with ctx.workprec(precision):
        ball = to_ball(domain)
        recovered = from_ball(ball)
    assert domain.is_subset_of(recovered)
    print(precision, "extra width ≈", float(recovered.width() - domain.width()))

intended = MPFRInterval("0.1", precision=100)
stored = MPFRInterval(Fraction.from_float(0.1), precision=100)
print("Intended decimal:", intended.exact_bounds())
print("Stored binary float:", stored.exact_bounds())
assert intended.contains(Fraction(1, 10))
assert not stored.contains(Fraction(1, 10))

# %% [markdown]
# **Written answer:** Why is conversion through float unsafe for a certificate? Does increasing precision remove the width of the original interval? What if the converted ball crosses a function boundary?

# %% [markdown]
# ## Submission
#
# Complete every exercise, replace the written-answer prompts with your explanations, then restart the kernel and run all cells. Include the assumptions behind each certificate and describe any inconclusive result.
