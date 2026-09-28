# Capstone projects

The [mirror trajectory project](mirror_trajectory.ipynb) is the scaffolded core option. It adapts SIAM Challenge Chapter 2 to final time 3, with a supplied collision engine and a student-completed event selector. Plan about 12–18 hours across experimentation, mathematical explanation, implementation, reproduction, peer review, and revision.

Other projects from the course plan may use root isolation, positivity, global optimization, small systems, or robust geometry. Every project must state a concrete validation claim and demonstrate an inconclusive or limiting case. Agree on a manageable domain and accuracy target before expanding the computation.

## Deliverables and milestones

1. **Proposal:** state inputs, domain/time, theorem or invariant, desired enclosure/decision, and a fallback claim if the target remains unresolved.
2. **Working notebook:** show approximate exploration, derive the method, implement the required steps, and run a successful and a limiting case.
3. **Certificate:** record exact bounds, precision/environment, branch or coverage evidence, and the precise stopping outcome. Keep approximate plotting labels separate from certificate endpoints.
4. **Peer audit:** exchange notebooks and use [the audit notebook](../assignments/peer_audit.ipynb); reproduce from a fresh kernel and inspect the hypotheses.
5. **Final revision and demonstration:** respond to findings, rerun the computation, and present the supported claim and its limits.

## Suggested rubric

| Criterion | Weight | What to look for |
|---|---:|---|
| Precise claim and input model | 20% | Exact versus uncertain inputs, domain/time, accuracy and scope |
| Mathematical validation argument | 30% | Correct theorem hypotheses and every necessary branch/coverage argument |
| Readable implementation and evidence | 25% | Clear Python, enclosing arithmetic, exact records, successful and limiting examples |
| Reproduction and interpretation | 15% | Fresh-kernel run, environment, plots labeled appropriately, accurate conclusions |
| Audit response and presentation | 10% | Concrete repairs or justified responses, clear final demonstration |

A correctly bounded partial result can earn substantial credit when its claim is appropriately scoped. Unsupported success claims lose credit even if numerical digits look convincing. This project rubric applies within the syllabus's capstone assessment component; peer-audit/demonstration participation is assessed separately as scheduled.

## Mirror project options

The required target is the exact standard initial data at T=3, with coordinate and distance widths at most 10^-20. Compare numerical precision separately from changed or uncertain initial heights. Keep all inconclusive outcomes explicit.

Choose at most one extension initially: a longer time horizon, a more systematic initial-height sensitivity experiment, or a tighter record/plot audit. The original SIAM time-10 result is an advanced extension and is not required for full core credit. Longer paths can need much more precision because enclosure dependencies grow.

Student project notebooks contain tagged exercise cells. Automated starter checks skip those cells; your completed submission must run every cell after a kernel restart. Worked instructor material lives in `solutions/` and should be excluded from student releases.
