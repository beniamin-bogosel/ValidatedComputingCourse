# Validated Computing — Course Development Plan

Status: Phases A–F are implemented as release candidate 1.0.0-rc1.
See [README.md](README.md) for the course index and [DEVELOPMENT_STATUS.md](DEVELOPMENT_STATUS.md)
for verification and remaining classroom-pilot work.

## 1. Direction and assumptions

Build a Python course in which **the lecture notebook is the course material**: explanations, definitions, short proofs, executable examples, plots, and interpretation live together. Labs are separate notebooks with implementation tasks and written reasoning. Students finish by producing and auditing precise computational certificates.

Use the 14-session structure in [the original handoff](validated_computing_course_codex_handoff.md), with the language choice superseded by [the Python stack](validated_computing_python_stack.md) and the delivery format specified in [the notebook plan](validated_computing_notebook_first.md). Do not maintain a parallel Julia version or a second set of lecture notes in Markdown.

Planning assumptions, to be adjusted once the timetable is known:

- Audience: Master's students in CS; Python, elementary calculus, and basic linear algebra. No advanced analysis prerequisite.
- Teaching: 14 lectures, provisionally 90–120 minutes each; 12 associated labs of approximately 2 hours. Sessions 13–14 focus on project audit and synthesis.
- Independent work: ordinarily 1–2 hours per lab beyond contact time; the heavier algorithm labs may need 2–3 hours. Extensions are optional.
- Delivery: English, local Python environments, JupyterLab or VS Code. Core examples run on an ordinary laptop without a GPU or network connection after installation.
- Reference: Tucker's *Validated Numerics* is the intended mathematical backbone. If supplied in `Doc/`, use it to verify theorem hypotheses and add section/page references before developing the corresponding lectures. No chapter mapping is assumed yet.

The learning progression is:

```text
float → Fraction / Decimal → MPFR with directed rounding
      → student endpoint intervals → Arb arithmetic
      → student validated algorithms → auditable certificates
```

By the end, students should be able to explain a numerical failure, construct an inclusion-preserving computation, improve an enclosure, implement local and global validation methods, and distinguish success from an inconclusive result.

## 2. Notebook design

Produce 14 lecture notebooks, 12 lab notebooks, corresponding instructor solutions, and an ungraded `00_setup.ipynb`.

Each lecture should have:

1. Learning objectives, prerequisites, estimated time, and linked lab.
2. A motivating numerical problem and an ordinary computation.
3. A precise account of what that computation establishes.
4. Alternating theory and experiments: definitions, one principal theorem with a short proof or proof sketch, worked code, and interpretation.
5. A worked validation result where the prerequisites support one.
6. Short checkpoints and a failure or inconclusive example.
7. Recap, reading references, and optional extensions.

Use recurring THEORY, EXPERIMENT, and EXERCISE labels, but keep the prose connected. Early lectures can end with exact arithmetic checks or explicit limitations; they need not introduce interval machinery prematurely. Use `$$ ... $$` for displayed mathematics.

Each lab should have:

1. Claim or investigative question.
2. Approximate experiment.
3. Explanation of why approximation does not establish the claim.
4. Guided implementation, followed by one independent task.
5. Validation and interpretation of the resulting certificate, when applicable.
6. A deliberately difficult case and an honest report of what remains unresolved.
7. A short homework question and an optional extension.

Lab deliverables are completed notebooks containing code, outputs, and written conclusions. Supply function signatures and small diagnostic checks. Keep core tasks within the allotted time; students should not have to build an entire numerical library to complete a week's lab.

Student notebooks must open and run their setup/demonstration cells before exercises are solved. Incomplete exercises must be clearly marked and must never silently substitute a reference implementation. Instructor solutions and completed submissions must run from a fresh kernel from top to bottom.

## 3. Teaching sequence

Number lecture and lab notebooks consistently: `01_...` pairs with `lab01_...` through week 12. Do not use the shifted lab numbering found in one of the initial examples.

### 01 — Why validated computing?

