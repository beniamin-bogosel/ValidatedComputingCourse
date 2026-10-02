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
# # 13 · Audit the claim, not just the output
#
# **Time:** 90–120 minutes, mainly workshop. **Preparation:** the methods used in your project. **Activity:** [Peer audit notebook](../assignments/peer_audit.ipynb).
#
# Objectives: reproduce a result, connect each conclusion to its assumptions and checks, detect a missing branch, and revise a claim precisely. This session consolidates earlier theorems rather than adding a new validation method.

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
from vc.intervals import RationalInterval as Interval
from vc.autodiff import Dual
from vc.roots import isolate_roots
from vc.mirrors import trace_lattice, final_distance

def cubic(x):
    return (x + 2) * (x - 1) * (x - 3)

def derivative(X):
    return cubic(Dual(X, Interval(1))).derivative


# %% [markdown]
# ## A reviewable certificate has several parts
#
# Record the mathematical claim and domain, exact input semantics, relevant theorem and hypotheses, precision and arithmetic, decisive bounds, search coverage or local scope, and stopping status. Add enough reproduction information to rerun the notebook from a fresh kernel.
#
# Reproduction is a necessary check, but a reproducible mistake is still a mistake. Review the code and the mathematical interpretation together. Numerical certification also relies on the arithmetic library and the implementation; it is not a formal proof of their source code.

# %% [markdown]
# ## AUDIT · A summary that silently drops work
#
# The author below runs the cubic search with a small budget, reports its certified roots, and claims the list is complete. The output dictionary is plausible-looking but discards the unresolved regions returned by the solver.

# %%
search = isolate_roots(cubic, derivative, Interval(-3, 4), max_steps = 2)
author_summary = {
    "domain": "[-3,4]",
    "roots": [str(item.retained) for item in search.certified],
    "all_roots_found": True,
}
print("Author summary:", author_summary)
print("Actual status:", search.status)
print("Unresolved intervals:", search.unresolved)
assert search.unresolved
assert search.status != "complete"

# %% [markdown]
# **Finding:** the code returned pending work as unresolved; the summary suppressed it. A complete root count is unsupported. The particular cubic has known roots, which also independently expose the omission.
#
# **Correction:** retain the certified intervals, unresolved intervals, and actual status. Say that all original roots remain accounted for by the union of certified root bounds and unresolved regions. To claim completeness, finish or otherwise settle those regions and establish distinctness before counting certificates.

# %%
corrected = {
    "certified": [str(item.retained) for item in search.certified],
    "unresolved": [str(part) for part in search.unresolved],
    "status": search.status,
    "all_roots_found": search.status == "complete",
}
print(corrected)
possible = [item.retained for item in search.certified] + search.unresolved
for root in [-2, 1, 3]:
    assert any(part.contains(root) for part in possible)

# %% [markdown]
# ## AUDIT · A reflection sequence is not automatically a trajectory certificate
#
# For the mirror model, inspect the finite lattice selection proof, every candidate collision or justified miss, strict time ordering, the final-time comparison, and the departure condition used to skip the previously hit mirror. Check that the endpoint is reported only after the requested time is reached.
#
# A budget-limited path has a valid last certified state, but that state occurs at its recorded elapsed time, not at the requested final time. Calling it a final-position enclosure would change the claim.

# %%
limited = trace_lattice(final_time = "3", precision = 100, max_collisions = 1)
print("Status:", limited.status, "reason:", limited.reason)
print("Last certified elapsed time:", limited.elapsed)
print("Requested time:", limited.final_time)
assert limited.status == "inconclusive"
try:
    final_distance(limited)
except ValueError as error:
    print("Endpoint claim rejected:", error)

# %% [markdown]
# ## Workshop · Exchange and inspect
#
# 1. State the author's claim in your own words before reading their conclusion.
# 2. Restart the kernel and rerun the notebook. Record environment, precision, runtime, and discrepancies.
# 3. Identify the theorem and match each hypothesis to an assumption, an analytic argument, or a computed bound.
# 4. Inspect one successful certificate and one inconclusive or limiting example.
# 5. Audit local versus global scope, omitted regions, boundary cases, and input uncertainty.
# 6. Give findings with cell references and their effect on the conclusion. Suggest a concrete correction.
#
# Use the [peer audit notebook](../assignments/peer_audit.ipynb). The project author should then record a response to each finding and revise the final claim where necessary.

# %% [markdown]
# ## Distinguish the review outcomes
#
# **Supported under stated assumptions:** the reviewer reproduced the computation and checked the indicated argument and bounds.
#
# **Needs correction:** identify the missing premise, implementation error, or overstated conclusion. A failed argument does not always imply the underlying mathematical claim is false.
#
# **Inconclusive:** the method or available evidence does not settle the requested claim. It may still establish a useful narrower result.
#
# **Exit ticket:** an author increases precision and obtains the same incorrect completeness summary. Which defect did that change fail to address? Next: [synthesis and demonstrations](14_synthesis.ipynb).
