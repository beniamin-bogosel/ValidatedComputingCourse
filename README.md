# Validated Computing

A Python/Jupyter introduction for Master's students in computer science. The course moves from floating-point behavior to rigorous enclosures and computational certificates. Theory, proofs, experiments, and interpretation live in the lecture notebooks; labs are separate notebooks.

Release candidate **1.0.0-rc1** includes setup, Lectures 01–14, Labs 01–12, instructor solutions, three conceptual assessments, and a scaffolded mirror-trajectory capstone with peer audit. Mathematical and teaching review and clean-environment verification are complete; classroom pacing still needs a pilot. The schedule is in [the syllabus](syllabus.md); [the development plan](COURSE_PLAN.md) records scope decisions.

## Start here

| Material | Notebook | Lab | Lecture Notes |
|---|---|---|---|
| Environment and arithmetic smoke checks | [00 · Setup](notebooks/00_setup.ipynb) | Ungraded | — |
| Approximation, evidence, and certificates | [01 · Why validated computing?](notebooks/01_intro.ipynb) | [Lab 01](labs/lab01_intro.ipynb) | [PDF 01](PDF_Lectures/lecture01_certificates.pdf) |
| Representation, spacing, and rounding | [02 · Floating-point arithmetic](notebooks/02_floating_point.ipynb) | [Lab 02](labs/lab02_floating_point.ipynb) | [PDF 02](PDF_Lectures/lecture02_floating_point.pdf) |
| Error, conditioning, and cancellation | [03 · Stability](notebooks/03_stability.ipynb) | [Lab 03](labs/lab03_stability.ipynb) | [PDF 03](PDF_Lectures/lecture03_stability.pdf) |
| Exact interval sets and operations | [04 · Interval basics](notebooks/04_interval_basics.ipynb) | [Lab 04](labs/lab04_interval_basics.ipynb) | [PDF 04](PDF_Lectures/lecture04_interval_arithmetic.pdf) |
| Machine bounds and Arb conversion | [05 · Directed rounding](notebooks/05_directed_rounding.ipynb) | [Lab 05](labs/lab05_directed_rounding.ipynb) | [PDF 05](PDF_Lectures/lecture05_outward_rounding.pdf) |
| Dependency and covering subdivisions | [06 · Dependency](notebooks/06_dependency.ipynb) | [Lab 06](labs/lab06_dependency.ipynb) | [PDF 06](PDF_Lectures/lecture06_dependency_subdivision.pdf) |
| Derivatives and adaptive bounds | [07 · Better enclosures](notebooks/07_better_enclosures.ipynb) | [Lab 07](labs/lab07_better_enclosures.ipynb) | [PDF 07](PDF_Lectures/lecture07_better_enclosures.pdf) |
| Derivatives through expression rules | [08 · Automatic differentiation](notebooks/08_automatic_differentiation.ipynb) | [Lab 08](labs/lab08_automatic_differentiation.ipynb) | [PDF 08](PDF_Lectures/lecture08_automatic_differentiation.pdf) |
| Exclusion, roots, and search completeness | [09 · Validated roots](notebooks/09_validated_roots.ipynb) | [Lab 09](labs/lab09_validated_roots.ipynb) | [PDF 09](PDF_Lectures/lecture09_validated_roots.pdf) |
| Local existence and uniqueness in a box | [10 · Nonlinear systems](notebooks/10_nonlinear_systems.ipynb) | [Lab 10](labs/lab10_nonlinear_systems.ipynb) | [PDF 10](PDF_Lectures/lecture10_nonlinear_systems.pdf) |
| Minimum bounds and all minimizers | [11 · Global optimization](notebooks/11_global_optimization.ipynb) | [Lab 11](labs/lab11_global_optimization.ipynb) | [PDF 11](PDF_Lectures/lecture11_global_optimization.pdf) |
| Reliable geometric decisions | [12 · Robust geometry](notebooks/12_robust_geometry.ipynb) | [Lab 12](labs/lab12_robust_geometry.ipynb) | [PDF 12](PDF_Lectures/lecture12_robust_geometry.pdf) |
| Reproduction, assumptions, and coverage | [13 · Certificate audit](notebooks/13_certificate_audit.ipynb) | [Peer audit](assignments/peer_audit.ipynb) | [PDF 13](PDF_Lectures/lecture13_certificate_audit.pdf) |
| Scope, limitations, and demonstrations | [14 · Synthesis](notebooks/14_synthesis.ipynb) | Project demonstrations | [PDF 14](PDF_Lectures/lecture14_synthesis.pdf) |

[Concept check 01–03](assignments/concept_checks_01_03.ipynb) · [Concept check 04–07](assignments/concept_checks_04_07.ipynb) · [Concept check 08–11](assignments/concept_checks_08_11.ipynb) · [Reading references](references.md)

