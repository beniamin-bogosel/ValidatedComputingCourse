# Validated Computing — student edition

A notebook-first introduction for Master's students in computer science. The course includes 14 lectures, 12 labs, three concept checks, and a short mirror-trajectory project. You need basic Python, elementary calculus, and basic linear algebra.

Start with [00 · Setup](notebooks/00_setup.ipynb), then follow [the syllabus](syllabus.md). [The reading index](reading/index.html) contains browser copies; mathematical typesetting in those HTML copies loads MathJax from its public CDN. Jupyter notebooks provide the primary reading and working format, and computations need no network after installation.

## Course navigation

{{COURSE_TABLE}}

[Concept check 01–03](assignments/concept_checks_01_03.ipynb) · [Concept check 04–07](assignments/concept_checks_04_07.ipynb) · [Concept check 08–11](assignments/concept_checks_08_11.ipynb) · [References](references.md)

**Capstone:** [Mirror trajectory](projects/mirror_trajectory.ipynb) · [Requirements and rubric](projects/README.md) · [Peer audit](assignments/peer_audit.ipynb).

## Install and start

The tested environment is CPython 3.12 on Linux x86_64. Run these commands from this extracted folder:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements-lock.txt
python -m pip install --no-deps --no-build-isolation -e .
python -m ipykernel install --sys-prefix --name validated-computing --display-name "Python (Validated Computing)"
python -m pip check
python -m pytest -q
jupyter lab
```

On Windows, use `py -3.12 -m venv .venv` and activate with `.venv\Scripts\Activate.ps1` in PowerShell. Windows and macOS have not been tested for this release. If the Linux dependency snapshot is unavailable for your platform, use `python -m pip install -e ".[dev]"` and run the checks above; record that environment separately.

Choose **Python (Validated Computing)** in Jupyter or the project's `.venv` interpreter in VS Code. Run the setup notebook before starting the course. The editable installation lets notebooks import `vc` from their own folders. There is no dependency on the author's workspace or local book PDFs.

## Work through a lab or project

Read the preparation lecture, predict an outcome, and complete the cells tagged as exercises. Some starter functions deliberately raise `NotImplementedError`. Run their diagnostic cells after implementing the task, write the requested explanations, then restart the kernel and run every cell before submitting.

The public `vc` package supplies reviewed reference algorithms used by lectures and later activities. Follow the instructor's guidance on when to consult them during an implementation task. Passing diagnostics does not replace the mathematical argument. This edition contains no worked lab solutions, assessment keys, or instructor notes.

The automatic starter check skips exercise cells:

```bash
python scripts/notebooks.py check
python scripts/notebooks.py execute
python scripts/check_links.py
```

This checks setup and supplied demonstrations, not your completed answers. For a completed submission, run all cells in Jupyter from a fresh kernel. If the automatic execution environment blocks local sockets, use Jupyter in an environment that permits a local kernel.

## Editing paired notebooks

Each `.ipynb` has a Jupytext `.py` partner. Edit one representation at a time. After editing in Jupyter, run `python scripts/notebooks.py sync --from ipynb`; after editing text, use `sync --from py`. Synchronization intentionally clears old outputs when the source changes.

The release manifest records the distributed file hashes. Your edits will change them; keep an untouched copy if you need to compare with the original release.
