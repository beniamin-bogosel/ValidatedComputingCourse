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
# # 01 · Why validated computing?
#
# **Time:** 90 minutes plus checkpoints. **Prerequisites:** Python, functions,
# elementary inequalities. **Lab:** [Numerical crime scene](../labs/lab01_intro.ipynb).
#
# By the end you should be able to distinguish an approximation, an error estimate,
# a rigorous enclosure, and a certificate; identify several sources of numerical
# error; and prove a small claim using exact arithmetic and elementary analysis.
#
# ## EXPERIMENT · Three plausible answers
#
# Predict each result before running the cell. The point is to explain what is
# computed, not to memorize surprising outputs.

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
import math
from fractions import Fraction
from vc.environment import require_binary64

require_binary64()
print("Decimal-looking sum:", 0.1 + 0.2)
print("Equals 0.3?", 0.1 + 0.2 == 0.3)
large = 1e16
print("Recovered increment:", (large + 1) - large)
candidate = 1.4142
print("Root candidate and residual:", candidate, candidate*candidate - 2)

# %% [markdown]
# ## THEORY · What is the claim?
#
# An **approximation** is a proposed value. An **error estimate** predicts its
# accuracy, sometimes using assumptions that have not been verified. An
# **enclosure** is a set proved to contain the intended exact value. A
# **certificate** records a precise claim together with checkable evidence and
# the assumptions that make that evidence sufficient.
#
# For example, “the output looks like 1.4142” and “the positive square root of 2
# lies between 1.4142 and 1.4143” ask for different evidence. Agreement between
# two programs may be useful, but both could share the same numerical weakness.
#
# **EXERCISE (5 minutes):** classify these statements: “two precisions agree,”
# “the exact value belongs to $[a,b]$,” “the graph crosses zero,” and “a continuous
# function has opposite signs at two exact endpoints.” Which need additional
# assumptions to imply existence of a root?

# %% [markdown]
# ## THEORY · Where error enters
#
# | Source | Example | What a validation must address |
# |---|---|---|
# | Input representation | Decimal 0.1 stored in binary | Which exact input was intended? |
# | Arithmetic rounding | Adding 1 to a large float | How far can each operation move its result? |
# | Truncation | Replacing an infinite sum by a finite sum | How large is the omitted tail? |
# | Discretization | Replacing a curve by a finite grid | What happens between grid points? |
# | Input uncertainty | A measured length with a tolerance | Which range of inputs must be covered? |
#
# Instability describes how an algorithm amplifies errors. Conditioning describes
# how the mathematical answer responds to changes in input. We develop that
# distinction in Lecture 03. There can be several error sources in one program.

# %% [markdown]
# ## EXPERIMENT · Recover the exact input stored in a float
#
# Python integers have arbitrary precision; `Fraction` implements exact rational
# arithmetic. We can ask exactly how the stored float differs from $1/10$.

# %%
intended = Fraction(1, 10)
stored = Fraction.from_float(0.1)
print("Stored rational:", stored)
print("Exact representation error:", stored - intended)
print("Approximate size of that error:", float(stored - intended))
assert stored > intended
assert Fraction(1, 10) + Fraction(2, 10) == Fraction(3, 10)

# %% [markdown]
# The last decimal printed is an approximation to the error. The fraction above
# it is exact. Exact rational arithmetic is enough for this question; it cannot
# represent every real number, such as $\sqrt{2}$, as a rational.
#
# **Checkpoint:** `Fraction(0.1)` preserves the input float. It does not undo the
# earlier conversion from the decimal literal. Predict `Fraction("0.1")`.

# %% [markdown]
# ## THEORY · From an error bound to an enclosure
#
# **Proposition.** If $a,x\in\mathbb R$, $e\geq0$, and $|x-a|\leq e$, then
#
# $$x\in[a-e,a+e].$$
#
# **Proof.** The absolute-value inequality is equivalent to
# $-e\leq x-a\leq e$. Add $a$ to each part. Conversely, subtracting $a$ from
# the endpoint inequalities gives the same absolute-value bound.
#
# Computing $a$ and guessing $e$ is not enough. We must justify the error bound,
# and ensure that any machine computation of endpoints does not shrink it.
# Today we avoid endpoint rounding by using exact rationals.

