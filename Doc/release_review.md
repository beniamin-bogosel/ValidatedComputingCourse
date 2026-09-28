# Release review — 1.0.0-rc1

The core material has received a source review covering the numerical helpers, mathematical claims, all 53 notebook sources and corresponding exercises/solutions, plus student/instructor release boundaries. This is a reviewed teaching release candidate; classroom timing has not been piloted.

## Corrections from review

- The 2×2 system helpers now reject extra equations, rows, or columns. Previously they could silently ignore a third equation and certify the first two. A regression with `(x, y, 1)` prevents that false certificate.
- The two-pass Jacobian helper now gives zero tangents for literal constant output components while preserving its two-output contract.
- Mirror distance extraction uses sharp rational squares and enclosing square roots of nonnegative endpoints. This supports complete trajectories whose coordinate intervals cross zero.
- Approximate mirror exploration now rejects fractional precision or event-budget inputs.
- The project audit now checks the final candidate set and flight inequalities independently of the student's event selector, including empty, inconclusive, and touching-time diagnostics. The selector's trusted contract is explicit.
- Lecture wording clarifies residual bounds, smoothness hypotheses, and exact calculations versus floating-point plotting. Batch-boundary navigation and several compact Python expressions have been made clearer.

## Distribution design

The student edition contains public lectures, starters, assessments, project/audit materials, arithmetic/reference code, environment/workflow checks, selected source notes, and browser reading copies. It excludes worked solutions, keys, instructor notes, algorithm-answer tests, development records, local PDFs, caches, and the author's environment. All starter code outputs and execution counts are cleared; release metadata is restricted to teaching fields. Public `vc` algorithms remain available because lectures and later activities depend on them.

The instructor edition additionally contains the worked material, complete regression tests, development notes, build tooling, and the model mirror certificate. Each archive carries a SHA-256 manifest. HTML links are rewritten within the release and checked after export; notebook links are checked too. The primary reading format remains Jupyter. HTML mathematical typesetting uses the public MathJax CDN, while computations run offline after dependencies are installed.

The supported tested target is CPython 3.12 on Linux x86_64. The source package now requires Python 3.12+, consistent with the pinned NumPy requirement. Windows instructions use `py -3.12`; Windows, macOS, and other Python versions are not claimed tested. The temporary verification wheelhouse is host-specific and is not shipped in the course archives.

## Verification record

Verified on 2026-09-11 with CPython 3.12.9 on Linux x86_64 (glibc 2.39), using the pinned requirements. The authoring tree passes all 161 tests, all 53 notebook-pair checks, and full fresh-kernel execution. Review regressions and release checks are in `tests/`.

Each ZIP was extracted into its own directory and installed into a newly created virtual environment, without system site packages. Installation used the pinned dependency wheels and the extracted package. `pip check` passed in both environments. The interpreter, `vc.__file__`, and editable-install metadata all point to that edition's extracted directory.

| Check | Student edition | Instructor edition |
|---|---:|---:|
| Notebook pairs checked | 36 | 53 |
| Notebook runs passed in the clean installation | 32 | 49 |
| Environment/workflow or full regression tests passed | 11 | 161 |
| Templates checked structurally, without execution | 4 | 4 |

The run counts include Markdown-only assessments. Lecture and solution code runs fully; student labs and the project run setup and demonstrations while tagged exercises remain intentionally unfinished. Every notebook runs with a separate kernel and its own working directory. Figure-producing demonstrations must contain embedded PNG output.

Release audits check the file manifest, paired-source agreement, starter-output cleanup, and local links, including generated HTML. An independent student-archive review also checked for solution/key leakage, local PDFs, author paths, private metadata, and duplicate ZIP entries. Final documentation and HTML updates are audited again; their computational files are compared with the clean-tested editions. The updated release builder is separately regression-tested.

In the authoring workspace, installation and execution logs are retained under `build/release-verification/`. The two archives, archive checksums (`SHA256SUMS`), and machine-readable verification record (`verification.json`) are in `dist/`. These temporary environments and downloaded dependency wheels are excluded from both archives. To reproduce the checks, follow the edition's README installation steps, then run `python -m pytest`, `python scripts/notebooks.py check`, `python scripts/notebooks.py execute`, and `python scripts/check_links.py`.

## Classroom pilot still needed

Before fixing deadlines, pilot the 90–120 minute lecture plans, Labs 09/11 with their homework allocation, and the 12–18 hour capstone estimate. Set the actual calendar and communicate when students may consult public reference implementations. The mirror core is time 3; the original SIAM time-10 answer, general mirror arrangements, tangent-event resolution, verified ODEs, and exhaustive higher-dimensional systems remain outside the required core.

This review and its regression tests support the implemented computations. They are not formal verification of Python, the arithmetic libraries, or the course algorithms.
