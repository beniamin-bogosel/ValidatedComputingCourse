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
# # Concept check · Lectures 08–11 · Instructor key
#
# **20 points · 35–45 minutes.** Explain the mathematical claims; no computation is required.

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


# %% [markdown]
# ## 1 · Differentiation guarantees (4 points)
#
# Explain why forward-mode AD with float components is not automatically validated differentiation. State the additional assumptions needed for interval AD. What goes wrong with choosing one branch from an interval midpoint?

# %% [markdown]
# **Marking key:** One point: AD propagates differentiation rules for the real expression, but float arithmetic still rounds. Two points: all component operations/input conversions preserve inclusion and the expression is differentiable on the full domain, including valid denominators and elementary-function domains. One point: the midpoint branch may not apply throughout the interval, which may also contain a nondifferentiable boundary.

# %% [markdown]
# ## 2 · Interval Newton (4 points)
#
# State the interval Newton image and its hypotheses. Explain what empty intersection proves and what strict interior inclusion proves. Does a derivative interval excluding zero alone prove existence?

# %% [markdown]
# **Marking key:** One point: for C¹ f, m in X, C containing f(m), and D containing all derivatives with 0 outside D, N=m−C/D. One point: N intersect X empty proves exclusion because every root in X belongs to N. One point: N strictly inside X proves existence and uniqueness under the stated scalar hypotheses. One point: a nonzero derivative bound only proves at most one root; f(x)=x+3 on [0,1] has no root.

# %% [markdown]
# ## 3 · Search completeness (4 points)
#
# A search returns three certified intervals and two unresolved intervals. It contracts some boxes and reaches a step budget. What can it claim? Describe what must be preserved at contraction, splitting, and budget exhaustion. Can overlapping root enclosures simply be counted?

# %% [markdown]
# **Marking key:** One point: each certificate proves its local claim, but a complete root count is not established. One point: contraction must retain every root in its parent; splitting must cover the parent. One point: all pending regions must be returned unresolved at budget exhaustion. One point: overlapping enclosures may refer to the same root; distinctness needs evidence before counting. The certified intervals are not promised to meet the unresolved-box width tolerance.

# %% [markdown]
# ## 4 · A local system certificate (4 points)
#
# For T(x)=x−Rf(x), give the Krawczyk enclosure and the conservative test taught in the course. Explain the role of R and identify the region where uniqueness is established.

# %% [markdown]
# **Marking key:** One point: K=m−RF(m)+(I−RJ(X))(X−m), with a valid interval Jacobian over X. One point: require K strictly inside X and a verified infinity-norm contraction bound q<1. One point: R must be fixed and nonsingular so a fixed point is a root; an approximate inverse is acceptable when the inequalities are verified. One point: C¹ smoothness is required on a neighborhood of X and uniqueness is local to X, not global.

# %% [markdown]
# ## 5 · Preserve all global minimizers (4 points)
#
# Given a feasible point z and an enclosure F(z)=[l,u], which endpoint is a safe incumbent? State the pruning rule when all minimizers must be retained. Explain why a zero value gap can coexist with wide candidate boxes, and what survives budget exhaustion.

# %% [markdown]
# **Marking key:** One point: u bounds the attainable value from above. One point: prune only when a local lower bound is strictly greater than the incumbent; equality may contain a tied minimizer. One point: a constant function has an exact minimum value and an entire minimizing domain. One point: the minimum-value enclosure and all-minimizers containment remain valid after budget exhaustion, while the requested value gap is not claimed.
