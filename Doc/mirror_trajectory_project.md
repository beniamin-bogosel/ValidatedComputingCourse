# Project candidate: reliability amid chaos

**User-selected project candidate:** simulate a ray reflecting among circular mirrors in two dimensions, then investigate precision sensitivity and validate its trajectory.

## References

- *The SIAM 100-Digit Challenge*, **Chapter 2: Reliability amid Chaos**, pp. 33–46. In particular, **§2.3: Reliable Reflections**, pp. 41–43, develops interval verification. The PDF is in this directory.
- Related motivation supplied by the user: [Illustrating butterfly effect with a laser](https://www.youtube.com/watch?v=iTaSXto67WQ). Video contents were not independently reviewed; automated retrieval failed.

## Implemented introductory adaptation

The [student project](../projects/mirror_trajectory.ipynb) and instructor model in `solutions/mirror_trajectory_solution.ipynb` implement the core progression below. The required final time is **3**, with exact standard initial data and coordinate/distance enclosure widths at most **10^-20**. The model meets this target at 100-bit Arb precision and certifies three reflections, at centers (1,0), (−1,1), and (0,2).

Students complete the event-order selector and audit supplied collision/reflection code. A unit-speed displacement bound justifies the finite mirror list. Candidate intersections, departure from the current mirror, and the final-time comparison are checked explicitly. Completion and accuracy are separate tests; inconclusive runs report only their last certified state.

## Notebook progression

1. Plot or animate a short ray trajectory with ordinary floating-point arithmetic.
2. Compare the same exact initial conditions at several arithmetic precisions. Separately perturb the initial position or direction to distinguish computational error from sensitivity to input uncertainty.
3. Enclose the trajectory using rigorous arithmetic. Verify collision choices and ordering, as well as reflection calculations; following an unverified sequence of mirrors does not certify the path.
4. Return a final-position enclosure at a specified time, or an explicit inconclusive result when the method cannot resolve an event or meet the tolerance.

The original challenge uses unit speed, initial position `(1/2, 1/10)`, an eastward direction, mirrors of radius `1/3` centered at integer lattice points, and final time `10`. Its requested quantity is distance from the origin, so a full adaptation should also enclose that distance.

Begin with a shorter time horizon and supplied collision/plotting scaffolding. Treat the full challenge as an extension after roots, elementary geometry, and rigorous arithmetic have been taught. Precision escalation may reduce numerical uncertainty; it cannot remove a fixed physical uncertainty in the initial data. Handle near-tangencies and ambiguous event ordering explicitly.

**Learning goal:** connect a visually striking sensitivity experiment with a precise computational certificate. Agreement across precision settings alone is evidence, not a proof.

The model includes precision comparisons, perturbed and interval initial heights, tangency and collision-budget limitations, and an exact-fraction JSON event record. The [project rubric](../projects/README.md) budgets 12–18 hours including explanation, audit, and revision. See [the development summary](applications_capstone_development.md). The original time-10 answer is not claimed by this core adaptation.
