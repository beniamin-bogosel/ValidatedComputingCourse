# Instructor notes — pacing, assessment, and review

The lecture notebooks carry the teaching narrative. These notes describe pacing and marking rather than duplicating the theory.

| Session | Suggested core pacing | If time is short |
|---|---|---|
| 01 | 15 min predictions; 20 min claims/error sources; 15 min exact inputs; 25 min root certificate; 15 min discussion | Keep the Patriot reference to a few minutes; prioritize the distinction between sign evidence and theorem |
| 02 | 20 min representation; 25 min spacing/rounding; 20 min special values; 15 min input conversion; 20 min time-error model | Move the plot or time-model derivation to the lab |
| 03 | 20 min error/conditioning; 25 min polynomial; 15 min rationalization; 25 min quadratics; 20 min summation | Rump/MPFR and finite differences are explicitly optional |

The 03 notebook is deliberately richer than one lecture. Do not try to cover every extension in a two-hour session. Pilot the first block before fixing workload expectations for later weeks.

## Lab marking

Suggested rubric for each lab: 40% correct implementation and relevant diagnostics; 40% mathematical explanation and precisely scoped conclusions; 20% reproducibility and interpretation of failure cases. Exact arithmetic checks provide evidence for the particular computations, not universal correctness of a program.

Look especially for these misunderstandings:

- Comparing a float with another float expression does not test equality with the intended rational.
- Small residual, sample positivity, and agreeing digits do not supply missing existence or coverage arguments.
- Unit roundoff and machine epsilon have distinct definitions in this course.
- Factoring can improve evaluation while the function remains ill-conditioned with respect to uncertain data.
- A Decimal reference is an approximation unless a bound is independently justified.
- A strict sign-bracketing test can fail on an interval containing roots; failure is not exclusion.

The solution notebooks give sample written responses and execute all diagnostic cells. The concept-check key includes point allocations. Keep this directory out of student releases.


## Interval core: sessions 04–07

| Session | Suggested core pacing | If time is short |
|---|---|---|
| 04 | 20 min interval sets; 30 min arithmetic and proofs; 20 min reciprocal/square; 25 min composition and dependency | Assign hull/intersection discussion as preparation |
| 05 | 20 min inward-rounding counterexample; 30 min directed operations; 20 min precision/input semantics; 25 min Arb conversion | Read the complete MPFR class after class; inspect addition live |
| 06 | 25 min equivalent formulas; 20 min inclusion; 30 min covering subdivision; 25 min Arb positivity | Use the plotted example as supplied code; focus on coverage proof |
| 07 | 30 min mean-value proof; 20 min intersection and failure case; 20 min monotonicity; 30 min adaptive stopping | Make the transcendental mean-value example optional |

Lab 04 supplies constructor/addition/subtraction so students focus on three formulas. Lab 05 exposes both directed product lists deliberately. Lab 06 asks students to implement subdivision; Lab 07 supplies the adaptive loop for inspection so the core task remains feasible in roughly two hours. An independent implementation of that loop is an extension. These timings are proposals and need classroom piloting.

Apply the same 40/40/20 rubric. Require an explanation of the following distinctions:

- An exact interval operation can still discard a repeated-variable dependency.
- Outward conversion is part of the certificate; a decimal display is not the exact endpoint.
- An empty intersection is not the singleton zero; a zero-containing image is generally inconclusive about roots.
- A derivative bound covers the whole interval; a midpoint derivative alone is inadequate.
- A centered form can be wider than a natural form, and its changing center need not preserve inclusion isotonicity.
- Every retained domain piece matters to a global range claim, including when the search budget runs out.
- Local image-width success does not mean the global range has that width.

The second conceptual assessment is 20 points and should take 30–40 minutes. Worked solutions give independent explanations as well as executable checks. Do not distribute this directory with student materials.

## Validation algorithms: sessions 08–11

