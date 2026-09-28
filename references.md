# Course references

## Mathematical backbone

Warwick Tucker, *Validated Numerics: A Short Introduction to Rigorous Computations*, Princeton University Press, 2011. The locally supplied PDF is in `Doc/`. The lecture notebooks explain the required material; the book provides further reading.

| Teaching block | Reading / use |
|---|---|
| Lecture 01 | Chapter 1, especially §§1.2 and 1.6: input representation and numerical examples |
| Lecture 02 | §§1.2–1.5: floating-point numbers, rounding, arithmetic, and IEEE formats |
| Lecture 03 | §1.6, Examples 1.6.1–1.6.2, printed pp. 19–21: Rump's example and the expanded polynomial |
| Lecture 04 | §§2.1–2.2, printed pp. 24–29: real intervals and interval arithmetic |
| Lecture 05 | §2.4, printed pp. 37–45: floating point interval arithmetic, especially §2.4.2 on rounding modes |
| Lecture 06 | §3.1, printed pp. 46–54: interval functions; Example 3.1.4 supplies the trigonometric sign example |
| Lecture 07 | §§3.2–3.3, printed pp. 55–59: centered forms and monotonicity |
| Lecture 08 | §4.1, printed pp. 60–64: first-order automatic differentiation; higher orders are optional |
| Lecture 09 | §§5.1.1–5.1.3, printed pp. 73–81: scalar root methods, especially interval Newton and Theorem 5.5 |
| Lecture 10 | §5.1.5, printed pp. 83–86: scalar Krawczyk; Appendix A.4: fixed-point theorems; multivariate supplement below |
| Lecture 11 | §5.2.1, printed pp. 87–89: optimization; monotonicity and convexity extensions in §§5.2.2–5.2.3 |

The scalar C¹ interval Newton test is proved in Lecture 09; its strict interior criterion is deliberately conservative. Lecture 10 gives a direct contraction proof for a small multivariate Krawczyk test. Instructor background: S. M. Rump, *Verification methods: rigorous results using floating-point arithmetic*, Acta Numerica (2010), [§13](https://www.tuhh.de/ti3/rump/intlab/ActaNumerica2010.pdf). The long survey is optional, not required introductory reading.

## Application and workshop readings

- Lecture 12: J. R. Shewchuk, [robust predicates introduction and papers](https://www.cs.cmu.edu/~quake/robust.html). This motivates determinant sign tests and adaptive precision; the course implementation uses Arb and rational fallback rather than expansion arithmetic.
- Mirror capstone: SIAM Challenge Chapter 2, pp. 33–46, especially §2.3 on reliable reflections, pp. 41–43. The course uses the original geometry and initial conditions with a shorter final time of 3. See [the source note](Doc/mirror_trajectory_project.md).
- Lectures 13–14 consolidate earlier proofs and require no new external reading. The exact rational rotation example illustrates wrapping without arithmetic rounding.

## Examples and projects

- [Tucker Chapter 1 examples](Doc/tucker_chapter1_examples.md).
- [Patriot reference note](Doc/patriot_failure_reference.md), with the [GAO primary report](https://www.gao.gov/assets/imtec-92-26.pdf). The notebook's fixed-point calculation is explicitly a simplified model.
- Bornemann, Laurie, Wagon, and Waldvogel, *The SIAM 100-Digit Challenge*. [Chapter index](Doc/siam_challenge_examples.md). Chapter 4 supports global optimization; Chapter 2 supports the [mirror-trajectory project](Doc/mirror_trajectory_project.md).
- [Existing advanced course review](Doc/existing_course_review.md). Use selected examples without adopting its Banach-space introduction.

## Software documentation

- [Python floating-point tutorial](https://docs.python.org/3/tutorial/floatingpoint.html).
- [Exact rational arithmetic](https://docs.python.org/3/library/fractions.html) and [Decimal](https://docs.python.org/3/library/decimal.html).
- [gmpy2 contexts](https://gmpy2.readthedocs.io/en/stable/contexts.html).
- [python-flint general concepts](https://python-flint.readthedocs.io/en/stable/general.html) and [Arb](https://python-flint.readthedocs.io/en/stable/arb.html).
- [Jupytext paired notebooks](https://jupytext.readthedocs.io/en/latest/paired-notebooks.html).
- [nbclient notebook execution](https://nbclient.readthedocs.io/en/latest/client.html).

Record the installed versions when reproducing numerical results; historical output tables need not match a modern Python evaluation order or arithmetic environment.