- **Objectives/prerequisites:** distinguish an approximation, an error estimate, an enclosure, and a certificate; requires basic Python and functions.
- **Theory:** representation, rounding, truncation, and input uncertainty; exact versus approximate claims. Central result: an explicit bound `|x - a| ≤ e` implies an enclosure; numerical agreement alone supplies no such bound.
- **Worked examples:** `0.1 + 0.2`, loss of an increment at large magnitude, and an approximate root with a small residual. Use `Fraction` to inspect an exact rational case.
- **Lab 01:** a numerical crime scene: run supplied programs, classify failure modes, and rewrite vague conclusions as precise claims. Mostly interpretation, with 30–45 minutes of coding.
- **Homework:** state what extra evidence would be needed to turn one observed answer into a proof.

### 02 — Floating-point representation and rounding

- **Objectives/prerequisites:** inspect binary64 values, predict spacing, and explain rounding; builds on 01 and elementary powers of two.
- **Theory:** sign/exponent/significand, normal/subnormal values, unit roundoff versus machine epsilon, overflow, NaN, and signed zero. Central results: spacing within a binade and the relative rounding-error model, with its normal-range assumptions.
- **Worked examples:** `float.hex`, `as_integer_ratio`, `math.nextafter`, powers of two, and exact `Fraction` comparisons. Introduce `Decimal` and why string construction differs from float construction. Explain that Python scalar operations may raise exceptions where NumPy exposes IEEE special values.
- **Lab 02:** map spacing, identify the lost-increment threshold, and audit input conversion. About 60–90 minutes of coding.
- **Homework:** derive spacing in one binade and explain why a relative-error bound needs care near underflow.

### 03 — Error, conditioning, stability, and cancellation

- **Objectives/prerequisites:** separate sensitivity of a problem from quality of an algorithm; requires 02 and first derivatives.
- **Theory:** absolute/relative error, forward/backward error, conditioning, and cancellation. Central results: first-order sensitivity through derivatives and the effect of input perturbations on subtraction.
- **Worked examples:** stable quadratic roots, rationalizing a difference of square roots, and naive versus compensated summation. Treat finite differences as an extension if lecture time is tight. Handle degenerate quadratic cases explicitly rather than applying the stable formula blindly.
- **Lab 03:** compare formulations and precision, using exact references where available and explicitly labelled high-precision approximations elsewhere. About 90–120 minutes of coding.
- **Homework:** explain a case where more precision helps and a case where uncertain input remains the limiting factor.

### 04 — Mathematical interval arithmetic

- **Objectives/prerequisites:** derive endpoint operations from sets and implement them; requires 01–03 and elementary inequalities.
- **Theory:** interval, width, midpoint, radius, hull, intersection, containment, and arithmetic range. Central results: endpoint formulas and inclusion for the supported arithmetic operations; division requires a denominator excluding zero.
- **Worked examples:** multiplication across sign combinations, reciprocal on a negative interval, and `X - X`. Distinguish a dedicated square operation from multiplying two independent copies of an interval.
- **Lab 04:** build a small bounded interval type with rational endpoints for exact arithmetic, including empty intersection handling. Limit operations to rational arithmetic; deliberately naive float arithmetic appears as a counterexample in 05. About 90–120 minutes of coding with a scaffold.
- **Homework:** prove one endpoint formula and explain why dependency does not violate inclusion.

### 05 — Machine intervals and directed rounding

- **Objectives/prerequisites:** preserve enclosure in machine arithmetic, including input conversion; requires 02 and 04.
- **Theory:** outward rounding, MPFR precision and local rounding contexts, domain errors, and the distinction between precision and validation. Central result: outward-rounded endpoint formulas preserve inclusion when inputs are enclosed and operation preconditions hold.
- **Worked examples:** exact rational counterexamples to naive float endpoints; `mpfr(0.1)` versus `mpfr("0.1")`; correct downward/upward parsing of intended decimal endpoints.
- **Lab 05:** replace the rational arithmetic kernel with `gmpy2` directed operations; check against exact rational results. Introduce Arb in a short comparison after the endpoint implementation works. About 90–120 minutes of coding using supplied context utilities.
- **Homework:** audit an implementation with a deliberately incorrect rounding mode. Random tests are bug-finding evidence, not a proof of all-input inclusion.

