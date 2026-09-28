# Applications and capstone: development summary

This milestone completed the planned core teaching material: Lectures 12–14, Lab 12, a scaffolded mirror project and instructor model, and student/worked peer-audit notebooks. The overall course has Lectures 01–14 and Labs 01–12. The subsequent [release review](release_review.md) records completion of packaging and verification; classroom piloting remains.

## New material

| Material | Main result |
|---|---|
| Lecture/Lab 12 | An orientation sign filter using Arb precision escalation and exact rational fallback |
| Lecture 13 | A worked audit of an omitted unresolved search region and an incorrect final-time trajectory claim |
| Lecture 14 | Claim synthesis, project demonstrations, and an exact rational wrapping experiment |
| Mirror project | A certified position and distance at time 3 in the SIAM lattice model, with explicit event ordering |
| Peer audit | A student review form and instructor example correcting an accuracy overclaim |

## Geometry

`vc/geometry.py` keeps exact rational coordinates distinct from interval measurements. The filter returns its sign, method, attempted precision/bound pairs, and the exact determinant when fallback is used. A zero-containing bound is inconclusive unless it is exactly [0,0]. Exact fallback decides exact rational input; it cannot replace a measured coordinate interval by its midpoint.

The cancellation example uses n=2^27, A=(0,0), B=(n,n−1), C=(n+1,n). All coordinates are exactly representable in binary64, but the computed determinant is zero while the exact value is one. This isolates arithmetic cancellation from input conversion.

## Mirror project

`vc/mirrors.py` validates a short ray trajectory using Arb enclosures. The geometry follows SIAM Chapter 2: radius 1/3 at every integer lattice center, initial position (1/2,1/10), eastward unit speed. The introductory horizon is **T=3**, not the original challenge's T=10.

The proof argument includes every part of event selection:

- Reflection preserves speed, so displacement by time T is at most T. Any colliding center is within T+radius of an allowed initial position in each coordinate. All lattice centers in that rectangle are enumerated.
- For each other mirror, the code verifies an outside start and either excludes a collision or encloses a positive simple entrance time. Tangent or otherwise undecided geometry is inconclusive.
- A selected collision must be strictly before all competitors and the remaining-time horizon. A final segment is accepted only when every candidate lies after that horizon.
- The actual contact point lies on the selected mirror. A positive reflected normal component proves departure, justifying omission of that same mirror on the next straight flight.
- Every subsequent position, velocity, and elapsed time is enclosed. Wrapping can make the calculation inconclusive without invalidating its earlier states.

At 100 bits, the standard short run certifies centers (1,0), (−1,1), and (0,2), then reaches T=3. Coordinate and distance widths meet the separate 10^-20 absolute-width target. The 24-bit run becomes inconclusive. A 53-bit run reaches T=3 but does not meet that target; the worked audit corrects this distinction.

`vc/mirror_exploration.py` supplies nearest-rounded MPFR trajectories for visual exploration at several precisions. They are explicitly approximations. Separately perturbing the initial height illustrates a different physical input. Interval-height runs preserve the full uncertainty; two allowed exact heights produce disjoint certified final-y enclosures in the short uncertainty experiment.

The model's JSON record in `build/certificates/mirror_t3.json` stores exact fraction endpoints, all per-mirror checks, collisions, final state, precision, and environment metadata. It supports inspection and reproduction; it is not a standalone formally verified proof object. On incomplete runs, position and elapsed time refer only to the last certified state, and final-distance extraction is rejected.

## Teaching and workflow

The student project asks for the event selector, analytic derivations, successful and limiting experiments, an event audit, and an exported record. The remaining collision code is supplied to keep the project introductory and readable. The expected 12–18 hours includes explanation, review and revision. The original longer SIAM challenge is an optional extension.

The notebook workflow now includes `projects/`, tags unfinished project cells as exercises, and checks/executes their setup separately from completed solutions. Instructor notebooks remain in `solutions/`. The peer audit explicitly distinguishes a supported claim from a missing proof condition, and a complete trajectory from a sufficiently narrow endpoint enclosure.

## Handoff at this milestone

Prepare separate student/instructor release bundles, verify their independent installation and notebook navigation, and pilot classroom pacing. Do not include local book PDFs in either release. Further ODE methods, arbitrary mirror geometries, tangent events, and exhaustive higher-dimensional searches remain outside the implemented introductory scope.
