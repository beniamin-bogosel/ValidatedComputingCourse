# Codex Handoff — Validated Computing / Interval Arithmetic Course

## Context

Design a **14-lecture course on Validated Computing / Interval Arithmetic** for **Master's students in Computer Science**.

The audience is not assumed to have advanced mathematical training. They should be comfortable with basic calculus, matrices, programming, and standard numerical computation.

The course should be practical and computational, with theory introduced only as needed to explain why the algorithms are correct.

A natural reference is:

- Warwick Tucker, *Validated Numerics: A Short Introduction to Rigorous Computations*.

The course should not merely teach interval arithmetic syntax. Its central message should be:

> Ordinary numerical computation gives an approximation; validated computation gives a mathematically certified statement.

Students should repeatedly move through the following pattern:

1. Compute a plausible numerical answer.
2. Identify why it is not automatically trustworthy.
3. Construct a rigorous enclosure or verification test.
4. Improve the enclosure if it is too wide.
5. Output an explicit certificate.

Examples of desired certificates:

- a function has no zero in a given interval;
- an interval contains exactly one root;
- all roots in a domain have been found;
- a global minimum lies in a rigorous interval;
- an integral lies in a certified interval;
- a matrix is nonsingular;
- the sign of a geometric predicate is rigorously determined.

---

# Global Course Structure

Use approximately:

- 1 introductory lecture;
- 10 main technical lectures;
- 2 application/project-oriented lectures;
- 1 concluding lecture.

The recommended 14-session structure is below.

---

## Lecture 1 — Why Validated Computing?

### Main topics

- Numerical computation versus mathematical proof.
- Sources of numerical error:
  - representation error;
  - rounding error;
  - truncation error;
  - discretization error;
  - uncertainty in input data;
  - algorithmic instability.
- Examples where plausible floating-point output is misleading.
- Difference between:
  - approximation;
  - error estimate;
  - mathematically rigorous enclosure;
  - complete certificate.

### Lab

"Numerical crime scene."

Give students several short programs producing apparently reasonable results.

Tasks:

- run them at different precisions;
- compare formulations;
- identify numerical failure modes;
- explain why repeated numerical agreement is not a proof.

Goal: motivate the need for validation before formally defining intervals.

---

## Lecture 2 — Floating-Point Arithmetic

### Main topics

- Binary representation.
- IEEE 754 binary64.
- Sign, exponent, significand.
- Normal and subnormal numbers.
- Machine epsilon.
- Spacing of floating-point numbers.
- Overflow and underflow.
- Infinity, NaN, signed zero.
- Rounding modes.
- `nextfloat` / `prevfloat`.

### Demonstrations

Examples such as

```text
0.1 + 0.2 != 0.3
```

and

```text
(10^16 + 1) - 10^16
```

and finding a power of two for which

```text
2^n + 1 == 2^n
```

in binary64.

### Lab

Students explore:

- bit representations;
- neighboring floating-point values;
- spacing as magnitude changes;
- overflow;
- underflow;
- subnormal numbers;
- signed zero;
- NaNs.

---

## Lecture 3 — Error, Conditioning, Stability, Cancellation

### Main topics

- Absolute versus relative error.
- Forward versus backward error.
- Conditioning of a mathematical problem.
- Stability of an algorithm.
- Catastrophic cancellation.
- Why subtraction itself is not "bad"; the issue is relative loss of information.
- Algebraically equivalent formulas can have very different numerical behavior.

### Core examples

#### Quadratic formula

Naive form:

$$
x=\frac{-b\pm\sqrt{b^2-4ac}}{2a}.
$$

Stable formulation:

$$
q=-\frac12\left(b+\operatorname{sign}(b)\sqrt{b^2-4ac}\right),
$$

$$
x_1=\frac q a,\qquad x_2=\frac c q.
$$

#### Rationalization

$$
\sqrt{x+1}-\sqrt{x}
=
\frac{1}{\sqrt{x+1}+\sqrt{x}}.
$$

Other useful examples:

- naive versus Kahan summation;
- finite-difference derivatives;
- nearly degenerate Heron formula;
- summing numbers in different orders.

### Important conceptual point

Higher precision may reduce rounding error, but higher precision by itself does **not** constitute a proof.

### Lab

Compare stable and unstable formulations numerically.

Students should quantify:

- absolute error;
- relative error;
- effect of precision;
- effect of algebraic reformulation.

