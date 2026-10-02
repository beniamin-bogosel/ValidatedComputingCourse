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
# # Concept check · Lectures 04–07
#
# **20 points · 30–40 minutes.** Explain your answers; no execution or external reading is required.

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
# ## 1 · Independent choices (4 points)
#
# For X = [−2, 3], give X − X and the range of x − x. Give X * X and the range of x². Explain why these answers differ.

# %% [markdown]
# **Answer:**

# %% [markdown]
# ## 2 · Outward rounding (4 points)
#
# State directed endpoint formulas for addition. Explain why decimal input conversion is part of the proof. Does increasing precision remove uncertainty in a measured input [1, 2]?

# %% [markdown]
# **Answer:**

# %% [markdown]
# ## 3 · Complete coverage (4 points)
#
# You enclose f on [0, 2/5] and [3/5, 1]. Does the hull of those two images enclose f([0, 1])? Give a counterexample using f(x)=x(1−x). What additional condition makes subdivision valid?

# %% [markdown]
# **Answer:**

# %% [markdown]
# ## 4 · Derivative bounds (4 points)
#
# State the hypotheses and formula for a mean-value enclosure. For f(x)=x² on [0, 1], show why substituting only f′(1/2) for a derivative bound is invalid.

# %% [markdown]
# **Answer:**

# %% [markdown]
# ## 5 · Stopping and conclusions (4 points)
#
# An adaptive routine keeps a covering list and stops when every local image has width ≤ 1/16, or when it reaches a box budget. Explain both outcomes. Must the final global image have width ≤ 1/16? What happens if difficult pieces are silently discarded?

# %% [markdown]
# **Answer:**
