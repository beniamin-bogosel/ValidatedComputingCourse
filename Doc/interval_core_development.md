# Interval core: development summary

Saved for future course development. The course is introductory and notebook-first; code should remain explicit and readable. This block implements Lectures and Labs 04–07 and their instructor solutions.

## Teaching sequence

| Session | Main idea | Student work |
|---|---|---|
| 04 | Exact rational intervals separate the set argument from rounding | Implement multiplication, reciprocal, and sharp square; distinguish repeated variables from independent choices |
| 05 | Outward rounding preserves the inclusion argument on machine endpoints | Implement directed MPFR addition and multiplication; audit exact conversion to and from Arb |
| 06 | Exact arithmetic does not remove dependency overestimation | Compare equivalent formulas; implement uniform subdivision with full coverage; certify a transcendental sign |
| 07 | Derivatives and subdivision improve bounds | Implement mean-value and monotonicity bounds; audit adaptive coverage and stopping outcomes |

Each lecture contains theory, a proof argument, readable code, interpretation, and failure or inconclusive cases. Each lab has diagnostic checks and written questions. A separate 20-point conceptual assessment covers the block. Lecture and solution notebooks include executed outputs; starter exercises are deliberately incomplete.

## Implementation decisions

- `vc/intervals.py`: bounded intervals with `Fraction` endpoints. Decimal strings denote exact intended decimals; floats require explicit conversion. Empty intersection is `None`; division through zero is rejected. Square is distinct from multiplying two independent interval operands.
- `vc/mpfr_intervals.py`: a small teaching implementation of basic directed operations. Precision is explicit and mixed interval precisions are rejected. Local contexts restore the caller's settings. This is not a general interval standard implementation.
- `vc/arb_bridge.py`: domain geometry remains rational. Endpoint balls are combined by union; exact midpoint/radius fractions recover a guaranteed containing interval. Never route certified endpoints through float. Arb conversion can widen a domain, so function domain restrictions also apply to the expanded ball.
- `vc/enclosures.py`: short, explicit functions for covering subdivision, hulls, mean-value forms, monotonicity, and adaptive refinement. Evaluator and derivative inclusion are stated premises, not established by a return type.
- Adaptive success means every local image width meets the tolerance. The full function range can remain wide. Budget exhaustion retains a valid global enclosure; dropping difficult pieces would lose that guarantee.
- To keep the lab workload introductory, students implement uniform subdivision in Lab 06 and audit the supplied adaptive loop in Lab 07. Implementing that loop independently is an extension. The development plan records this choice.

## Sources and later use

Tucker §§2.1–2.2, §2.4, and §§3.1–3.3 supply the reading map. The trigonometric positivity example is Example 3.1.4. The polynomial range examples use elementary analytic reference ranges so enclosure claims can be inspected independently.

The SIAM book and mirror project remain later applications; no further book-wide analysis was needed. The mirror trajectory should distinguish numerical sensitivity from a certified collision sequence, with a short path as the core task. See [the project note](mirror_trajectory_project.md).

## Continuation

Next implement Lectures/Labs 08–11: scalar automatic differentiation, validated root isolation, small nonlinear systems, and global optimization. Reuse the exact domain intervals and Arb bridge. Keep mathematical hypotheses, coverage, and unresolved outcomes explicit. Do not introduce a large generic arithmetic framework.

See [development status](../DEVELOPMENT_STATUS.md) for verification and [instructor notes](../solutions/teaching_notes.md) for pacing. Classroom workload and cross-platform installation remain unpiloted.
