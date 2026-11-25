# ---
# jupyter:
#   course:
#     kind: application
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
# # Application 13 · Audit four submitted certificates
#
# **Builds on:** [Lecture 13](../notebooks/13_certificate_audit.ipynb) (reproduction, assumptions, coverage) and Lectures 04–09.
#
# **Time:** about 60 minutes, in pairs. **You will decide:** for each of four short "submitted" certificates, whether the claim is supported, and if not, whether the *claim* is false or only the *argument* is broken.
#
# Each submission runs without errors and prints a confident conclusion. Some contain one planted flaw; at least one is correct. Do not invent flaws: a correct certificate must be accepted, and every rejection needs a reproducible probe.

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
# and do not open sibling notebooks automatically in Colab.
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
    working_folder = Path("/content/validated-course") / 'applications'
    working_folder.mkdir(parents=True, exist_ok=True)
    os.chdir(working_folder)
    print("Course helpers ready:", vc.__version__)

# %%
from fractions import Fraction
import math
import numpy as np
from flint import arb, ctx
from vc.intervals import RationalInterval as Interval
from vc.autodiff import Dual        # available for your probes
from vc.roots import inspect_root, isolate_roots
from vc.enclosures import subdivide

# %% [markdown]
# ## Audit checklist
#
# For each submission, answer in order:
#
# 1. **Claim.** What exactly is claimed? About which inputs and which domain?
# 2. **Theorem.** Which mathematical statement turns the computation into the claim? Are its premises (continuity, differentiability, nonzero derivative, …) met?
# 3. **Coverage.** Does the computation account for the *whole* domain, with no gaps?
# 4. **Enclosures.** Is every quantity used as a bound actually a valid enclosure (outward rounding, remainders, no sampling)?
# 5. **Verdict.** Accept, or reject with (a) the flaw, (b) a probe that demonstrates it, and (c) whether the claim itself is false or merely unsupported.
#
# **Tip for probes.** Inside functions that may receive intervals or dual numbers, write `x * Fraction(1, 10000)` rather than `x / 10000`: dividing a dual number by an integer produces a binary64 float, which `RationalInterval` rejects on purpose.

# %% [markdown]
# ## Submission A · A maximum bound by subdivision
#
# *"Let f(x) = x(1 − x)(x + 1/2). We claim max over [0, 1] of f ≤ 0.35. Proof: we cover [0, 1] by ten intervals of width 1/10, evaluate f in exact interval arithmetic on each, and take the largest upper endpoint."*

# %%
def f_A(X):
    return X * (1 - X) * (X + Fraction(1, 2))

edges = np.arange(0, 1, 0.1)
pieces_A = [Interval(Fraction(e), Fraction(e) + Fraction(1, 10)) for e in edges]
bound_A = max(f_A(piece).hi for piece in pieces_A)
print(f"{len(pieces_A)} pieces, largest upper bound {float(bound_A):.4f}")
print("Claim A: max f <= 0.35 on [0, 1]:", bound_A <= Fraction(35, 100))

# %% [markdown]
# **Your audit of A.** Use the checklist. Write probes below.

# %%
# Probes for Submission A


# %% [markdown]
# ## Submission B · Exactly one root
#
# *"Let g(x) = x³ − x/10000. We claim g has exactly one root in [−1, 1]. Existence: g(−1) < 0 < g(1), computed exactly. Uniqueness: g′(x) = 3x² − 1/10000 is positive at all 20 points of a uniform grid on [−1, 1], so g is increasing."*

# %%
def g_B(x):
    return x**3 - x / 10000

def g_B_prime(x):
    return 3 * x**2 - Fraction(1, 10000)

existence = g_B(Fraction(-1)) < 0 < g_B(Fraction(1))
grid = [Fraction(v).limit_denominator(1000) for v in np.linspace(-1, 1, 20)]
increasing = all(g_B_prime(x) > 0 for x in grid)
print("sign change:", existence, "  derivative positive on grid:", increasing)
print("Claim B: exactly one root in [-1, 1]:", existence and increasing)

# %% [markdown]
# **Your audit of B.**

# %%
# Probes for Submission B


# %% [markdown]
# ## Submission C · An enclosure of e
#
# *"We claim e ∈ [s, s + 10⁻¹²], where s = Σ_{k=0}^{10} 1/k!. The sum is computed exactly with fractions, so there is no rounding error at all, and 10⁻¹² is a generous safety margin."*

# %%
s = sum(Fraction(1, math.factorial(k)) for k in range(11))
claimed_C = Interval(s, s + Fraction(1, 10**12))
print(f"s = {float(s):.15f}")
print("Claim C: e lies in", [float(claimed_C.lo), float(claimed_C.hi)])

# %% [markdown]
# **Your audit of C.**

# %%
# Probes for Submission C


# %% [markdown]
# ## Submission D · A root of x² − 2
#
# *"We claim x² − 2 has exactly one root in the printed interval R ⊆ [1, 2]. We apply one interval Newton step from Lecture 09 to X = [1, 2], using an interval enclosure of the derivative over X. The Newton image lies strictly inside X, which proves existence and uniqueness of a root in X, and every root in X lies in the intersection R."*

# %%
def h_D(X):
    return X.square() - 2

def h_D_prime(X):
    return 2 * X

decision = inspect_root(h_D, h_D_prime, Interval(1, 2))
print("status:", decision.status)
print("derivative enclosure:", decision.slopes)
print("Newton image:", [float(decision.newton.lo), float(decision.newton.hi)])
print("Claim D: unique root in R =", [float(decision.retained.lo), float(decision.retained.hi)])

# %% [markdown]
# **Your audit of D.**

# %%
# Probes for Submission D


# %% [markdown]
# ## Summary table
#
# | Submission | Verdict | Flaw (checklist item) | Probe | Claim false, or only unsupported? |
# |---|---|---|---|---|
# | A | | | | |
# | B | | | | |
# | C | | | | |
# | D | | | | |
#
# **Discussion.** Which flaw would be hardest to find by reading the printed output alone? Which one could a referee only find by rerunning the code? For a rejected but true claim, write the smallest change that turns the submission into a valid certificate.
