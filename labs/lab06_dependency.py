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
# # Lab 06 · Recover information by subdivision
#
# **Time:** about 2 hours. **Preparation:** [Lecture 06](../notebooks/06_dependency.ipynb).
#
# Compare equivalent formulas and then implement subdivision with complete coverage. Use exact rational intervals so changes in width come from the enclosure method.

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
import matplotlib.pyplot as plt
from IPython.display import display
from vc.intervals import RationalInterval as Interval
from vc.arb_bridge import evaluate_ball

def expanded(X):
    return X - X.square()

def product(X):
    return X * (1 - X)

def vertex(X):
    return Fraction(1, 4) - (X - Fraction(1, 2)).square()

domain = Interval(0, 1)
true_range = Interval(0, Fraction(1, 4))

# %% [markdown]
# ## Task A · Three formulas (25 minutes)
#
# Evaluate the three formulas on [0, 1]. Derive the true range analytically and compare enclosure widths.

# %% tags=["exercise"]
for name, formula in [("expanded", expanded), ("product", product), ("vertex", vertex)]:
    bound = formula(domain)
    assert true_range.is_subset_of(bound)
    print(name, bound, "width:", bound.width())


# %% [markdown]
# **Written answer:** Why can exact endpoint arithmetic still overestimate? Would 1,000-digit arithmetic resolve this example?

# %% [markdown]
# ## Task B · Cover, evaluate, combine (50 minutes)
#
# Write uniform subdivision into $2^{depth}$ pieces by repeated bisection, then hull all local images. Require a nonnegative integer depth. Preserve a point domain as one piece.

# %% tags=["exercise"]
def split_uniformly(domain, depth):
    raise NotImplementedError("Bisect every non-point piece at each level")

def enclose_by_pieces(evaluate, domain, depth):
    raise NotImplementedError("Combine all local enclosures with hull")


# %% tags=["exercise"]
widths = []
for depth in range(7):
    pieces = split_uniformly(domain, depth)
    assert pieces[0].lo == domain.lo
    assert pieces[-1].hi == domain.hi
    for index in range(len(pieces) - 1):
        assert pieces[index].hi == pieces[index + 1].lo
    bound = enclose_by_pieces(product, domain, depth)
    assert true_range.is_subset_of(bound)
    widths.append(float(bound.width()))
    print(depth, len(pieces), bound)
fig, ax = plt.subplots(figsize=(6, 3))
ax.plot(range(7), widths, "o-", label="enclosure width")
ax.axhline(0.25, color="black", linestyle="--", label="true range width")
ax.set(xlabel="Subdivision depth", ylabel="Width")
ax.legend()
display(fig)
plt.close(fig)


# %% [markdown]
# **Written answer:** Prove the coverage argument. Why does the width approach 1/4 rather than zero? Explain why checking only [0, 0.4] and [0.6, 1] would not certify the full range.

# %% [markdown]
# ## Task C · Certify a transcendental sign (35 minutes)
#
# Use Arb to enclose $(\sin x-x^2+1)\cos x$ on [0, 1/2]. Try a direct evaluation first, then subdivision if necessary. Work at 100 bits. State the certificate using exact endpoints.

# %% tags=["exercise"]
def trig_expression(x):
    raise NotImplementedError("Use the Arb methods sin and cos")

def trig_enclosure(X):
    return evaluate_ball(trig_expression, X, precision=100)


# %% tags=["exercise"]
trig_domain = Interval(0, Fraction(1, 2))
bound = enclose_by_pieces(trig_enclosure, trig_domain, depth=3)
assert bound.lo > 0
print("Certified enclosure:", bound)
print("Display approximation:", float(bound.lo), float(bound.hi))

# %% [markdown]
# **Written answer:** Which library operations justify the sign claim? What would a bound containing zero tell you? Would a dense positive plot be an alternative proof?

# %% [markdown]
# ## Submission
#
# Complete every exercise, replace the written-answer prompts with your explanations, then restart the kernel and run all cells. Include the assumptions behind each certificate and describe any inconclusive result.