**Capstone:** [Mirror trajectory notebook](projects/mirror_trajectory.ipynb) · [Project requirements and rubric](projects/README.md). The core target is a certified short path to time 3; the original SIAM time-10 challenge remains an extension.

## Installation

**Google Colab:** the original notebooks now include a setup cell before their first course import. Upload `notebooks/00_setup.ipynb` to Colab, run its first code cell, and select the root-level `vc_runtime.zip` when prompted. The same setup is included in the separate Colab editions. It loads `vc` and installs the arithmetic libraries; locally it skips Colab setup. See [the Colab guide](COLAB.md) for upload, saving, and export instructions. The original local-Jupyter workflow below is unchanged.

Use Python 3.12 for the tested environment. The package requires Python 3.12 or later; the dependency snapshot was verified with CPython 3.12.9 on Linux x86_64 (glibc 2.39). Other Python versions and operating systems require their own verification. No GPU is required. Run from the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m pip install --no-deps --no-build-isolation -e .
python -m ipykernel install --sys-prefix --name validated-computing --display-name "Python (Validated Computing)"
jupyter lab
```

On Windows, create the environment with `py -3.12 -m venv .venv`, then activate with `.venv\Scripts\Activate.ps1` in PowerShell. If platform-specific pins are unavailable, install from `python -m pip install -e ".[dev]"`, then run the checks below and record that environment separately. The lock records a tested environment, not a guarantee of identical behavior on every machine.

In VS Code, select `.venv` or **Python (Validated Computing)** as the notebook kernel. Run `00_setup.ipynb` first. The editable package installation makes `vc` available even when the notebook's working directory is `notebooks/` or `labs/`.

Lecture notebooks and solutions include checked outputs for reading. Re-run them in your own environment. Once dependencies are installed, their computations do not need internet access. External readings are links, and the reference PDFs are optional local resources rather than runtime dependencies.

## Labs and instructor material

In labs and student projects, complete the cells marked as exercises and then run their diagnostic checks. Some stubs deliberately raise `NotImplementedError` when called. Automated starter checks execute setup and demonstrations only; completed submissions and instructor solutions should run every cell from a fresh kernel.

The `solutions/` directory contains complete instructor notebooks and the conceptual-test key. Keep it out of student distributions. Lecture examples are public teaching material; lab solutions and marking guidance are instructor material. The PDFs under `Doc/` are local reading resources and are excluded from version control.

## Editing and checking notebooks

Each notebook has a Jupytext `.py` partner with `# %%` cell boundaries. Both formats are part of the teaching package. Edit one representation at a time, then explicitly choose the source for synchronization:

```bash
python scripts/notebooks.py sync --from py
python scripts/notebooks.py check
python scripts/notebooks.py execute
python -m pytest
python scripts/check_links.py
```

If you edited `.ipynb` in Jupyter, use `sync --from ipynb` instead. Synchronization from text preserves saved outputs only when every cell's source and tags are unchanged; otherwise outputs are cleared to avoid stale results. Execution writes fresh outputs to the `.ipynb` files. It uses the current Python interpreter, starts an independent kernel for each notebook, and runs from each notebook's own directory.

`execute` runs lecture and solution code fully, and skips only tagged exercise cells in student labs and projects. Markdown-only assessments and the peer-audit form need no computation. Templates are checked structurally. Local Jupyter sockets must be permitted by the execution environment.

For a readable browser copy of a notebook, after execution:

```bash
jupyter nbconvert --to html --output-dir build/html notebooks/03_stability.ipynb
```

## Authoring conventions

- Alternate theory and experiments; state the assumptions supporting each mathematical claim.
- Use exact input descriptions. Label high-precision approximations as approximations unless a bound is justified.
- Keep essential algorithms visible in notebooks; use `vc` for shared infrastructure.
- Write short, explicit Python functions with named intermediate values. Prefer plain loops and visible formulas to compact tricks.
- Add a failure or inconclusive case, short checkpoints, and precise reading references.
- Use [the templates](templates/) for lectures, labs, projects, and audits.
- Measure runtime and review workload before assigning extensions as required work.

## Release packages

Build separate student and instructor editions after fresh-kernel execution:

```bash
python -m scripts.release build
```

The ZIP archives appear in `dist/`. Each has its own installation guide, notebook pairs, browser reading index, and SHA-256 manifest. Student starters have all outputs cleared; worked solutions, assessment keys, instructor notes, and development records are excluded. The public `vc` reference implementations remain available for lectures and later activities.

The primary format is Jupyter. Generated HTML reading copies embed figures and use the public MathJax CDN for mathematical typesetting. No book PDFs or author environment are included in either archive.

See [the release review](Doc/release_review.md) for changes, validation, and remaining classroom-pilot work.
