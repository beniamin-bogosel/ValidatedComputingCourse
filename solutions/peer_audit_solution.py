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
# # Worked peer audit · Mirror project
#
# **Teaching example:** this is a model audit of a deliberately overstated draft, not a record of an external person's review. The draft uses the standard exact inputs, T=3 and 53 bits, but claims coordinate widths below 10^-20. The corrected model uses 100 bits.
#
# ## Claim and reproduction
#
# The intended claim concerns the final-time position and distance for the ideal integer-lattice mirror model. Reproduce both precision settings and inspect their exact widths. The floating-point display alone cannot establish the requested width.

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
from vc.mirrors import trace_lattice, final_distance

target_width = Fraction(1, 10**20)
draft = trace_lattice("3", 53)
revised = trace_lattice("3", 100)
for name, result in [("draft", draft), ("revised", revised)]:
    print(name, result.status, "widths:", [float(part.width()) for part in result.position])
assert draft.status == revised.status == "complete"
assert any(part.width() > target_width for part in draft.position)
assert all(part.width() <= target_width for part in revised.position)
assert final_distance(revised).width() <= target_width

# %% [markdown]
# ## Proof-condition and event audit
#
# The unit-speed reflection identity supplies the reachable-region argument. All lattice centers in that region are enumerated. For each completed event, the candidate checks must establish a positive simple entrance time strictly before competing events and before the remaining-time horizon. Departure from the current circle must be positive. The final flight must miss all remaining candidates before T.
#
# The notebook and helper code use Arb operations and exact endpoint extraction. Position, direction, and elapsed time are enclosed; dependencies may widen bounds but do not invalidate inclusion under the stated model. This audit checks the recorded inequalities and inspects the corresponding code; it does not formally verify the arithmetic library.

# %%
from vc.intervals import RationalInterval as Interval
from vc.mirrors import select_first

previous_time = Interval(0)
assert len(revised.checks) == len(revised.collisions) + 1
for event, checks in zip(revised.collisions, revised.checks):
    assert len(checks) == len(revised.centers)
    assert {check.center for check in checks} == set(revised.centers)
    action, selected = select_first(checks, Interval(3) - previous_time)
    assert action == "collision" and selected.center == event.center
    assert event.departure.lo > 0
    previous_time = event.elapsed
final_checks = revised.checks[-1]
remaining = Interval(revised.final_time) - previous_time
assert len(final_checks) == len(revised.centers)
assert {check.center for check in final_checks} == set(revised.centers)
for check in final_checks:
    assert not check.status.startswith("inconclusive")
    if check.status == "hit":
        assert check.time.lo > remaining.hi
print("Recorded collision decisions support the revised short-time claim.")

# %% [markdown]
# ## Findings and author response
#
# | Finding | Effect | Correction and response |
# |---|---|---|
# | The draft treated trajectory completion as meeting a 10^-20 width target | The time-3 enclosure is valid, but its claimed accuracy is unsupported | Add explicit exact width checks; rerun from the original inputs at 100 bits |
# | Decimal display rounded both endpoints to the same visible number | The display concealed the actual interval width | Print exact endpoints and a separate width; export fraction strings |
# | The interpretation must specify the shortened horizon | A time-3 result does not answer the original time-10 SIAM question | State T=3 in the claim, certificate, and final discussion |
#
# The revised computation reaches time 3 and meets all stated coordinate and distance width targets. It certifies the mirror sequence (1,0), (−1,1), (0,2). The target is an absolute interval-width bound, not an automatic claim about correctly rounded decimal digits.
#
# ## Outcome
#
# **Supported under stated assumptions for the revised claim.** The reviewed scope is the ideal short-time model and its displayed event inequalities. Tangent events, a general mirror geometry, and the original time-10 result are outside this model audit. The completed project includes low-precision, uncertain-input, and collision-budget limitations. A classroom peer should still independently rerun and inspect the submitted notebook and record their own findings.
