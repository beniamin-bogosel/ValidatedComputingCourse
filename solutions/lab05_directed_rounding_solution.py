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
# # Lab 05 · Instructor solution
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
    working_folder = Path("/content/validated-course") / 'solutions'
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

# %%
def add_outward(left, right):
    if left.precision != right.precision:
        raise ValueError("Use the same precision for both operands")
    precision = left.precision
    with gmpy2.context(precision=precision, round=gmpy2.RoundDown):
        lower = left.lo + right.lo
    with gmpy2.context(precision=precision, round=gmpy2.RoundUp):
        upper = left.hi + right.hi
    return MPFRInterval(lower, upper, precision=precision)


# %%
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
# **Worked explanation:** For all admissible a and b, down(left.lo + right.lo) ≤ left.lo + right.lo ≤ a+b ≤ left.hi + right.hi ≤ up(left.hi + right.hi). Nearest rounding may move the lower endpoint up or the upper endpoint down, losing an extreme value.

# %% [markdown]
# ## Task B · Products with mixed signs (45 minutes)
#
# Implement multiplication by computing all four endpoint products in each directed context. Keep the two product lists visible. Use exact interval arithmetic on the stored bounds as a diagnostic oracle.

# %%
def multiply_outward(left, right):
    if left.precision != right.precision:
        raise ValueError("Use the same precision for both operands")
    precision = left.precision
    with gmpy2.context(precision=precision, round=gmpy2.RoundDown):
        lower_products = [left.lo * right.lo, left.lo * right.hi,
                          left.hi * right.lo, left.hi * right.hi]
    with gmpy2.context(precision=precision, round=gmpy2.RoundUp):
        upper_products = [left.lo * right.lo, left.lo * right.hi,
                          left.hi * right.lo, left.hi * right.hi]
    lower = min(lower_products)
    upper = max(upper_products)
    return MPFRInterval(lower, upper, precision=precision)


# %%
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
# **Worked explanation:** The multiplication extrema depend on endpoint signs; selecting only lower×lower and upper×upper fails for mixed or negative signs. Computing all corners handles every bounded sign case. Local contexts prevent one calculation from silently changing later calculations or library calls.

# %% [markdown]
# ## Task C · Conversion audit (35 minutes)
#
# Run the exact endpoint audit below at several precisions. Then compare the semantics of a decimal string and a stored float. The helper deliberately converts Arb midpoint and radius back to exact fractions.

# %%
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
# **Worked explanation:** Nearest binary64 conversion can move a certified endpoint inward. Exact midpoint/radius conversion preserves the actual Arb ball. More precision reduces representation error, but the original width 1/5 remains. Ball conversion can widen the domain; the function must be defined throughout that ball, and a nonfinite result cannot be used as a finite certificate.
