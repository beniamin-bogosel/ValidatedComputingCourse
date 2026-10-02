# ---
# jupyter:
#   course:
#     kind: assessment
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
# # Capstone peer audit
#
# **Reviewer:** [name] · **Author:** [name] · **Project notebook:** [path] · **Date:** [date]
#
# **Time:** 45–60 minutes for the first review, followed by author revisions. Use [Lecture 13](../notebooks/13_certificate_audit.ipynb) as guidance. This notebook is a record of your review, not an automatic correctness checker.

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
    working_folder = Path("/content/validated-course") / 'assignments'
    working_folder.mkdir(parents=True, exist_ok=True)
    os.chdir(working_folder)
    print("Course helpers ready:", vc.__version__)


# %% [markdown]
# ## 1 · Claim as understood by the reviewer
#
# Restate the mathematical claim, domain, inputs, uncertainty model, and accuracy target. Separate local and global conclusions. Identify the meaning of every status in the author's final report.

# %% [markdown]
# ## 2 · Reproduction
#
# Record the interpreter and library versions, input encoding, precision, and runtime. Restart the project kernel and run all cells. Record discrepancies and the exact notebook/cell involved. Do saved certificate data agree with a newly generated run?

# %% [markdown]
# ## 3 · Proof conditions
#
# Name the theorem or invariant. For each premise, identify its source: problem assumption, analytic proof, or computed bound. Inspect input conversion, elementary-function domains, rounding/enclosure operations, and output conversion. Check a limiting or inconclusive example as well as the successful case.

# %% [markdown]
# ## 4 · Coverage and decisions
#
# For a search, account for retained, certified, excluded, and unresolved regions. For geometry, distinguish exact and uncertain coordinates. For mirrors, check all candidate mirrors, the reachable-region argument, collision ordering, departure, and the final-time comparison. Explain what prevents an omitted branch from invalidating the claim.

# %% [markdown]
# ## 5 · Findings
#
# | Cell or record | Finding and evidence | Effect on the claim | Suggested correction |
# |---|---|---|---|
# | [reference] | [observation] | [which conclusion is affected] | [specific action] |
#
# Distinguish a false mathematical claim from a claim whose supplied proof is incomplete.

# %% [markdown]
# ## 6 · Review outcome
#
# Choose and justify: **supported under stated assumptions**, **needs correction**, or **inconclusive**. State precisely which code, computations, and arguments you checked; list any remaining review limits.

# %% [markdown]
# ## 7 · Author response and final revision
#
# Respond to each finding. Record the changed cells or certificate fields, rerun results, and any narrowing of the final claim. Include the revised conclusion here so that the audit and final submission agree.
