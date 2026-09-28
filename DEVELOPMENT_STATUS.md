# Development status

## First milestone: foundation and Lectures/Labs 01–03

Implemented:

- An isolated `.venv`, pinned dependency snapshot, editable `vc` package, and project-local Jupyter kernel.
- Setup notebook and three lecture notebooks with theory, proofs, experiments, plots, checkpoints, and references.
- Three student lab notebooks and standalone instructor solutions with worked explanations.
- A 20-point conceptual assessment and instructor key.
- Four notebook templates: lecture, lab, project, and peer audit.
- Explicit Jupytext synchronization, paired-source checks, fresh-kernel execution, and workflow/arithmetic regression tests.
- Course index, syllabus, reading map, and instructor pacing/marking notes.

The first block incorporates exact input checks, rational root certificates, the Patriot-inspired conversion model, Tucker's polynomial cancellation example, stable quadratic roots, and summation. Rump's expression and finite differences are optional extensions in Lecture 03. The mirror-trajectory capstone is implemented in the fourth milestone below.

## Second milestone: interval core, Lectures/Labs 04–07

Implemented:

- Four lecture notebooks, four student labs, four standalone instructor solutions, and a second 20-point conceptual assessment with instructor key.
- Exact rational interval arithmetic, a small MPFR directed-rounding implementation, and an exact endpoint conversion layer for Arb.
- Natural and mean-value enclosures, derivative-sign bounds, uniform subdivision, and adaptive refinement with explicit success and budget outcomes.
- Exact inclusion checks, domain-error cases, conversion audits, and tests that subdivision retains complete coverage even when its target is unmet.
- Tucker reading references through §§3.1–3.3, course navigation, instructor pacing, and [a saved summary in Doc](Doc/interval_core_development.md).

Python uses short functions, explicit loops, and named intermediate bounds. Students implement interval operations and uniform subdivision; the adaptive search is supplied for audit to keep the introductory workload manageable. The teaching kernels support bounded intervals and a deliberately small operation set. Function and derivative evaluators must satisfy the stated enclosure assumptions.

## Third milestone: validation algorithms, Lectures/Labs 08–11

Implemented:

- Four lectures and student labs, four standalone instructor solutions, and a third 20-point concept check with key.
- Scalar dual numbers with interval and Arb component arithmetic, plus two-pass 2×2 Jacobians.
- Scalar interval Newton with root exclusion, strict inclusion certificates, recorded contraction/splitting decisions, and unresolved regions.
- Local 2×2 Krawczyk certificates with exact point preconditioners and an explicit contraction bound.
- One-dimensional branch-and-bound with feasible incumbents, strict pruning, minimum-value enclosures, and candidate unions retaining all minimizers.
- Known-root and known-minimum checks, multiple/boundary root limitations, near-singular system failure, tied minima, and budget outcomes.
- Updated reading map and pacing, plus [a saved summary in Doc](Doc/validation_algorithms_development.md).

The required system task is local certification; exhaustive box search remains optional. The root tolerance stops unresolved boxes and does not promise a target width for certified roots. Optimization stops on a value gap and does not promise tight localization. These distinctions are taught and retained in the result records.

## Fourth milestone: applications, capstone, and synthesis

Implemented:

- Lecture/Lab 12 on robust orientation, with Arb precision escalation and exact rational fallback for exact inputs.
- Lectures 13–14 on certificate audit, synthesis, project demonstrations, and wrapping with exact rational arithmetic.
- A student mirror-trajectory project and complete instructor model, a peer-audit notebook and worked audit, and a project rubric.
- A short SIAM-lattice trajectory certificate at time 3, checking all candidate mirrors, collision ordering, departure, and the final-time segment. Separate coordinate/distance width checks meet the 10^-20 target at 100 bits.
- Exact fraction JSON event export, approximate precision/sensitivity experiments, and low-precision, uncertainty, tangency, and budget-limit examples.
- Project notebook pairing and tagged starter-exercise checks, plus [a saved summary in Doc](Doc/applications_capstone_development.md).

The original SIAM time-10 answer, arbitrary mirror geometries, and tangent-event resolution remain extensions. A completed trajectory is distinct from meeting its accuracy target; incomplete runs report the last certified state only.

## Fifth milestone: final review and release

Implemented:

- Mathematical and teaching review of the arithmetic helpers, all notebook sources, and exercise/solution alignment, with simpler Python expressions and clearer assumptions.
- Regressions for incorrectly shaped 2×2 systems, literal constant Jacobian outputs, and mirror distance bounds when coordinates cross zero.
- Separate student and instructor ZIP editions, browser reading copies, internal link checks, and per-file SHA-256 manifests.
- Explicit release selection and output/metadata cleanup, keeping solutions, keys, instructor notes, development records, and local PDFs out of the student edition.
- Independent installations and fresh-kernel execution from the extracted editions; the package import and editable installation are checked against each extracted directory.

Release candidate: **1.0.0-rc1**. The [release review](Doc/release_review.md) records corrections, verification, distribution scope, and classroom-pilot priorities.

## Verification

Environment: Linux x86_64, CPython 3.12.9. Numerical stack: NumPy 2.5.3, Matplotlib 3.11.1, gmpy2 2.3.1, python-flint 0.9.0. Full installed dependency pins are in `requirements-lock.txt`.

- All 53 `.py`/`.ipynb` pairs pass structural and source-agreement checks.
- Completed lecture/setup and solution code is checked from independent fresh kernels in each notebook's own directory.
- The three Markdown-only concept checks and keys and the peer-audit form pass structural and source checks; they require no numerical execution.
- Student lab/project setup and demonstration cells are checked separately; unfinished exercises are intentionally skipped.
- Figure-producing cells must embed PNG output; a plain text Figure representation fails the execution check.
- 161 tests cover notebook workflow, rational and MPFR arithmetic inclusion across sign cases, input semantics, precision-context restoration, Arb conversion, and complete subdivision coverage. Additional checks cover derivative formulas, root retention and distinctness, system contraction/exclusion, pruning evidence, ties, boundaries, and budget-limited outcomes. Known analytic roots and minima provide independent references. Application checks cover determinant cancellation and input uncertainty, an analytically solved normal-incidence reflection, event ordering, reachable lattice bounds, unresolved trajectories, and exact endpoint export. Final-review regressions and release checks cover the corrections and distribution boundaries above.
- Package dependency consistency, editable installation without build isolation, and local course links are checked.

The computations are checked on the environment above. Cross-platform installation and classroom pacing have not been piloted. Tests support the specific implementations and examples; they are not formal verification of Python or the arithmetic libraries.

## Before classroom delivery

The planned core teaching material and release stage are complete. Pilot classroom pacing and review the lab/project workload before fixing deadlines. Verify installation on any additional operating systems used by students. No additional advanced methods are required for the introductory core.

Do not distribute `solutions/` with student materials. Local reference PDFs are not part of the teaching package's code or runtime requirements.
