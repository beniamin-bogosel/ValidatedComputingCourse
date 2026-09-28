# ---
# jupyter:
#   course:
#     kind: instructor_solution
#   jupytext:
#     cell_metadata_filter: tags
#     formats: ipynb,py:percent
#     notebook_metadata_filter: kernelspec,jupytext,course
#     text_representation:
#       extension: .py
#       format_name: percent
#       format_version: '1.3'
#       jupytext_version: 1.19.5
#   kernelspec:
#     display_name: Python (Validated Computing)
#     language: python
#     name: validated-computing
# ---

# %% [markdown]
# # Instructor solution · Lab 09 · Certify roots and account for the search
#
# **Preparation:** [Lecture 09](../notebooks/09_validated_roots.ipynb).
#
# **Time:** 2 hours plus 30–60 minutes homework. Complete the local interval Newton decision routine, then use supplied search scaffolding to maintain coverage of the possible root set.

# %%
from fractions import Fraction
import inspect
from vc.intervals import RationalInterval as Interval
from vc.autodiff import Dual
from vc.roots import RootDecision, isolate_roots

def cubic(x):
    return (x+2)*(x-1)*(x-3)

def derivative(X):
    return cubic(Dual(X, Interval(1))).derivative


# %% [markdown]
# ## Task A · Implement the local decision (50 minutes)
#
# Implement these decisions in order: exclude if the function image misses zero; request a split if the derivative includes zero; compute interval Newton; exclude on empty intersection; certify on strict interior inclusion; contract if the retained width is less than half the input width; otherwise request a split. Return a `RootDecision` with the supporting quantities. Match the status strings in the starter.

# %%
def student_inspect(evaluate, derivative, domain):
    image = evaluate(domain)
    if not image.contains(0):
        return RootDecision(domain, image, "excluded_range")
    slopes = derivative(domain)
    if slopes.contains(0):
        return RootDecision(domain, image, "split", slopes)
    center = Interval(domain.midpoint())
    newton = center - evaluate(center)/slopes
    retained = domain.intersection(newton)
    if retained is None:
        return RootDecision(domain, image, "excluded_newton", slopes, newton)
    if domain.lo < newton.lo and newton.hi < domain.hi:
        return RootDecision(domain, image, "certified", slopes, newton, retained)
    if retained.width() < domain.width()/2:
        return RootDecision(domain, image, "contract", slopes, newton, retained)
    return RootDecision(domain, image, "split", slopes, newton, retained)


# %%
sqrt_two = student_inspect(lambda X: X.square()-2, lambda X: 2*X, Interval(1, 2))
assert sqrt_two.status == "certified"
assert sqrt_two.retained.lo**2 < 2 < sqrt_two.retained.hi**2
excluded = student_inspect(lambda X: X.square()+1, lambda X: 2*X, Interval(-1, 1))
assert excluded.status == "excluded_range"
multiple = student_inspect(lambda X: X.square(), lambda X: 2*X, Interval(-1, 1))
assert multiple.status == "split"
print("sqrt(2) certificate:", sqrt_two)

# %% [markdown]
# **Worked explanation:** For any root r in X, the mean value theorem gives r=m−f(m)/f′(ξ), so the root lies in both X and its Newton image. Division is justified only when the derivative bound excludes zero. The bounded interval arithmetic intentionally rejects a denominator containing zero; splitting retains the root possibilities while seeking a region where a theorem applies.

# %% [markdown]
# ## Task B · Use and audit the search (45 minutes)
#
# Run the supplied driver with your decision callback. Inspect the driver source and identify what happens to every box after exclusion, certification, contraction, splitting, or budget exhaustion. Check the known cubic roots independently.

# %%
print(inspect.getsource(isolate_roots))
search = isolate_roots(cubic, derivative, Interval(-3, 4), inspect=student_inspect)
print(search.status)
for certificate in search.certified:
    print(certificate.domain, "->", certificate.retained)
print("Unresolved:", search.unresolved)

# %%
assert search.status == "complete"
assert len(search.certified) == 3 and not search.unresolved
for certificate, root in zip(search.certified, [-2, 1, 3]):
    assert certificate.retained.contains(root)
for first, second in zip(search.certified, search.certified[1:]):
    assert first.retained.hi < second.retained.lo
for decision in search.decisions:
    for root in [-2, 1, 3]:
        if decision.domain.contains(root):
            assert not decision.status.startswith("excluded")
            if decision.retained is not None:
                assert decision.retained.contains(root)

# %% [markdown]
# **Worked explanation:** The search invariant accounts for every original root, all three returned certificates prove existence and uniqueness in their respective domains, the root enclosures are disjoint, and no unresolved intervals remain. The algebraic roots independently check this run. The tolerance stops undecided small boxes; it does not promise a target width for certified enclosures or turn unresolved boxes into root certificates.

# %% [markdown]
# ## Task C · Report limitations honestly (35 minutes plus homework)
#
# Run a small budget, a double root, and a boundary root. For each case list certified and unresolved regions. Do not convert an unresolved interval into a root merely because it is small.

# %%
limited = isolate_roots(cubic, derivative, Interval(-3, 4), max_steps=2, inspect=student_inspect)
double = isolate_roots(lambda X: X.square(), lambda X: 2*X, Interval(-1, 1),
                       tolerance="1/100", inspect=student_inspect)
boundary = isolate_roots(lambda X: X, lambda X: Interval(1), Interval(0, 1),
                         inspect=student_inspect)
for name, result in [("budget", limited), ("double", double), ("boundary", boundary)]:
    print(name, result.status, "unresolved:", result.unresolved)
    assert result.unresolved
for root in [-2, 1, 3]:
    possible = limited.unresolved + [item.retained for item in limited.certified]
    assert any(part.contains(root) for part in possible)
assert any(part.contains(0) for part in double.unresolved)
assert any(part.contains(0) for part in boundary.unresolved)

# %% [markdown]
# **Worked explanation:** The budget-limited run accounts for possible roots through certified and unresolved regions, without a complete root count. The double-root run preserves zero but cannot divide by its zero-containing derivative enclosure. The boundary run reaches {0} but fails the chosen strict interior criterion. Exact substitution could certify the point as a root under an additional rule; adjacent closed search boxes share endpoints, so such point certificates would need deduplication before counting roots.
