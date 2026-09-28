# Course references

The lecture notebooks explain the required material. These readings provide context and further examples; books and source PDFs are not included in this distribution and are not runtime dependencies.

## Tucker reading map

Warwick Tucker, *Validated Numerics: A Short Introduction to Rigorous Computations*, Princeton University Press, 2011. Page numbers below are printed book pages.

| Lecture | Reading |
|---|---|
| 01 | Chapter 1, especially §§1.2 and 1.6: inputs and numerical examples |
| 02 | §§1.2–1.5: representation, rounding and floating-point arithmetic |
| 03 | §1.6, Examples 1.6.1–1.6.2, pp. 19–21: cancellation examples |
| 04 | §§2.1–2.2, pp. 24–29: real intervals and arithmetic |
| 05 | §2.4, pp. 37–45: machine interval arithmetic and rounding modes |
| 06 | §3.1, pp. 46–54: interval functions and inclusion |
| 07 | §§3.2–3.3, pp. 55–59: centered forms and monotonicity |
| 08 | §4.1, pp. 60–64: first-order automatic differentiation |
| 09 | §§5.1.1–5.1.3, pp. 73–81: root methods and interval Newton |
| 10 | §5.1.5, pp. 83–86, and Appendix A.4: scalar Krawczyk and fixed points |
| 11 | §5.2.1, pp. 87–89: global optimization |

Lectures 13–14 consolidate the preceding arguments and require no additional external reading.

## Applications and background

- [Tucker Chapter 1 example note](Doc/tucker_chapter1_examples.md).
- [Patriot timing-failure note](Doc/patriot_failure_reference.md), with the primary GAO report and the scope of the simplified classroom model.
- Bornemann, Laurie, Wagon, and Waldvogel, *The SIAM 100-Digit Challenge*: [brief chapter index](Doc/siam_challenge_examples.md) and [mirror project source note](Doc/mirror_trajectory_project.md).
- Lecture 12: J. R. Shewchuk, [robust geometric predicates](https://www.cs.cmu.edu/~quake/robust.html). The course's Arb/Fraction filter uses a simpler implementation than the expansion-arithmetic algorithms described there.
- Optional advanced background for Lecture 10: S. M. Rump, [Verification methods](https://www.tuhh.de/ti3/rump/intlab/ActaNumerica2010.pdf), §13. The lecture proves its conservative contraction criterion directly.

## Software documentation

- [Python floating point](https://docs.python.org/3/tutorial/floatingpoint.html), [Fraction](https://docs.python.org/3/library/fractions.html), and [Decimal](https://docs.python.org/3/library/decimal.html).
- [gmpy2 contexts](https://gmpy2.readthedocs.io/en/stable/contexts.html).
- [python-flint concepts](https://python-flint.readthedocs.io/en/stable/general.html) and [Arb](https://python-flint.readthedocs.io/en/stable/arb.html).
- [Jupytext pairing](https://jupytext.readthedocs.io/en/latest/paired-notebooks.html) and [nbclient](https://nbclient.readthedocs.io/en/latest/client.html).

Record versions and input semantics when reproducing an experiment. A historical printed table need not exactly match a modern arithmetic environment.