### 06 — Interval extensions and dependency

- **Objectives/prerequisites:** construct inclusion functions and recognize overestimation; requires 04–05.
- **Theory:** natural interval extension, inclusion isotonicity, dependency, and subdivision. Central results: compositional inclusion and enclosure of a domain through a covering subdivision.
- **Worked examples:** `x - x`, `x / x` on a domain excluding zero, and three forms of `x(1-x)`. Compare the student endpoint type with Arb and introduce safe box-to-ball conversion.
- **Lab 06:** implement subdivision-based range enclosure and plot bounds versus subdivision depth. Treat sampled values as illustrations; use analytically known ranges for selected comparisons. About 60–90 minutes of coding.
- **Homework:** explain why increasing arithmetic precision alone does not remove dependency overestimation.

### 07 — Better enclosures

- **Objectives/prerequisites:** choose between algebraic reformulation, monotonicity, centered forms, and subdivision; requires 06 and the mean value theorem.
- **Theory:** derivative bounds and mean-value forms, with manually supplied derivatives this week. Central results: the mean-value enclosure and endpoint range bounds for certified monotone functions.
- **Worked examples:** a polynomial on a wide interval and a simple transcendental function evaluated through Arb; introduce wrapping geometrically.
- **Lab 07:** implement mean-value and monotonicity bounds, then audit a supplied readable adaptive subdivision with an explicit budget. Students implement uniform subdivision in Lab 06; completing an adaptive search from scratch is an extension. Report the guaranteed enclosure and the stopping condition separately. About 90–120 minutes of coding.
- **Homework:** give an example where a centered form does not improve the natural form; optional positivity certification on a box.

### 08 — Automatic differentiation with intervals

- **Objectives/prerequisites:** compute derivative enclosures through the same expression graph; requires 07, the chain rule, and basic operator overloading.
- **Theory:** dual numbers, forward mode, and Jacobian columns. Central results: arithmetic/chain rules for dual numbers and inclusion of derivatives when their component operations are rigorous.
- **Worked examples:** polynomial and elementary-function derivatives, evaluated first with ordinary numbers and then with balls. Explain domain restrictions and why branch-dependent programs need additional care.
- **Lab 08:** implement a scalar dual type for a small operation set; use supplied scaffolding for a two-variable Jacobian. About 90–120 minutes of coding. Hessians are an extension.
- **Homework:** compare interval AD with finite differences and explain their different guarantees.

### 09 — Validated scalar root finding

- **Objectives/prerequisites:** prove exclusion, existence, uniqueness, and domain-wide coverage; requires 06–08 and continuity.
- **Theory:** sign bracketing, interval Newton, contraction, subdivision, and completeness. State the exact hypotheses of the selected interval Newton theorem, including a derivative interval excluding zero; use strict interior inclusion as the conservative success test in the taught implementation.
- **Worked examples:** certify a root of `x² - 2`; isolate the simple roots of `(x+2)(x-1)(x-3)` on `[-3,4]`; show the difficulty of a multiple root and a root at a subdivision boundary.
- **Lab 09:** complete supplied search scaffolding with exclusion, Newton contraction, certification, and unresolved outcomes. Return all certified root intervals plus coverage evidence and unresolved boxes. About 2–3 hours of coding across lab and homework.
- **Homework:** audit an incorrect “all roots found” claim. Multiple-root isolation is optional; the core method may legitimately remain inconclusive there.

### 10 — Small nonlinear systems

- **Objectives/prerequisites:** extend scalar validation to boxes; requires 08–09 and matrices.
- **Theory:** interval Jacobians, approximate inverse preconditioning, and the Krawczyk operator. Central results: root containment/exclusion and a sufficient inclusion/contraction criterion for existence and uniqueness, with all hypotheses stated and checked.
- **Worked examples:** intersections of `x² + y² = 1` and `x = y`; a near-singular Jacobian as a failure case. NumPy may propose a preconditioner; rigorous arithmetic must verify the resulting inequalities.
- **Lab 10:** implement Krawczyk evaluation for a 2×2 system using supplied box and matrix helpers. Local certification is the required task; exhaustive box search is an extension. About 90–120 minutes of coding.
- **Homework:** explain why a small residual and an approximate matrix inverse do not establish uniqueness.

