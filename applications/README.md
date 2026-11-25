# Applications for Lectures 07–14

Worked application notebooks, one per lecture from 07 to 13, plus a document that proposes these and further applications, with teaching notes, an instructor key for the audit notebook, and alternative capstones.

| Lecture | Notebook | Application |
|---|---|---|
| 07 | [app07_approximation_error](app07_approximation_error.ipynb) | Certified error of a math-library polynomial for sin |
| 08 | [app08_network_robustness](app08_network_robustness.ipynb) | Robustness certificate for a small neural network |
| 09 | [app09_ray_tracing_and_wilkinson](app09_ray_tracing_and_wilkinson.ipynb) | First hit of a ray with a torus; all roots of Wilkinson's polynomial |
| 10 | [app10_robot_arm_and_henon](app10_robot_arm_and_henon.ipynb) | Robot arm reaching a whole path; Hénon periodic orbits |
| 11 | [app11_curve_fitting](app11_curve_fitting.ipynb) | Global frequency fit; aliasing found by the certificate |
| 12 | [app12_convex_hull](app12_convex_hull.ipynb) | A convex hull that leaves an input point outside |
| 13 | [app13_seeded_audit](app13_seeded_audit.ipynb) | Audit of four seeded certificates (key in the PDF, Appendix A) |

Document: [applications.pdf](applications.pdf) (source: `tex/applications.tex`).

The `.py` files (Jupytext percent format) are the editable sources. To rebuild everything from the course root:

```bash
.venv/bin/python applications/build.py            # sync, execute, extract figures, compile PDF
.venv/bin/python applications/build.py execute app09
```

`build.py` puts the repository root on `PYTHONPATH`, so `vc` is importable even without an editable install. The PDF's figures come from notebook cells tagged `tex-figure-<name>`. The Appendix A key reveals the answers to `app13`, so keep the PDF out of student distributions if that notebook is assigned.