---

## Lecture 4 — Introduction to Interval Arithmetic

### Main topics

An interval is

$$
X=[\underline{x},\overline{x}]
=
\{x\in\mathbb R:\underline{x}\le x\le \overline{x}\}.
$$

Introduce:

- lower and upper endpoints;
- width;
- midpoint;
- radius;
- hull;
- intersection.

Define operations first set-theoretically:

$$
X\circ Y
=
\{x\circ y:x\in X,\ y\in Y\}.
$$

Then derive endpoint formulas for:

- addition;
- subtraction;
- multiplication;
- reciprocal;
- division.

### Central principle

If

$$
x\in X,\qquad y\in Y,
$$

then interval arithmetic must guarantee

$$
x\circ y\in X\circ Y.
$$

### Conceptual examples

For

$$
X=[0,1],
$$

we have

$$
X-X=[-1,1],
$$

even though the real expression

$$
x-x
$$

is always zero when the same variable occurs twice.

This anticipates the dependency problem.

### Lab

Implement a minimal interval type with:

- addition;
- subtraction;
- multiplication;
- division where valid.

Add containment tests using randomly sampled real values.

---

## Lecture 5 — Machine Interval Arithmetic and Directed Rounding

### Main topics

Mathematical interval arithmetic is exact as a set operation, but computer endpoints are floating-point numbers.

To preserve inclusion:

- lower endpoints must be rounded downward;
- upper endpoints must be rounded upward.

Discuss:

- outward rounding;
- correctly rounded elementary functions;
- empty intervals;
- unbounded intervals;
- division across zero;
- basic motivation for IEEE 1788.

Do not spend excessive time on the full interval standard.

### Lab

Show that naive floating-point endpoint computation can violate enclosure.

Then compare the student implementation with a trusted interval package.

Students should write property-based tests of the form:

```text
sample x in X
sample y in Y
assert real_operation(x,y) in interval_operation(X,Y)
```

---

## Lecture 6 — Interval Extensions and the Dependency Problem

### Main topics

For a real function

$$
f:\mathbb R^n\to\mathbb R,
$$

an interval extension

$$
F(X)
$$

must satisfy

$$
f(X)\subseteq F(X).
$$

Introduce:

- natural interval extension;
- inclusion isotonicity;
- overestimation;
- variable dependency;
- repeated occurrences of variables;
- monotonicity;
- subdivision.

Important distinction:

> A wide interval is not mathematically incorrect. It may simply be too weak to be useful.

### Examples

Compare different interval evaluations of expressions such as

$$
x-x,
$$

$$
\frac{x}{x},
$$

$$
x(1-x),
$$

and different factorizations of the same polynomial.

### Lab

For several functions and intervals:

- compute the natural interval extension;
- estimate the actual range numerically;
- subdivide the domain;
- plot enclosure width versus subdivision depth.

---

## Lecture 7 — Better Interval Enclosures

### Main topics

Introduce techniques for reducing overestimation:

- monotonicity;
- centered forms;
- mean-value forms;
- first-order Taylor forms;
- derivative bounds;
- subdivision;
- adaptive subdivision.

A typical mean-value enclosure:

$$
f(X)
\subseteq
f(m)+F'(X)(X-m),
$$

where

$$
m=\operatorname{mid}(X).
$$

Introduce the wrapping effect geometrically, but do not develop advanced set representations yet.

### Lab

Implement a centered or mean-value form.

Compare:

1. natural interval evaluation;
2. mean-value evaluation;
3. evaluation after subdivision.

Goal:

> certify the range of a function on an interval or box to a prescribed tolerance.

---

## Lecture 8 — Automatic Differentiation

### Main topics

Introduce automatic differentiation through computational graphs or dual numbers.

For first-order dual numbers:

$$
a+a'\varepsilon,
\qquad
\varepsilon^2=0.
$$

Explain forward-mode automatic differentiation.

Then replace real values by intervals to obtain rigorous derivative bounds.

Cover:

- scalar derivatives;
- gradients;
- Jacobians;
- perhaps Hessians only conceptually.

### Lab

Implement a minimal forward-mode AD type.

Then allow values to be intervals so that one computation returns:

- a rigorous function enclosure;
- a rigorous derivative enclosure.

---

## Lecture 9 — Validated Root Finding

This should be one of the central lectures of the course.

### Main topics

Start from ordinary bisection and Newton methods.

For an interval \(X\):