### 11 — Validated global optimization

- **Objectives/prerequisites:** bound a global optimum and retain all candidate minimizers; requires 06–07 and search algorithms, with 09 as useful background.
- **Theory:** lower bounds, feasible incumbents, branch-and-bound, and stopping gaps. Central results: safe pruning by a validated incumbent upper bound and the invariant enclosing the global minimum over a covered compact domain.
- **Worked examples:** a one-dimensional multimodal polynomial, with a two-dimensional example as an extension. Compare natural and mean-value bounds.
- **Lab 11:** implement branch-and-bound using supplied queue/plotting utilities. Return a certified interval for the minimum value and a union of retained boxes covering every minimizer. About 2–3 hours of coding across lab and homework.
- **Homework:** audit boundary handling and stopping criteria. A narrow bound on the minimum value does not imply narrow localization of all minimizers.

### 12 — Application studio: robust geometry

- **Objectives/prerequisites:** embed validation in a familiar CS algorithm; requires 05–07 and determinants.
- **Theory:** orientation predicates, interval sign tests, and exact fallback. Central results: a determinant enclosure excluding zero certifies its sign; exact rational evaluation decides the sign for exact rational inputs, including degeneracy.
- **Worked examples:** nearly collinear points and the difference between exact decimal coordinates and uncertain measured coordinates.
- **Lab 12:** implement an Arb sign filter with precision escalation and a `Fraction` fallback for exact rational inputs. About 60–90 minutes of coding, leaving time for capstone work.
- **Homework/extension:** explain why exact arithmetic cannot remove physical input uncertainty. Optional studio alternatives are elementary validated integration or residual-based linear-system verification; develop one core studio first. Validated ODEs remain an advanced project or concluding demonstration.

### 13 — Capstone workshop and certificate audit

- **Objectives/prerequisites:** state and audit a computational claim; requires the methods used in the student's project.
- **Theory:** assumptions, trusted arithmetic and algorithm code, reproducibility, domain coverage, and unresolved cases. Consolidate earlier theorems rather than adding a new method.
- **Worked example:** audit a plausible-looking certificate that omits an unresolved branch.
- **Workshop:** exchange capstone notebooks, rerun from a clean kernel, inspect proof conditions, and file an audit in a notebook template. Programming effort depends on repairs.
- **Homework:** revise the certificate and document the response to the audit.

### 14 — From validated numerics to computer-assisted proof

- **Objectives/prerequisites:** explain the scope and limits of the course's guarantees; builds on the complete course.
- **Theory:** synthesis of approximation, enclosure, local validation, and global coverage; distinguish numerical certification from formal verification of the implementation. Introduce dependency, wrapping, dimension, and conditioning as practical limitations.
- **Worked examples:** revisit the opening failures with the tools now available; instructor demonstrations may introduce Taylor models or rigorous ODEs.
- **Session activity:** concise project demonstrations and a claim-classification exercise. No new programming assignment.
- **Final deliverable:** project notebook, reproducible certificate data where applicable, and the completed peer-audit response.

## 4. Software and repository design

The implemented package follows this notebook-first structure; see README.md for the current linked inventory:

```text
ValidatedCompCourse/
├── COURSE_PLAN.md
├── README.md                     # setup and linked course index
├── syllabus.md                   # concise student-facing schedule and assessment
├── references.md                 # reading map and software references
├── pyproject.toml                # package and dependency declarations
├── requirements-lock.txt         # tested environment, produced after compatibility checks
├── jupytext.toml
├── notebooks/
│   ├── 00_setup.ipynb
│   ├── 01_intro.ipynb
│   ├── ...
│   └── 14_synthesis.ipynb
├── labs/                         # lab01–lab12, paired with lectures
├── solutions/                    # instructor distribution only
├── templates/                    # lecture, lab, project, and audit notebooks
├── vc/                           # small, documented supporting Python package
│   ├── intervals.py
│   ├── arb_bridge.py
│   ├── autodiff.py
│   ├── roots.py
│   ├── systems.py
│   ├── optimization.py
│   └── certificates.py
├── tests/                        # arithmetic and algorithm correctness checks
├── projects/                     # topics, rubric, proposal and report notebooks
├── figures/                      # reusable or generated teaching figures
└── Doc/                          # local reference material, if supplied
```

