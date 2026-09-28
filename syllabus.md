# Validated Computing — syllabus

Audience: Master's CS students with Python, elementary calculus, and basic linear algebra. Proposed schedule: 14 lectures of 90–120 minutes, 12 labs of about 2 hours, and project work. Exact timetable and assessment dates remain to be set.

The learning outcome is to formulate a numerical claim, construct and improve rigorous enclosures, implement validation methods, and state exactly what has been certified.

| Session | Topic | Lab / activity | Material status |
|---|---|---|---|
| 01 | Why validated computing? | Numerical crime scene; exact root certificate | Implemented |
| 02 | Floating-point representation and rounding | Spacing, input conversion, time-error model | Implemented |
| 03 | Error, conditioning, stability, cancellation | Polynomial and quadratic evaluation | Implemented |
| 04 | Mathematical interval arithmetic | Rational endpoint operations | Implemented |
| 05 | Machine intervals and directed rounding | MPFR kernel; introduction to Arb | Implemented |
| 06 | Interval extensions and dependency | Subdivision and range enclosure | Implemented |
| 07 | Better enclosures | Mean-value forms and adaptive subdivision | Implemented |
| 08 | Automatic differentiation | Scalar dual numbers and derivative bounds | Implemented |
| 09 | Validated roots | Root isolation with unresolved outcomes | Implemented |
| 10 | Small nonlinear systems | Local certification in two dimensions | Implemented |
| 11 | Global optimization | One-dimensional branch-and-bound | Implemented |
| 12 | Application studio | Robust geometry; optional alternatives | Implemented |
| 13 | Capstone workshop | Reproduction and certificate audit | Implemented |
| 14 | Synthesis and demonstrations | From numerics to computer-assisted proof | Implemented |

## Assessment proposal

- Labs: 40%, collected in portfolios 01–03, 04–06, 07–09, and 10–12.
- Short conceptual tests: 20%.
- Capstone project: 30%.
- Demonstration and peer audit: 10%.

Lab grading rewards the mathematical interpretation alongside implementation and outputs. A correctly reported inconclusive result is preferable to an unsupported success claim. First portfolio: submit Labs 01–03 with the specified written responses and completed diagnostic checks. The [first concept check](assignments/concept_checks_01_03.ipynb) covers this block. A [second concept check](assignments/concept_checks_04_07.ipynb) covers the interval core through session 07. A [third concept check](assignments/concept_checks_08_11.ipynb) covers differentiation and validated algorithms through session 11.

Projects are introduced in session 07, proposed in 09, demonstrated provisionally in 11, and audited in 13. Allow approximately 12–18 hours per student, with late-semester independent work shifted toward the project. The implemented [mirror-trajectory project](projects/mirror_trajectory.ipynb) adapts SIAM Challenge Chapter 2 to final time 3; the original time-10 problem is optional. See the [project rubric](projects/README.md), [peer-audit form](assignments/peer_audit.ipynb), and [source/scope note](Doc/mirror_trajectory_project.md).

See [references](references.md) and the [detailed plan](COURSE_PLAN.md) for topic scope, prerequisites, and development milestones.