- if

$$
0\notin F(X),
$$

then \(X\) contains no root.

Introduce the interval Newton operator:

$$
N(X)
=
m-\frac{f(m)}{F'(X)},
$$

where

$$
m=\operatorname{mid}(X).
$$

Under appropriate hypotheses:

- if

$$
N(X)\cap X=\varnothing,
$$

there is no root in \(X\);

- if

$$
N(X)\subseteq X,
$$

one obtains a uniqueness certificate;

- otherwise contract or subdivide.

Discuss carefully the difference between:

- proving no root exists;
- proving at least one exists;
- proving exactly one exists;
- finding **all** roots in a bounded domain.

### Lab

Implement complete root isolation.

Input:

```text
f, [a,b], tolerance
```

Output:

```text
[interval 1] contains exactly one root
[interval 2] contains exactly one root
...
all remaining subintervals were rigorously excluded
```

This is a model example of a computational certificate.

---

## Lecture 10 — Nonlinear Systems

### Main topics

Generalize intervals to boxes:

$$
X=X_1\times\cdots\times X_n.
$$

For

$$
F:\mathbb R^n\to\mathbb R^n,
$$

introduce:

- interval Jacobians;
- multidimensional interval Newton;
- Krawczyk operator;
- exclusion;
- contraction;
- uniqueness tests.

Keep the dimension small.

### Lab

Solve a nonlinear system in two variables.

Visualize the subdivision tree or box classification:

- rejected;
- unresolved;
- certified unique solution.

---

## Lecture 11 — Validated Global Optimization

### Main topics

Validated optimization is a natural application of interval range bounds.

Introduce branch-and-bound.

For a box \(X\),

$$
f(X)\subseteq F(X).
$$

The lower endpoint of \(F(X)\) gives a rigorous lower bound on the objective over \(X\).

Use:

- incumbent upper bound;
- interval lower bounds;
- subdivision;
- derivative exclusion;
- monotonicity;
- interval Newton on stationary points.

Explain why global optimization becomes possible:

> regions can be eliminated because they are provably worse than the current best value.

### Lab

Certify the global minimum of a one- or two-dimensional function.

Compare:

- natural interval bounds;
- Taylor/mean-value bounds;
- derivative pruning.

Output a rigorous interval for the minimum value and a box containing all minimizers.

---

## Lecture 12 — Application Studio

Choose one or more of the following.

### Option A — Robust Computational Geometry

This is particularly appropriate for computer science students.

Example: orientation predicate

$$
\det
\begin{pmatrix}
x_2-x_1 & y_2-y_1\\
x_3-x_1 & y_3-y_1
\end{pmatrix}.
$$

A wrong floating-point sign may alter:

- convex hulls;
- triangulations;
- intersections;
- combinatorial topology.

Use intervals as a filter:

- positive interval -> sign certified positive;
- negative interval -> sign certified negative;
- interval containing zero -> increase precision or use exact arithmetic.

This demonstrates validation inside a conventional algorithm.

### Option B — Validated Integration

Certify

$$
\int_a^b f(x)\,dx
$$

using interval bounds and rigorous truncation estimates.

Possible example:

$$
\int_0^1 e^{-x^2}\,dx.
$$

Distinguish:

- numerical quadrature error;
- floating-point error;
- truncation error;
- final certified enclosure.

### Option C — Verified Linear Algebra

Start from an approximate solution

$$
A\widetilde{x}\approx b
$$

and residual

$$
r=b-A\widetilde{x}.
$$

Show the general validated-computing paradigm:

1. ordinary numerical algorithm gives a fast approximation;
2. rigorous verification establishes correctness.

Possible topics:

- nonsingularity;
- linear system enclosure;
- eigenvalue bounds.

### Option D — Validated ODEs

Warwick Tucker treats rigorous ODE integration.

For this audience, keep it introductory.

Possible example:

$$
x'=rx(1-x).
$$

Introduce:

- enclosure of trajectories;
- local truncation error;
- uncertainty in initial values;
- wrapping effect.

Lorenz may be mentioned as motivation rather than used as the main implementation assignment.

---

## Lecture 13 — Capstone Workshop and Certificate Auditing

### Main topics

Focus on reproducibility and the notion of a trusted computational result.

Discuss:

- mathematical claim;
- assumptions;
- trusted kernel;
- stopping criteria;
- termination;
- reproducibility;
- independent verification.

Students exchange projects and attempt to audit each other's certificates.

Questions to ask:

- What exactly has been proved?
- What depends on floating-point heuristics?
- Is completeness actually established?
- Can any branch of the computation remain unresolved?
- Is termination guaranteed?
- Is outward rounding really used?
- What external library functionality is trusted?

### Lab

Peer audit and repair of capstone projects.

---

## Lecture 14 — Conclusion: From Numerics to Computer-Assisted Proof

### Main topics

Review the hierarchy:

```text
floating-point approximation
        ↓
error analysis
        ↓
interval enclosure
        ↓
validated algorithm
        ↓
computational certificate
        ↓
computer-assisted proof
```

Discuss relation to:

- arbitrary precision;
- exact rational arithmetic;
- symbolic computation;
- automatic differentiation;
- theorem proving;
- formal proof assistants such as Lean;
- proof-producing numerical software.

Also discuss limitations:

- dependency;
- dimensional explosion;
- excessive subdivision;
- wrapping;
- poor coordinate choices;
- ill-conditioned problems;
- difficulty proving termination.

Briefly mention more advanced methods:

- Taylor models;
- affine arithmetic;
- zonotopes;
- ball arithmetic;
- validated ODE solvers;
- rigorous PDE numerics;
- computer-assisted proofs in dynamical systems.

---

# Recommended Software Stack

## Primary recommendation: Julia

A clean choice for the course is:

- Julia;
- `IntervalArithmetic.jl`;
- optionally `ForwardDiff.jl`;
- Pluto or Jupyter notebooks.

Reasons:

- concise mathematical syntax;
- strong generic programming;
- easy comparison between `Float64`, `BigFloat`, and interval values;
- well-developed interval arithmetic ecosystem;
- suitable for implementing algorithms rather than merely calling black-box software.

Useful built-in concepts/functions include:

- floating-point inspection;
- neighboring representable values;
- `BigFloat`;
- generic numeric types.

## Optional comparison: Python + Arb/FLINT

Because many CS students know Python, a later comparison could use:

- `python-flint`;
- Arb ball arithmetic.

This permits discussion of endpoint intervals

$$
[a,b]
$$

versus midpoint-radius or ball representations

$$
m\pm r.
$$

Do not introduce Arb first. Endpoint intervals make the set interpretation clearer.

---

# Recommended Laboratory Philosophy

Every lab should follow essentially the same structure.

## 1. Claim

State a precise mathematical statement.

Example:

> Prove that \(f\) has exactly three zeros in \([-5,5]\).

## 2. Approximation

Use ordinary floating-point computation to obtain a plausible answer.

## 3. Failure analysis

Explain why the approximation does not yet prove the claim.

## 4. Validation

Use intervals, derivative bounds, interval Newton, subdivision, etc.

## 5. Certificate

Output a concise rigorous conclusion.

Example:

```text
Claim:
f has exactly three roots in [-5,5].

Certificate:
[-2.1031,-2.1030] contains exactly one root.
[ 0.4999, 0.5001] contains exactly one root.
[ 3.7412, 3.7414] contains exactly one root.

Every other subinterval of [-5,5] was rejected because
0 was not contained in its interval image.

Therefore these are all roots of f in [-5,5].
```

Students should learn that the **certificate is the output**, not merely a decimal approximation.

---

# Suggested Assessment

Possible distribution:

- 40% weekly laboratories;
- 20% short conceptual tests;
- 30% capstone project;
- 10% capstone demonstration / peer audit.

A traditional proof-heavy examination is probably not ideal for this audience.

Assessment should focus on whether students can:

- formulate a precise numerical claim;
- distinguish approximation from proof;
- select an appropriate validation strategy;
- implement the strategy correctly;
- state exactly what has been certified;
- recognize when an interval result is merely inconclusive.

---

# Possible Capstone Projects

Suitable topics include:

1. Complete root isolation for a parameterized polynomial.
2. Certified global minimization in one or two dimensions.
3. Proving positivity of a function on a box.
4. Robust computational geometry predicates.
5. Validated solution of a small nonlinear system.
6. Certified numerical integration.
7. Comparison of natural, centered, and Taylor interval forms.
8. Floating-point filter with interval or arbitrary-precision fallback.
9. Certified range evaluation for a small computational graph.
10. Property-based testing of interval arithmetic implementations.
11. Verified linear-system solver.
12. Small validated ODE integrator.

Prefer projects with a clear final statement such as:

$$
f(x)>0\qquad\text{for every }x\in X,
$$

or

> The system has exactly four solutions in the prescribed domain.

---

# What to De-emphasize

For this audience, avoid spending too much time on:

- abstract foundations of real analysis;
- long convergence proofs;
- full details of IEEE 1788 decorations;
- advanced Taylor models;
- high-order validated ODE algorithms;
- infinite-dimensional validated numerics;
- sophisticated rigorous PDE algorithms.

These may be mentioned in the concluding lecture.

---

# Suggested Conceptual Backbone

The course should repeatedly emphasize the following progression:

$$
\boxed{
\text{Understand floating point}
\longrightarrow
\text{Compute rigorous enclosures}
\longrightarrow
\text{Improve the enclosures}
\longrightarrow
\text{Certify local statements}
\longrightarrow
\text{Certify global statements}
}
$$

A second useful conceptual hierarchy is:

```text
approximate
→ bound the error
→ verify
→ certify
→ prove
```

---

# Role of Warwick Tucker's Book

Use Warwick Tucker, *Validated Numerics*, as the mathematical backbone rather than as a syllabus to follow rigidly.

Useful Tucker themes include:

- interval arithmetic;
- rigorous function evaluation;
- root finding;
- optimization;
- quadrature;
- automatic differentiation;
- rigorous ODE integration.

Adapt the material toward:

- Master's CS students;
- executable algorithms;
- software design;
- explicit certificates;
- short mathematical proofs;
- reproducible numerical experiments.

The course should be somewhat more algorithmic and software-oriented than the book.

---

# Design Principles for Individual Lectures

A useful approximate balance for each technical lecture:

- 20% motivation / numerical failure example;
- 30% definitions and one key theorem;
- 20% worked algorithm or pseudocode;
- 30% guided computational exercise.

Do not end lectures immediately after definitions.

Ideally, every technical lecture should culminate in a statement a computer can certify.

---

# Tasks for Codex

Continue course development using this document as the baseline.

## Immediate tasks

1. Produce a detailed syllabus for all 14 lectures.
2. For each lecture specify:
   - learning objectives;
   - prerequisite concepts;
   - definitions;
   - 1–3 central theoretical results;
   - worked examples;
   - lab exercises;
   - homework exercises;
   - expected programming effort.
3. Keep mathematical prerequisites modest.
4. Use `$$ ... $$` for displayed mathematics in Markdown.
5. Prefer constructive numerical examples over abstract generality.

## Develop Lecture 1–3 first

Prepare full materials for:

- floating-point representation;
- IEEE 754 behavior;
- numerical error;
- catastrophic cancellation;
- conditioning versus stability.

Include executable Julia examples.

Particularly develop examples involving:

- neighboring floats;
- machine epsilon;
- `0.1 + 0.2`;
- loss of increments at large magnitude;
- cancellation;
- stable quadratic roots;
- Kahan summation;
- finite differences.

## Then develop the interval arithmetic core

For Lectures 4–7 prepare:

- rigorous definitions;
- proofs of basic inclusion properties;
- endpoint formulas;
- directed rounding demonstrations;
- dependency examples;
- natural interval extensions;
- mean-value / centered forms;
- subdivision strategies.

Design a small student-built interval class before switching to `IntervalArithmetic.jl`.

## Then develop validated algorithms

For Lectures 8–11 prepare implementable versions of:

- forward-mode automatic differentiation;
- interval derivatives;
- interval Newton;
- complete root isolation;
- Krawczyk operator;
- branch-and-bound global optimization.

Each algorithm should explicitly distinguish:

- heuristic numerical search;
- rigorous verification;
- certificate generation.

## Lab framework

Create a common lab template containing:

```text
Claim
Ordinary numerical experiment
Why this does not prove the claim
Validated method
Certificate
Failure / inconclusive case
```

Use this framework throughout the course.

## Final goal

The completed teaching package should eventually contain:

```text
course/
├── syllabus.md
├── references.md
├── lectures/
│   ├── lecture01.md
│   ├── ...
│   └── lecture14.md
├── labs/
│   ├── lab01/
│   ├── ...
│   └── lab12/
├── notebooks/
├── assignments/
├── projects/
│   └── project_topics.md
└── solutions/
```

The aim is to create a course where students finish with the ability to turn numerical experiments into mathematically reliable computational statements.