Numerical dependencies are NumPy, Matplotlib, `gmpy2`, and `python-flint`; exact rational and decimal arithmetic come from the standard library. Use JupyterLab, ipykernel, and Jupytext for teaching, plus pytest and a notebook execution tool for development. `mpmath` is optional for exploratory comparisons. Pick and pin a supported Python/package combination only after installation and arithmetic smoke checks on the teaching platforms.

The documented `gmpy2` contexts provide precision and directed rounding controls needed for the teaching kernel. Use scoped contexts so one experiment does not change later arithmetic accidentally. See the [gmpy2 context documentation](https://gmpy2.readthedocs.io/en/stable/contexts.html).

Arb represents enclosures as midpoint-radius balls, with precision controls and enclosure-related operations. Keep geometric subdivision boxes distinct from ball evaluations; implement and test the small conversion/predicate layer needed by the algorithms. Endpoint-to-ball conversion must enclose the entire input interval even when the midpoint and radius are rounded. See the [python-flint Arb reference](https://python-flint.readthedocs.io/en/stable/arb.html).

Pair notebooks with Jupytext `py:percent` files. Commit both forms so students can open `.ipynb` directly and authors can review text diffs. Edit one representation at a time, explicitly synchronize it before committing, and check agreement in the build; do not rely on the editor to infer the intended source. See [Jupytext's paired-notebook workflow](https://jupytext.readthedocs.io/en/latest/paired-notebooks.html).

Notebooks remain the teaching narrative and the place where students implement the central methods. The shared `vc` package supplies public infrastructure and reviewed implementations for lectures and later weeks. State when students may consult this code during implementation exercises; it is included in the student edition. Publish worked lab solutions after the relevant exercise deadline so later labs have a working baseline even if a student did not finish an earlier lab. Instructor solutions must be excluded from student releases, including notebook outputs and metadata.

Avoid a large generic arithmetic framework. Implement only what the worked examples need. In particular, the student interval kernel initially handles bounded intervals and basic arithmetic, explicitly rejects division through zero, and leaves general elementary functions to Arb.

## 5. Mathematical and execution quality requirements

These refine the initial plans and should be applied while authoring:

- **Input semantics:** distinguish the exact value of a supplied binary float, an intended decimal/rational number, and uncertain input data. Increasing precision does not recover discarded information.
- **Meaning of testing:** random containment samples can expose bugs. Exact rational comparisons and targeted edge cases provide stronger regression tests, but the inclusion argument still rests on mathematics and the arithmetic implementation's guarantees.
- **Proof conditions:** every validation branch must cite the theorem it implements and check its hypotheses. A small box, small residual, overlapping enclosures, or many matching digits is insufficient by itself.
- **Global coverage:** root isolation must account for every part of the original domain, avoid counting boundary roots twice, and keep unresolved boxes. A budget-limited run can return useful partial results without claiming completeness.
- **Optimization:** incumbents require rigorous upper bounds at feasible points. Preserve boundary candidates when pruning with derivatives. Retaining all minimizers requires care with ties; use strict objective pruning for that claim.
- **Stopping criteria:** separate a certified value/error gap from a requested geometric width. Impose time, depth, or box budgets and report inconclusive outcomes when needed. Do not promise termination for arbitrary inputs.
- **Certificate representation:** store the claim, exact input description, domain, precision, algorithm parameters, validated inequalities, and any unresolved regions. Use exact dyadic/rational encodings or documented outward-enclosing strings for bounds, never a conversion through ordinary float merely to serialize them.
- **Trust statement:** a successful notebook is a computational certificate conditional on the stated mathematics and trusted software. An optional smaller checker can replay proof conditions; it is not automatically a formally verified proof.
- **Execution:** each completed notebook starts from a fresh kernel, imports its own dependencies, establishes its precision, fixes any random seed, and runs without earlier notebooks or internet access. Keep plots illustrative and prevent plotting conversions from entering certification decisions.

During implementation, test the arithmetic kernel with exact rational oracles, rounding-boundary cases, zero crossings, and context restoration. Test algorithms with known answers, incomplete searches, multiple/boundary roots, singular systems, and objective ties. Execute lecture and solution notebooks automatically; validate unsolved lab structure/setup separately. Compare mathematical bounds and statuses rather than brittle printed digit strings.

## 6. Assessment and capstones

Keep the original proposed weighting:

| Component | Weight | Evidence |
|---|---:|---|
| Labs | 40% | Implementation, interpretation, and honest handling of failure |
| Short conceptual tests | 20% | Error analysis, theorem hypotheses, and claim classification |
| Capstone project | 30% | Reproducible validated result with clearly stated scope |
| Demonstration and peer audit | 10% | Reproduction, critique, and response to identified issues |

For manageable marking, keep weekly labs short and group them into four submission portfolios: 01–03, 04–06, 07–09, and 10–12. Publish individual checkpoint expectations before teaching.

Introduce project choices in week 07, collect a precise claim and domain in week 09, require an initial validated result in week 11, and audit it in week 13. A suggested capstone budget is 12–18 hours per student, with the final weeks' independent workload shifted toward the project.

Default projects: scalar root isolation, positivity on a box, one-dimensional global optimization, a small nonlinear system, robust geometric predicates, or elementary validated integration. Range-bound comparisons and arithmetic testing projects must include a concrete validation claim. Offer linear-system verification as an extension and ODE validation only with substantial instructor scaffolding.

The final submission is a notebook with the claim, assumptions, approximate exploration, theorem used, validated computation, certificate, limitations, and reproduction instructions. Reward a correctly identified inconclusive case over an unsupported success claim.

## 7. Development order and review milestones

| Phase | Deliverables | Completion criterion |
|---|---|---|
| A. Foundation | Setup notebook; lecture/lab templates; package skeleton; environment; Jupytext workflow; course index | Setup and one sample notebook run in a fresh environment; paired sources agree |
| B. First teaching block | Full Lectures 01–03, Labs 01–03, instructor solutions, conceptual questions | Examples are checked; theory/code balance and student workload are reviewed |
| C. Interval core | Lectures/Labs 04–07; rational and MPFR teaching kernels; Arb bridge; arithmetic checks | Supported inclusion properties have derivations and regression coverage; each notebook runs independently |
| D. Validation algorithms | Lectures/Labs 08–11; AD, roots, systems, optimization; certificate records | Each method has a successful and an inconclusive example; proof conditions and coverage claims are checked |
| E. Applications and projects | Lecture/Lab 12; Lectures 13–14; project and audit templates; rubric | At least one complete model capstone can be reproduced and audited |
| F. Release | Student/instructor notebook bundles; executed reading copies; tested environment; reading map | Student bundle has no solution leakage; completed notebooks pass clean execution; links and mathematics are reviewed |

Develop the phases in order. Within each topic, write the mathematical claim and hypotheses first, build a small executable example, turn it into a lecture narrative, then derive the lab and solution from it. This makes the lab match the material actually taught.

**Current review milestone:** Phases A–F are complete as release candidate 1.0.0-rc1, including separate student/instructor bundles, executed browser reading copies, independent installation and notebook execution, and mathematical and teaching review. See [the release review](Doc/release_review.md) for corrections and verification evidence. Classroom pacing and other operating systems still need a pilot.
The mirror capstone certifies the SIAM geometry at time 3; time 10 remains an optional extension. Its event selector verifies ordering and horizon comparisons, while a unit-speed bound justifies the finite lattice enumeration.
Python examples use explicit steps, short functions, and named intermediate values. See [development status](DEVELOPMENT_STATUS.md) and [the interval-core summary](Doc/interval_core_development.md) and [validation-algorithms summary](Doc/validation_algorithms_development.md), and [applications/capstone summary](Doc/applications_capstone_development.md).
