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
# # 09 · Find roots and justify the search
#
# **Time:** 110–120 minutes plus optional refinement. **Preparation:** Lectures 06–08, the intermediate and mean value theorems. **Lab:** [Root isolation and coverage](../labs/lab09_validated_roots.ipynb).
#
# Objectives: distinguish exclusion, existence, uniqueness, and completeness; derive interval Newton; inspect a search record; and retain unresolved regions when a test cannot decide.

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
from collections import Counter
import inspect
import numpy as np
import matplotlib.pyplot as plt
from IPython.display import display
from vc.intervals import RationalInterval as Interval
from vc.autodiff import Dual
from vc.roots import inspect_root, isolate_roots

def f(X):
    return X*X - 2

def derivative(X):
    return f(Dual(X, Interval(1))).derivative


# %% [markdown]
# ## EXPERIMENT · An approximation suggests a question
#
# Newton iteration from 1.5 quickly suggests √2. Its small residual does not itself give an interval containing a root or an all-roots statement. We will certify a specified interval instead.

# %%
guess = 1.5
for step in range(5):
    guess = guess - (guess*guess - 2)/(2*guess)
print("Approximate root:", guess, "residual:", guess*guess - 2)

left_value = f(Interval(1))
right_value = f(Interval(2))
assert left_value.hi < 0 < right_value.lo
print("Exact opposite signs at 1 and 2 establish existence by continuity.")

# %% [markdown]
# ## THEORY · Four different conclusions
#
# - **Exclusion:** if 0∉F(X), no root lies in X.
# - **Existence:** continuous f with certified opposite endpoint signs has a root between them.
# - **Uniqueness:** if a valid derivative interval excludes zero, f is strictly monotone on X and has at most one root there.
# - **Completeness:** every root in the original domain is accounted for by certified intervals, with no unresolved regions left.
#
# A zero-containing image provides none of the missing conclusions. A derivative excluding zero proves at most one root, not existence. A certificate on [1,2] says nothing about the negative root outside that interval.

# %% [markdown]
# ## THEORY · Derive interval Newton
#
# Assume f is continuously differentiable on a neighborhood of X=[a,b], let m be its exact midpoint, and suppose D encloses f′(X) with 0∉D. Let C enclose f(m). Define
#
# $$N(X)=[m,m]-C/D.$$
#
# If r∈X is a root, the mean value theorem gives 0=f(m)+f′(ξ)(r−m), hence r=m−f(m)/f′(ξ)∈N(X). Therefore **every root in X survives intersection with N(X)**.
#
# Consequences: an empty intersection excludes all roots in X; otherwise it can contract the set of possible roots. No existence premise has been smuggled into the contraction argument.

# %%
domain = Interval(1, 2)
center = Interval(domain.midpoint())
center_value = f(center)
slopes = derivative(domain)
newton_image = center - center_value / slopes
retained = domain.intersection(newton_image)
print("Derivative bounds:", slopes)
print("Newton image:", newton_image)
print("Retained:", retained)
assert retained.lo**2 < 2 < retained.hi**2

# %% [markdown]
# ## THEORY · A conservative existence and uniqueness test
#
# Under the preceding hypotheses, our success test is **N(X) strictly inside X**. This implies exactly one root in X, and that root belongs to X∩N(X).
#
# Here is a one-dimensional proof. Suppose D is positive. For every allowed slope d, the line f(m)+d(t−m) crosses zero at m−f(m)/d, inside X by the Newton inclusion. Thus each such line is negative at a and positive at b. Apply the mean value theorem separately between m and each endpoint: the actual endpoint values have these signs. Continuity gives existence, and the positive derivative gives uniqueness. For negative D reverse the signs. The computed C may be wider than {f(m)}; it still contains the line crossings used by the proof.
#
# Tucker §5.1.3 gives interval Newton results under its stated smoothness assumptions. We prove the C¹ scalar version above and deliberately require strict inclusion. Boundary cases can remain unresolved even when a different theorem or an exact calculation could settle them.

