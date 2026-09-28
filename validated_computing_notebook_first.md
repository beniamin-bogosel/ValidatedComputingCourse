# Notebook-First Format for a Validated Computing Course

## Recommendation

Yes: the course can be kept primarily in **Jupyter notebook format**.

For a course on validated computing, this is especially natural because the subject constantly alternates between:

- mathematical explanation;
- formulas;
- numerical experiments;
- plots;
- code;
- rigorous certificates;
- exercises.

A notebook lets the lecture move directly from theory to computation whenever necessary.

The recommended philosophy is:

$$
\boxed{
\text{explain}
\rightarrow
\text{experiment}
\rightarrow
\text{observe failure}
\rightarrow
\text{derive}
\rightarrow
\text{validate}
}
$$

---

# Why Notebooks Fit This Course

Validated computing is not purely theoretical and not purely programming-oriented.

A typical topic naturally has the structure:

```text
Mathematical statement
↓
ordinary numerical experiment
↓
numerical failure or uncertainty
↓
theoretical explanation
↓
validated method
↓
rigorous computational certificate
```

A notebook can represent this directly.

For example:

```text
Markdown: motivation / numerical pathology
↓
Code: reproduce the failure
↓
Markdown: explain why it happens
↓
Math: derive the relevant bound
↓
Code: test the bound
↓
Markdown: introduce interval formulation
↓
Code: compute a certified enclosure
↓
Exercise
↓
Code cell left for students
↓
Certificate / conclusion
```

This is arguably better suited to validated numerics than a traditional separation into:

- lecture slides;
- separate source code;
- separate exercise sheets.

---

# Example: Floating-Point Lecture

A Markdown section can introduce catastrophic cancellation.

Then immediately execute:

```python
import math

x = 1e16
print((x + 1) - x)

for n in range(40, 60):
    x = 2.0**n
    print(n, (x + 1) == x)
```

Then return to Markdown and explain:

- representable floating-point numbers;
- spacing;
- relative precision;
- why adding `1` eventually stops changing the number.

The code is not separate from the lecture.

It is part of the mathematical narrative.

---

# Example: Dependency Problem

A Markdown cell:

```markdown
## Dependency problem

For \(X=[0,1]\),

$$
X-X=[-1,1],
$$

although the real function

$$
x-x
$$

is identically zero.
```

Immediately followed by:

```python
X = Interval(0, 1)
X - X
```

Then continue with a student exercise.

```markdown
### Exercise

Compare the interval evaluation of

$$
f(x)=x(1-x)
$$

using

$$
x-x^2,
$$

$$
x(1-x),
$$

and

$$
\frac14-\left(x-\frac12\right)^2.
$$
```

This is exactly the kind of transition for which notebooks are very effective.

---

# Recommended Cell Types

A useful convention is to organize notebook material into three recurring categories.

## THEORY

Contains:

- definitions;
- explanations;
- propositions;
- formulas;
- short proofs;
- derivations.

Example:

```markdown
## Interval extension

An interval function \(F\) is an inclusion function for \(f\) if

$$
f(X)\subseteq F(X)
$$

for every admissible interval \(X\).
```

---

## EXPERIMENT

Contains executable code illustrating the mathematics.

Example:

```python
X = Interval(0, 1)

print(X - X)
print(X * (1 - X))
```

Typical goals:

- reproduce a floating-point pathology;
- compare equivalent formulas;
- visualize interval overestimation;
- show subdivision;
- verify a theorem computationally;
- generate a rigorous enclosure.

---

## EXERCISE

Contains student tasks.

Example:

```markdown
### Exercise

Implement interval multiplication.

Your function must satisfy:

$$
xy\in X\cdot Y
$$

for every

$$
x\in X,\qquad y\in Y.
$$
```

Then:

```python
def interval_mul(X, Y):
    # TODO
    pass
```

This gives the notebook a predictable structure throughout the course.

---

# Lecture Notebooks Versus Lab Notebooks

It is advisable to keep **lecture notebooks** and **student lab notebooks** separate.

The lecture notebook should contain:

