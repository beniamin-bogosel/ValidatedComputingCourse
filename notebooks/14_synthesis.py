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
# # 14 · From numerical experiments to supported claims
#
# **Time:** 90–120 minutes including project demonstrations. **Preparation:** the completed course. There is no new programming assignment.
#
# Objectives: connect approximation, enclosure, local validation, and global coverage; revisit the opening numerical failures; and explain practical limits without overstating what has been proved.

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
import matplotlib.pyplot as plt
from IPython.display import display
from vc.intervals import RationalInterval as Interval
from vc.geometry import orientation
from vc.roots import inspect_root
from vc.optimization import minimize
from vc.systems import matrix_vector

# %% [markdown]
# ## Four questions to ask of a numerical result
#
# | Result | What it supplies | What still needs justification |
# |---|---|---|
# | An approximate root or minimizer | A candidate worth investigating | Existence, error, uniqueness, global scope |
# | A rigorous function enclosure | A bound on every allowed value | Whether it decides the sign or desired accuracy |
# | A local root certificate | Existence/uniqueness in a specified region | Whether roots exist elsewhere |
# | A completed global search | A domain-wide claim under its invariant | Input/model assumptions and implementation trust |
#
# Precision can help resolve arithmetic uncertainty. Reformulation can reduce cancellation or dependency. Subdivision can recover information lost by a wide enclosure. None of these repairs automatically supplies a missing coverage argument or removes physical input uncertainty.

# %% [markdown]
# ## Revisit the opening examples
#
# The cancellation examples taught us to distinguish the mathematical function from its floating-point evaluation. Exact input semantics explained why converting a decimal string and importing a stored float answer different questions. The Patriot-inspired model illustrated accumulated conversion error under explicitly simplified assumptions; its historical engineering context remains in the reference note.
#
# We now have several ways to make a concrete claim stronger: exact rational comparison, directed rounding, a sign enclosure, a derivative bound, or a theorem-backed search. Choose the method that establishes the needed conclusion.

# %%
n = 2 ** 27
turn = orientation((0, 0), (n, n - 1), (n + 1, n))
root = inspect_root(lambda X: X.square() - 2, lambda X: 2 * X, Interval(1, 2))
minimum = minimize(lambda X: (X.square() - 1).square(), Interval(-2, 2))
print("Exact-input orientation sign:", turn.sign)
print("One root in [1,2]:", root.status, root.retained)
print("Minimum value:", minimum.minimum, "status:", minimum.status)
print("Minimizer candidate intervals:", [piece.domain for piece in minimum.candidates])

# %% [markdown]
# ## EXPERIMENT · Wrapping without rounding error
#
# A rotation preserves lengths. Yet repeatedly rotating an axis-aligned interval box and replacing the result by another axis-aligned box can make the enclosure grow. This is wrapping: the representation loses relations between coordinates.
#
# Use the exact rational rotation matrix with cosine 3/5 and sine 4/5. Track a square in two ways: repeatedly apply interval matrix arithmetic, and rotate its four exact corners before taking a hull for display. The latter gives the true coordinate ranges because a linear image of a square has extrema at its vertices.

# %%
rotation = [[Fraction(3, 5), Fraction(-4, 5)],
            [Fraction(4, 5), Fraction(3, 5)]]
box = [Interval(-1, 1), Interval(-1, 1)]
corners = [(Fraction(x), Fraction(y)) for x in [-1, 1] for y in [-1, 1]]
box_widths, true_widths = [], []
for step in range(16):
    box_widths.append(float(box[0].width()))
    x_values = [point[0] for point in corners]
    true_widths.append(float(max(x_values) - min(x_values)))
    box = matrix_vector(rotation, box)
    new_corners = []
    for x, y in corners:
        new_x = Fraction(3, 5) * x - Fraction(4, 5) * y
        new_y = Fraction(4, 5) * x + Fraction(3, 5) * y
        new_corners.append((new_x, new_y))
    corners = new_corners
fig, ax = plt.subplots(figsize = (7, 3))
ax.semilogy(range(16), box_widths, "o-", label = "repeated box enclosure")
ax.semilogy(range(16), true_widths, "o-", label = "true coordinate width from exact corners")
ax.set(xlabel = "Number of rotations", ylabel = "Width", title = "Wrapping with exact rational arithmetic")
ax.legend()
display(fig)
plt.close(fig)

# %% [markdown]
# The widening cannot be blamed on insufficient arithmetic precision: every enclosure update and corner rotation used exact rational arithmetic. Only the plotted widths were converted to floats. A richer representation, better coordinates, or subdivision can help, at a computational cost. The mirror project also loses dependencies between position, direction, and event time as the trajectory grows.
#
# Higher dimension increases the cost of covering domains. Near singularity weakens root and system tests. Nonsmooth branches and ambiguous events require separate reasoning. These limits help determine a project's feasible scope.

# %% [markdown]
# ## Project demonstrations
#
# Give a short demonstration with the exact claim, one approximate exploration, the validation theorem and decisive bounds, one limitation, and the response to a peer-audit finding. Show the result from a fresh kernel and distinguish approximate plot labels from exact certificate endpoints.
#
# Submit the completed project notebook, its reproducible certificate data where applicable, and the peer audit with the author's response. See [the project rubric](../projects/README.md).
#
# ## Claim-classification discussion
#
# Classify each statement and repair it if necessary:
#
# - “Two precisions agree to ten digits, therefore those digits are certified.”
# - “The interval determinant contains zero, so the points are collinear.”
# - “The system residual is zero, so the surrounding box contains a unique root.”
# - “The optimization gap is zero, so the minimizer is localized.”
# - “The solver preserved unresolved boxes, so its partial certificate can still be useful.”
#
# A useful answer names the missing hypothesis or computation. For the first four statements, earlier notebooks supply counterexamples; the last statement is valid when the reported partial claims and retained search invariant are stated accurately.
#
# ## Beyond this introduction
#
# Taylor models, verified integration and ODE methods, higher-dimensional search, and formal proof assistants are possible next topics. They require additional representations, hypotheses, or software verification; this course has not implemented them. The [advanced-course review](../Doc/existing_course_review.md) records material for later study.
#
# The course's certificates rely on mathematical arguments, exact input descriptions, enclosing arithmetic, and correctly implemented search logic. Testing and peer audit strengthen confidence in those implementations; formal verification would be a separate task.
