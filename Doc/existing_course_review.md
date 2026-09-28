# Existing validated numerics course: review and reuse notes

Reviewed: 2026-09-11.

## Source and scope

Local source directory: `/home/beni/Courses/ValidatedNumerics`.

Course title: **Computer-assisted proofs in nonlinear analysis**. The saved page lists Jan Bouwe van den Berg, Maxime Breden, Olivier Hénot, Jean-Philippe Lessard, and Jason D. Mireles James as authors.

Material inspected:

- Finite-dimensional problems — local Pluto source `finite_dimension_lecture_notes_89e4e102.jl` in the directory above (not included in course releases).
- The accompanying saved HTML page, including its rendered outputs and course navigation.

Only the finite-dimensional lecture is available locally as substantive teaching material. The navigation lists further modules on algebraic equations, Taylor integration, periodic orbits, and invariant manifolds of equilibria, including the parameterization method and Lorenz system. It also links exercises, but those exercise texts and later modules were not available locally and have not been reviewed. The Julia notebook was read, not executed.

## Assessment for our intended audience

**Use this as an advanced reference and source of selected examples. Its opening sequence is too steep to use directly as the introduction for our planned Master's CS audience.**

The difficulty comes from mathematical prerequisites and pacing. Translating Julia to Python would leave that difficulty largely intact. The lecture explicitly explains that its general framework is intended to extend to infinite-dimensional problems.

Its opening progression is:

1. Explore the logistic map and introduce the period-three-implies-chaos theorem.
2. State a contraction theorem in a Banach space using derivative/operator bounds.
3. Derive a Newton–Kantorovich criterion involving an approximate inverse and constants `Y`, `Z₁`, and `Z₂`.
4. Give a brief introduction to interval arithmetic and input conversion.
5. Use rigorous bounds to prove the existence of a period-three orbit.

Students must therefore encounter chaos, fixed-point reformulation, Banach spaces, derivatives of vector-valued maps, operator norms, approximate inverses, and radius inequalities before gaining much experience with interval arithmetic. Those are substantial simultaneous demands for students assumed to know only elementary calculus and linear algebra.

This is a judgment about suitability for our course. The inspected material has a coherent purpose as preparation for more advanced computer-assisted proofs.

## What the worked example accomplishes

For the logistic map with parameter exactly `39/10`, the lecture formulates a period-three orbit as a zero of a three-variable system. It computes an approximate zero and approximate inverse using ordinary floating-point arithmetic, then evaluates rigorous bounds for a Newton-like fixed-point map.

The radius inequalities establish a nearby locally unique solution. The lecture also addresses injectivity of the preconditioner and checks that the three coordinate enclosures are disjoint, supporting the claim of genuine period three rather than a fixed point.

This is a valuable example of the complete sequence: mathematical claim, numerical candidate, rigorous verification, and interpretation of what has actually been proved. The final disjointness check is particularly useful pedagogically: solving an auxiliary equation is not always sufficient to establish the original claim.

## Material worth adapting

| Material | Proposed place in our course | Adaptation |
|---|---|---|
| Notebook narrative alternating mathematics and code | All lectures | Preserve the integrated teaching format in Python/Jupyter |
| Ordinary search followed by rigorous verification | Introduction, roots, systems, capstones | Make the distinction explicit without introducing the full fixed-point framework immediately |
| Typed decimal versus stored float | Lectures 02 and 05 | Use `Fraction`, MPFR, and Arb input examples |
| Logistic map experiment | Optional short motivation in 01 or 03 | Show sensitivity; do not require a theorem about chaos |
| A single mathematical problem developed through to a certificate | Lectures 09–12 | Start with scalar roots or a geometric predicate |
| Approximate inverse followed by rigorous validation | Lecture 10 | Use one supplied 2×2 example and explain the needed matrix concepts locally |
| Period-three orbit certificate | Optional capstone or final demonstration | Revisit after scalar root finding and systems; supply substantial scaffolding |
| Auditing the gap between an auxiliary solution and the original claim | Lecture 13 | Ask students to identify and verify any missing conditions |

Keep abstract Banach-space statements, general Newton–Kantorovich/radii-polynomial machinery, infinite-dimensional extensions, invariant manifolds, and rigorous dynamical-systems computations outside the required introductory sequence.

## Implications for our course plan

Retain the progression in [COURSE_PLAN.md](../COURSE_PLAN.md):

```text
floating-point behavior and error
→ interval sets and endpoint operations
→ outward rounding
→ dependency and better enclosures
→ scalar root certificates
→ small systems and global optimization
→ applications and certificate auditing
```

The existing plan is itself ambitious in weeks 08–11. Protect its introductory level by enforcing these scope limits during authoring:

- One central new mathematical idea per lecture, supported by a concrete example and short proof.
- Scalar AD is the required implementation; general Jacobian machinery is scaffolded.
- Root-isolation labs use selected simple-root problems and supplied search infrastructure. Difficult or multiple roots may remain explicitly unresolved.
- Systems require local certification in dimension two; exhaustive system solving is optional.
- Optimization starts in one dimension with supplied queue and plotting utilities.
- Each week has one core implementation task; advanced extensions do not silently become required prerequisites for the next lab.

A suitable introductory success criterion is that students can explain and implement a rigorous enclosure, a scalar existence/uniqueness test, and a simple global coverage argument, then identify exactly what their output certifies. Generality beyond that can grow through projects.

## Cautions when reusing the source

The saved notebook ends by noting automatic numeric conversions, and its rendered `isguaranteed` check reports `false, false, true` for the three bounds. This is a reason to inspect conversion semantics before reusing the computation; it is not, by itself, a conclusion that the mathematical result is false. Any Python adaptation should explicitly specify input semantics and revalidate every proof condition.

There is also a small norm-notation issue in the displayed derivation of `Z₂`: for its diagonal Jacobian difference, the induced matrix 1-norm involves the maximum absolute coordinate difference. Bounding it by the vector 1-norm gives an inequality, whereas the source writes equality at that step. The proposed upper bound can still follow with the inequality. Re-derive such estimates when adapting them.

Preserve attribution for adapted ideas and examples. This review records the local snapshot; it does not assess current package behavior, exercise difficulty, or the uninspected modules. Tucker's PDF is now present in `Doc/`; it was not examined as part of this review.
