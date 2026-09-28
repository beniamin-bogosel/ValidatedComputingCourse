# Tucker, Chapter 1 — examples for the opening lectures

Source: Warwick Tucker, *Validated Numerics*, Chapter 1, **§1.6: Examples of Floating Point Computations**. The PDF is available in this directory. Page numbers below are printed book pages.

- **Example 1.6.1, pp. 19–20: Rump's cancellation example.** Evaluating a two-variable expression at `(77617, 33096)` involves enormous terms whose exact sum is only `−2`. Floating-point results can be grossly wrong, including the wrong sign, and agreement across several precisions can be misleading. Useful for Lecture 01 motivation and Lecture 03 cancellation. Historical numerical outputs depend on the arithmetic environment; recompute the Python examples when authoring.
- **Example 1.6.2, pp. 20–21: a reasonable-looking polynomial.** Compare the expanded polynomial below, Horner evaluation, and the factored form near `t = 1`:

$$
p(t)=t^6-6t^5+15t^4-20t^3+15t^2-6t+1=(t-1)^6.
$$

  Cancellation can produce a jagged graph and misleading apparent roots or signs. This is an especially accessible example for Lecture/Lab 03: algebraically equivalent expressions can behave very differently numerically. Horner's method alone does not remove the difficulty. Discuss conditioning and evaluation error separately.

- **Example 1.6.3, pp. 21–22:** the following example encloses the sum of `1/k²` using a mathematically bounded tail and directed rounding of the finite computation. Revisit it when transitioning from numerical failures to rigorous enclosures.

Develop these examples when writing the relevant notebooks; no full reproduction is needed at the planning stage.