# %%
decision = inspect_root(f, derivative, domain)
print("Status:", decision.status)
assert decision.status == "certified"
assert decision.domain.lo < decision.newton.lo
assert decision.newton.hi < decision.domain.hi
print(inspect.getsource(inspect_root))


# %% [markdown]
# ## THEORY · Preserve the root set through a search
#
# The search maintains pending intervals. Each step excludes a region, certifies its one root, contracts without losing a root, or replaces a box by two covering children. Small undecided boxes become **unresolved**; if the step budget is exhausted, all pending boxes are also returned unresolved.
#
# Induction gives the invariant: every original root lies in a pending, certified, or unresolved interval. The decision record retains the original and retained intervals for every contraction. Contracted search boxes need not cover every non-root point of the original domain; the record explains those removals.
#
# The `tolerance` here stops refinement of undecided boxes. It is **not** a promised width for certified root intervals. One can subsequently refine a certified enclosure if a smaller error bound is needed.

# %%
def cubic(x):
    return (x+2)*(x-1)*(x-3)

def cubic_derivative(X):
    return cubic(Dual(X, Interval(1))).derivative

search = isolate_roots(cubic, cubic_derivative, Interval(-3, 4))
print("Search status:", search.status)
print("Decision counts:", Counter(item.status for item in search.decisions))
for certificate in search.certified:
    print("One root in", certificate.domain, "; tighter root bound:", certificate.retained)
print("Unresolved:", search.unresolved)
assert search.status == "complete"
assert len(search.certified) == 3
for certificate, root in zip(search.certified, [-2, 1, 3]):
    assert certificate.retained.contains(root)
for first, second in zip(search.certified, search.certified[1:]):
    assert first.retained.hi < second.retained.lo

# %%
xs = np.linspace(-3, 4, 401)
fig, ax = plt.subplots(figsize=(7, 3))
ax.plot(xs, cubic(xs), color="black")
ax.axhline(0, color="gray", linewidth=0.8)
for certificate in search.certified:
    part = certificate.retained
    ax.axvspan(float(part.lo), float(part.hi), color="tab:green", alpha=0.25)
ax.set(xlabel="x", ylabel="f(x)", title="Certified root enclosures; plot is illustrative")
display(fig)
plt.close(fig)

# %% [markdown]
# The algebraically known roots −2, 1, 3 provide an independent diagnostic. The computational count follows from the certificates, their disjoint root enclosures, and the absence of unresolved regions. A list of three good-looking approximations would not supply that argument.
#
# **AUDIT (10 minutes):** select a contraction record and explain why points outside its retained interval cannot be roots. Locate a subdivision record and check that both children were preserved.

# %% [markdown]
# ## Failure cases · Multiple roots, boundaries, and budgets
#
# For x² near zero, the derivative interval includes zero and the taught division is unavailable. For f(x)=x on [0,1], interval Newton reaches the boundary point {0}; strict interior inclusion does not succeed. Exact substitution proves that this point is a root, but this search intentionally has no separate boundary-root certification rule.

# %%
multiple = isolate_roots(lambda X: X.square(), lambda X: 2*X,
                         Interval(-1, 1), tolerance="1/100")
boundary = isolate_roots(lambda X: X, lambda X: Interval(1), Interval(0, 1))
limited = isolate_roots(cubic, cubic_derivative, Interval(-3, 4), max_steps=2)
for name, result in [("multiple root", multiple), ("boundary root", boundary), ("small budget", limited)]:
    print(name, result.status, "unresolved:", result.unresolved)
    assert result.unresolved
assert any(part.contains(0) for part in multiple.unresolved)
assert any(part.contains(0) for part in boundary.unresolved)

# %% [markdown]
# ## Exit ticket and reading
#
# A search certifies two roots and returns three unresolved intervals. Write an accurate conclusion. Explain why declaring every small interval “one root” is invalid and why overlapping enclosures cannot simply be counted twice.
#
# **Reading:** Tucker §§5.1.1–5.1.3, printed pp. 73–81, especially Theorem 5.5. Extended division and scalar Krawczyk in §§5.1.4–5.1.5 are optional. Next: [small nonlinear systems](10_nonlinear_systems.ipynb).