# %% [markdown]
# ## EXPERIMENT · A small residual is not an error bound
#
# Scaling a function changes its residual without changing its roots. Consider
# $h(x)=10^{-12}(x-1)$. At $x=0$ the residual is tiny, although the distance to
# its only root is one. We compute this example exactly.

# %%
scale = Fraction(1, 10**12)
x0 = Fraction(0)
residual = scale * (x0 - 1)
print("Exact residual:", residual)
print("Exact distance to the root:", abs(x0 - 1))

# %% [markdown]
# A residual becomes useful when connected to a theorem. For a differentiable
# scalar function with a known root $r$, a lower bound
# $|f'|\geq m>0$ along the segment gives $|x-r|\leq|f(x)|/m$ by the mean value
# theorem. Notice that this statement assumes a root exists; it does not create
# an existence proof from a residual.

# %% [markdown]
# ## THEORY + EXPERIMENT · Certify a square root
#
# Let $f(x)=x^2-2$, $a=14142/10000$, and $b=14143/10000$.
# The function is continuous, so opposite endpoint signs imply existence by the
# intermediate value theorem. It is strictly increasing for positive $x$ because
# $f'(x)=2x>0$, so that root is unique on $[a,b]$.
#
# The arithmetic checks below supply the sign evidence. The continuity and
# monotonicity arguments supply the mathematical implication.

# %%
a, b = Fraction(14142, 10000), Fraction(14143, 10000)
fa, fb = a*a - 2, b*b - 2
assert 0 < a < b
assert fa < 0 < fb
midpoint = (a + b) / 2
radius = (b - a) / 2
print("Exact endpoint signs:", fa, fb)
print(f"Certificate: exactly one zero of x² - 2 in [{a}, {b}].")
print(f"Its distance to midpoint {midpoint} is at most {radius}.")

# %% [markdown]
# We have now certified an enclosure without using an interval package. This
# works because the example has simple exact endpoints and a short proof. Later
# we automate analogous arguments for more complicated functions and domains.
# The certificate is conditional on the elementary mathematics and the correctness
# of the exact arithmetic implementation; it is not a formal proof of Python.
#
# **EXERCISE (10 minutes):** what changes if both endpoint signs are positive?
# Could there be zero roots, one multiple root, or two roots? Give examples.

# %% [markdown]
# ## A historical reason to track numerical assumptions
#
# The 1991 Patriot failure at Dhahran involved a loss of precision when converting
# integer clock ticks to real-valued time. The tracking error grew with operating
# duration. It is a useful example of a numerical assumption becoming invalid
# outside the intended operating conditions. We will model time-conversion error
# in Lecture 02, without claiming to reproduce the whole historical program.
# Source: [GAO report, pp. 5–6 and Appendix II](https://www.gao.gov/assets/imtec-92-26.pdf).

# %% [markdown]
# ## EXPERIMENT · A grid can miss a zero
#
# The continuous function $g(x)=(x-1/3)^2$ never changes sign. None of the eleven
# sampled points below equals $1/3$. A positive sample minimum is not a proof of
# positivity on the whole domain.

# %%
grid = [Fraction(k, 10) for k in range(11)]
values = [(x - Fraction(1, 3))**2 for x in grid]
print("All samples positive:", all(v > 0 for v in values))
print("Exact value at 1/3:", (Fraction(1, 3) - Fraction(1, 3))**2)

# %% [markdown]
# ## Recap and preparation for the lab
#
# Write conclusions about the intended exact problem. Separate observed agreement
# from a proved bound. State why the evidence implies existence, uniqueness, or
# exclusion, and report when it does not decide the question.
#
# **Exit ticket:** give one example where exact rational arithmetic settles the
# claim and one where additional analysis is required. What precisely does our
# square-root certificate prove, and what does the sample grid fail to prove?
#
# **Reading:** Tucker, Chapter 1, especially §1.2 and §1.6. Examples 1.6.1–1.6.2
# will return in Lecture 03. Historical note: [Patriot reference](../Doc/patriot_failure_reference.md).
# Next: [Lecture 02](02_floating_point.ipynb).