- complete explanations;
- finished examples;
- demonstrations;
- short guided exercises;
- instructor-ready code.

The lab notebook should contain:

- tasks;
- incomplete code;
- questions;
- experiments;
- spaces for interpretation;
- possibly hidden or separate solutions.

For example:

```text
06_dependency.ipynb
```

could contain the polished lecture.

Then:

```text
lab06_dependency.ipynb
```

could contain:

```python
# TODO: implement subdivision-based range enclosure

def interval_range(f, X, depth):
    pass
```

This avoids filling the lecture notebook with long exercise solutions.

---

# Suggested Repository Structure

A clean repository could be:

```text
validated-computing/
├── README.md
├── notebooks/
│   ├── 01_intro.ipynb
│   ├── 02_floating_point.ipynb
│   ├── 03_stability.ipynb
│   ├── 04_interval_basics.ipynb
│   ├── 05_directed_rounding.ipynb
│   ├── 06_dependency.ipynb
│   ├── 07_centered_forms.ipynb
│   ├── 08_automatic_differentiation.ipynb
│   ├── 09_interval_newton.ipynb
│   ├── 10_nonlinear_systems.ipynb
│   ├── 11_global_optimization.ipynb
│   ├── 12_applications.ipynb
│   ├── 13_project_workshop.ipynb
│   └── 14_conclusion.ipynb
├── labs/
│   ├── lab01.ipynb
│   ├── lab02.ipynb
│   ├── ...
│   └── lab12.ipynb
├── solutions/
├── vc/
│   ├── __init__.py
│   ├── interval.py
│   ├── autodiff.py
│   ├── rootfinding.py
│   └── optimization.py
├── data/
├── figures/
├── assignments/
└── projects/
```

---

# Keep Notebooks Self-Contained

Avoid notebooks that only work if earlier notebooks were executed in the same Python session.

For example, Lecture 9 should not rely on an `Interval` class that exists only because Lecture 4 was executed beforehand.

Instead, place reusable material in a small Python package.

Example:

```text
vc/
├── interval.py
├── autodiff.py
├── rootfinding.py
└── optimization.py
```

Then notebooks can do:

```python
from vc.interval import Interval
```

or later:

```python
from flint import arb
```

This improves:

- reproducibility;
- debugging;
- grading;
- version control;
- student usability.

---

# Recommended Internal Structure of a Lecture Notebook

A typical notebook can follow this pattern.

## 1. Motivation

Explain the numerical problem.

Example:

> Newton's method finds a number close to a zero. How do we prove that a zero actually exists near that number?

---

## 2. Ordinary Numerical Experiment

Use normal Python.

```python
import math

def f(x):
    return x*x - 2

x = 1.4
```

Show the approximation.

---

## 3. Why This Is Not Yet a Proof

Discuss:

- rounding;
- truncation;
- stopping criteria;
- completeness;
- uniqueness.

---

## 4. Mathematical Tool

Introduce the required interval concept.

For example:

$$
N(X)
=
m-\frac{f(m)}{F'(X)}.
$$

---

## 5. Validated Algorithm

Implement it.

```python
def interval_newton(f, df, X):
    ...
```

---

## 6. Certificate

Produce something explicit.

```text
[1.4142135623, 1.4142135624]

contains exactly one zero of f.
```

---

## 7. Exercise

Students modify:

- function;
- domain;
- precision;
- subdivision strategy;
- stopping tolerance.

---

## 8. Failure Case

Give a case where the algorithm is inconclusive.

This is important.

Students should understand that:

> "Unable to certify" is not the same as "false."

---

# Notebook-First Teaching Style

A useful principle is:

> Do not write a long theoretical section and then move to a separate programming session.

Instead, introduce code exactly when it clarifies the mathematics.

For example:

```text
definition
→ 5-line experiment
→ observation
→ theorem
→ 10-line implementation
→ certificate
```

This makes the computational behavior part of the theory.

---

# Jupyter in VS Code

The notebooks can be edited and executed directly in VS Code.

A convenient stack is:

```text
VS Code
+ Python extension
+ Jupyter extension
+ Codex
```

This gives:

- Markdown rendering;
- LaTeX rendering;
- executable Python cells;
- inline plots;
- variable inspection;
- debugging;
- integrated terminal;
- Git integration;
- AI-assisted notebook development.

---

# Using Codex with the Notebook Repository

Codex can help create and revise:

- `.ipynb` notebooks;
- Python modules;
- exercises;
- examples;
- tests;
- Markdown explanations.

Possible requests include:

```text
Create Lecture 4 on interval arithmetic as a Jupyter notebook.

Use alternating Markdown and Python cells.

Start from the set definition of interval arithmetic.

Include:
- addition;
- subtraction;
- multiplication;
- reciprocal;
- division;
- dependency problem;
- 4 short exercises.

Use the local vc.Interval class when appropriate.
```

or:

```text
Add a numerical experiment after the section on catastrophic cancellation
showing failure of the naive quadratic formula.

Then add a stable version and compare relative errors.
```

The notebook-first repository makes this kind of incremental development natural.

---

# Jupytext: Strongly Recommended

Raw `.ipynb` files are JSON internally.

This can make:

- Git diffs;
- code review;
- manual editing;
- Codex patches

less readable.

A strong option is to use **Jupytext**.

Install with:

```bash
pip install jupytext
```

A notebook can then have a text representation such as:

```python
# %% [markdown]
# # Floating-Point Arithmetic
#
# We investigate IEEE 754 binary64 arithmetic.

# %%
x = 1e16
(x + 1) - x

# %% [markdown]
# The result is zero because the spacing between nearby
# floating-point numbers exceeds one at this scale.
```

This representation is:

- easy to read;
- easy to edit;
- friendly to Git;
- friendly to Codex;
- convertible to a normal notebook.

A good workflow is:

```text
.ipynb for teaching
+
.py or .md Jupytext mirror for editing/version control
```

---

# Suggested Notebook Naming

Use simple ordered names:

```text
01_intro.ipynb
02_floating_point.ipynb
03_stability.ipynb
04_interval_basics.ipynb
05_directed_rounding.ipynb
06_dependency.ipynb
07_centered_forms.ipynb
08_automatic_differentiation.ipynb
09_interval_newton.ipynb
10_nonlinear_systems.ipynb
11_global_optimization.ipynb
12_applications.ipynb
13_project_workshop.ipynb
14_conclusion.ipynb
```

This keeps both filesystem ordering and course ordering obvious.

---

# Suggested Lab Naming

Similarly:

```text
lab01_floating_point.ipynb
lab02_stability.ipynb
lab03_intervals.ipynb
lab04_directed_rounding.ipynb
lab05_dependency.ipynb
lab06_centered_forms.ipynb
lab07_autodiff.ipynb
lab08_roots.ipynb
lab09_systems.ipynb
lab10_optimization.ipynb
```

---

# Python Stack Inside the Notebooks

The recommended numerical progression remains:

$$
\boxed{
\texttt{float}
\to
\texttt{Fraction/Decimal}
\to
\texttt{gmpy2.mpfr}
\to
\text{student-built intervals}
\to
\texttt{python-flint / Arb}
}
$$

The notebook format makes it particularly easy to compare these arithmetic systems directly.

For example, one cell can compute using:

```python
float
```

the next using:

```python
Decimal
```

the next using:

```python
gmpy2.mpfr
```

and finally:

```python
flint.arb
```

Students can immediately compare:

- approximation;
- precision;
- rounding;
- exactness;
- enclosure.

---

# Final Recommendation

For this course, a **notebook-first model is strongly recommended**.

The main course artifact can be the notebook itself rather than a slide deck.

Use:

```text
Markdown
+ LaTeX
+ executable Python
+ plots
+ exercises
+ rigorous certificates
```

inside the same document.

A particularly effective teaching rhythm is:

$$
\boxed{
\text{Theory}
\to
\text{Code}
\to
\text{Failure}
\to
\text{Analysis}
\to
\text{Validated Code}
\to
\text{Certificate}
}
$$

This matches the subject matter of validated computing extremely well.