| Session | Suggested core pacing | If time is short |
|---|---|---|
| 08 | 15 min finite differences; 30 min dual rules; 25 min interval inclusion; 20 min Jacobian columns; 15 min branch limitations | Make the Arb experiment a supplied demonstration |
| 09 | 20 min four root claims; 30 min interval Newton proof; 30 min search invariant; 25 min failure and budget cases | Move repeated root-enclosure refinement to homework |
| 10 | 20 min box/Jacobian; 30 min fixed-point derivation; 25 min contraction proof; 25 min examples and local scope | Supply the NumPy proposal and matrix loops |
| 11 | 25 min lower/upper bounds; 25 min pruning invariant; 25 min loop and comparison; 25 min audit and failure cases | Treat stationary-point pruning as an extension |

Labs 08 and 10 are intended for about two hours. Labs 09 and 11 may require 30–60 minutes of homework beyond the lab, especially for written audits. Students fill small mathematical operations or defined gaps in supplied search scaffolds, rather than building data structures from scratch. These timings remain unpiloted.

Use the established 40% implementation/diagnostics, 40% mathematical explanation, 20% reproducibility/failure interpretation rubric. Pay particular attention to:

- Float AD still rounds; interval AD needs differentiability and inclusion throughout the domain.
- Derivative bounds excluding zero establish at most one root. Existence needs a separate argument.
- Root search tolerance stops unresolved small boxes and is not a guaranteed certified-root width.
- Root contraction preserves the possible root set; a record is needed to justify portions removed from the search.
- Boundary roots can appear in adjacent closed boxes. Any future endpoint certification rule must address distinctness before counting.
- The taught Krawczyk test explicitly checks both strict box inclusion and a contraction norm below one, as well as nonsingularity of the chosen point preconditioner.
- A failed sufficient system test is inconclusive; an exact zero residual does not prove uniqueness in a surrounding box.
- A local system certificate says nothing about roots elsewhere without a global argument.
- A feasible value enclosure supplies an incumbent through its upper endpoint. Strict pruning is needed to preserve all minimizers, including ties.
- A value-gap certificate does not promise small candidate domains. Budget outcomes retain the guarantees stated by their records.

The third 20-point concept check should take 35–45 minutes. Its key emphasizes hypotheses and the exact scope of each conclusion. Do not distribute instructor solutions or these notes with the student bundle.

## Application and capstone block: sessions 12–14

| Session | Suggested pacing | Instructor emphasis |
|---|---|---|
| 12 | 20 min determinant sign; 25 min cancellation/filter; 20 min fallback and uncertain data; 25 min capstone planning | Exact inputs and measured sets are different problems |
| 13 | 25 min omitted-root-region audit; 15 min mirror scope failure; 45–60 min peer workshop | Reproduction alone does not establish the mathematical claim |
| 14 | 20 min synthesis; 20 min exact wrapping; remaining time for concise demonstrations | State supported conclusions and respond to audit findings |

Lab 12 takes about 90 minutes. The capstone uses supplied collision arithmetic, with students completing the event selector and explaining the proof obligations. Allocate 12–18 hours across the project, including experiments, written justification, audit, and revision. The exact initial data and T=3 target should be completed before attempting a longer horizon. Classroom pacing remains unpiloted.

The mirror model must account for candidate mirror enumeration, intersection decisions, time ordering, the remaining-time comparison, and departure from the last mirror. A plausible collision plot or agreeing precision runs is not enough. The `complete` status certifies reaching the horizon; explicit width assertions certify the separate accuracy target. Incomplete results are at the last certified elapsed time, not the requested final time.

The driver trusts the student's event selector. Its correctness is a premise of the full trajectory claim, so check its inconclusive, touching-time, and empty-candidate cases as well as successful collisions. The project audit checks the final flight directly from recorded bounds, without asking the same callback to approve its own decision again. Passing these examples does not establish the callback's all-input correctness; require the event-order argument too.

Use `solutions/mirror_trajectory_solution.ipynb` as the model computation and `solutions/peer_audit_solution.ipynb` as a worked review exercise. The latter deliberately contrasts a completed 53-bit run with the corrected 100-bit accuracy claim; it is not an actual external peer review. The project rubric is in `projects/README.md`.

In the final discussion, the rotation example isolates wrapping from rounding error using exact fractions. Distinguish implementation testing and numerical certification from formal software verification. The class has not implemented ODE validation, arbitrary billiard arrangements, or the original time-10 SIAM answer.
