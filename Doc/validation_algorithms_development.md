# Validation algorithms: development summary

Lectures/Labs 08–11 extend the introductory notebook course from interval enclosures to computational certificates. Each topic includes theory and proof conditions, visible Python, worked examples, a student lab, an instructor solution, and inconclusive cases. A third 20-point conceptual assessment covers the block.

## Sequence and scope

| Session | Implemented material | Deliberate scope boundary |
|---|---|---|
| 08 | Scalar dual numbers, arithmetic/chain rules, rational and interval derivatives, Arb elementary functions, two-pass Jacobians | First derivatives only; no branch analysis or large generic AD framework |
| 09 | Sign bracketing, interval Newton, exclusion, strict inclusion certification, recorded contractions and subdivisions | Multiple and boundary roots may remain unresolved; root accuracy refinement is separate from search tolerance |
| 10 | Explicit 2×2 matrix operations, point preconditioning, Krawczyk image, infinity-norm contraction bound | Local box certification; exhaustive system search remains an extension |
| 11 | Feasible incumbent, lower bounds, strict pruning, branch-and-bound, minimum enclosure, retained minimizer union | One-dimensional compact domains; value-gap stopping does not promise location accuracy |

## Code and certificate records

- `vc/autodiff.py`: short `Dual` methods expose each derivative rule. Its component arithmetic determines whether results are approximate or enclosing. The two-pass Jacobian helper keeps row/output and column/input conventions visible.
- `vc/roots.py`: `RootDecision` records the original domain, image, derivative interval, Newton image, retained interval, and action. `RootSearch` returns certificates, unresolved intervals, and the decision history. Budget exhaustion retains all pending intervals. Contraction preserves all roots, not a literal cover of non-root points. Strict interior certification is intentionally conservative.
- `vc/systems.py`: a certificate stores the box, midpoint, exact point preconditioner, Jacobian and residual bounds, remainder matrix, Krawczyk image, and norm bound. Nonsingularity of the preconditioner is checked exactly. NumPy may propose a matrix, but each float is explicitly interpreted as its exact stored rational before verification.
- `vc/optimization.py`: `MinimumResult` contains the minimum-value interval, feasible witness and its value enclosure, candidate minimizer boxes, pruned-box evidence, split count, and stopping status. Pruning is strict (`lower > incumbent`) to preserve tied minimizers. Retained and pruned terminal boxes together cover the original domain.

The lab scaffolds leave the mathematically essential steps to students: product and reciprocal differentiation, interval Newton classification, the Krawczyk image and decision, and optimization pruning/stopping/child handling. Support code uses plain loops and named quantities. No solution notebook is a runtime dependency of another notebook.

## Examples and evidence

The cubic `(x+2)(x-1)(x-3)` on `[-3,4]` supplies three known roots for an independent completeness check. The multiple root of `x²` and the boundary root of `x` on `[0,1]` illustrate unresolved outcomes.

The circle/line system has independently known roots with coordinates ±1/√2. A nearly singular system has exactly zero midpoint residual while containing two distinct nearby roots; the uniqueness test correctly fails. This exposes why a residual is insufficient.

The polynomial `x⁴−2x²` on `[-2,2]` has minimum −1 at both −1 and 1. Natural and combined mean-value enclosures produce the same minimum guarantee with different split counts. Tied, constant, and boundary objectives check the meaning of pruning and stopping. Known analytic answers support the tests but are not substituted into the search algorithms.

## Reading and continuation

Tucker §4.1 and selected §§5.1–5.2 support the reading map. Lecture 09 proves its scalar C¹ interval Newton criterion directly. Lecture 10 uses an explicit contraction argument; Rump's 2010 *Verification methods* survey §13 is optional instructor background for the multivariate setting. No further full-book analysis of the SIAM source was needed.

Next develop the application studio and model capstone: robust orientation predicates, a short mirror trajectory with explicit collision decisions, and reproducibility/peer-audit material. Keep the SIAM Chapter 2 challenge as motivation and an optional extension beyond the introductory mirror project. Later packaging must separate student and instructor materials.

See [development status](../DEVELOPMENT_STATUS.md) for final verification. Classroom pacing and cross-platform installation still need piloting.
