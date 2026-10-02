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
# # Lab 07 · Instructor solution
#
# Implement the mean-value form and a monotonicity test. Then audit an adaptive enclosure algorithm, including its budget-limited outcome.

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
from vc.intervals import RationalInterval as Interval
from vc.enclosures import adaptive_range

def f(X):
    return X * (1 - X)

def derivative(X):
    return 1 - 2*X


# %% [markdown]
# ## Task A · Mean-value form (40 minutes)
#
# Implement $F(m)+F\prime(X)(X-m)$ with the midpoint treated as a point interval. Intersect the result with the natural enclosure; raise an error if the intersection is empty. Both evaluators must enclose the indicated function on the whole input.

# %%
def centered(evaluate, derivative, domain):
    center = Interval(domain.midpoint())
    center_value = evaluate(center)
    slopes = derivative(domain)
    displacement = domain - center
    return center_value + slopes * displacement

def combined(evaluate, derivative, domain):
    natural = evaluate(domain)
    mean_value_bound = centered(evaluate, derivative, domain)
    result = natural.intersection(mean_value_bound)
    if result is None:
        raise ValueError("The supplied enclosures are inconsistent")
    return result


# %%
domain = Interval(Fraction(1, 4), Fraction(3, 4))
true_range = Interval(Fraction(3, 16), Fraction(1, 4))
natural = f(domain)
mean_value_bound = centered(f, derivative, domain)
result = combined(f, derivative, domain)
assert true_range.is_subset_of(result)
assert result.is_subset_of(natural)
assert result.is_subset_of(mean_value_bound)
print("Natural:", natural)
print("Mean value:", mean_value_bound)
print("Intersection:", result)


# %% [markdown]
# **Worked explanation:** For each x, f(x)=f(m)+f′(ξ)(x−m), where ξ lies between m and x, hence inside X. Bounds on f(m) and every derivative value in X therefore enclose f(x). Two incorrect enclosures can overlap; an empty intersection detects inconsistency, but a nonempty one cannot verify the derivative formula.

# %% [markdown]
# ## Task B · Monotonicity and a tempting shortcut (35 minutes)
#
# Return the hull of endpoint value enclosures if the derivative interval is nonnegative or nonpositive. Otherwise return `None` to report an inconclusive test.

# %%
def monotone_bound(evaluate, derivative, domain):
    slopes = derivative(domain)
    if slopes.lo >= 0 or slopes.hi <= 0:
        left_value = evaluate(Interval(domain.lo))
        right_value = evaluate(Interval(domain.hi))
        return left_value.hull(right_value)
    return None


# %%
small = Interval(0, Fraction(1, 4))
bound = monotone_bound(f, derivative, small)
assert bound.lo == 0 and bound.hi == Fraction(3, 16)
assert monotone_bound(f, derivative, Interval(0, 1)) is None

def square(X):
    return X.square()

def midpoint_only_slope(X):
    # Deliberately invalid as a derivative enclosure on a non-point interval.
    return Interval(2 * X.midpoint())

wrong = centered(square, midpoint_only_slope, Interval(0, 1))
print("Incorrect shortcut:", wrong)
assert not wrong.contains(1)


# %% [markdown]
# **Worked explanation:** For x² on [0, 1], the midpoint slope is 1 but the derivative ranges over [0, 2]. The shortcut gives [−1/4, 3/4], missing f(1)=1. `None` means the derivative enclosure has not established a sign; overestimation could make this test fail even for a monotone function.

# %% [markdown]
# ## Task C · Audit adaptive stopping (35 minutes)
#
# Use your combined enclosure as the evaluator in the supplied `adaptive_range`. Inspect its short implementation in `vc/enclosures.py`. Check coverage explicitly after sorting the returned pieces. Compare an attainable local image-width target with a deliberately exhausted budget.

# %%
def evaluate(X):
    return combined(f, derivative, X)

resolved = adaptive_range(evaluate, Interval(0, 1), Fraction(1, 16), max_boxes=128)
limited = adaptive_range(evaluate, Interval(0, 1), Fraction(1, 10**6), max_boxes=2)
for result in [resolved, limited]:
    pieces = sorted(result.pieces, key=lambda piece: piece.domain.lo)
    assert pieces[0].domain.lo == 0
    assert pieces[-1].domain.hi == 1
    for index in range(len(pieces) - 1):
        assert pieces[index].domain.hi == pieces[index + 1].domain.lo
    assert Interval(0, Fraction(1, 4)).is_subset_of(result.enclosure)
    print(result.status, len(pieces), result.enclosure)
assert resolved.status == "resolved"
assert all(piece.enclosure.width() <= resolved.tolerance for piece in resolved.pieces)
assert limited.status == "budget_exhausted"

# %% [markdown]
# **Worked explanation:** `resolved` means every retained local image interval has width at most the target. `budget_exhausted` means the box limit was reached before that test passed. Both preserve a cover of the whole domain, so both enclose its range. The global range contains [0, 1/4], so it cannot have width ≤ 1/16. A stopping label says whether the requested refinement succeeded; it does not change the inclusion argument.
