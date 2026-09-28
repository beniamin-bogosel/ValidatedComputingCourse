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
# # Worked peer audit · Mirror project
#
# **Teaching example:** this is a model audit of a deliberately overstated draft, not a record of an external person's review. The draft uses the standard exact inputs, T=3 and 53 bits, but claims coordinate widths below 10^-20. The corrected model uses 100 bits.
#
# ## Claim and reproduction
#
# The intended claim concerns the final-time position and distance for the ideal integer-lattice mirror model. Reproduce both precision settings and inspect their exact widths. The floating-point display alone cannot establish the requested width.

# %%
from fractions import Fraction
from vc.mirrors import trace_lattice, final_distance

target_width = Fraction(1, 10**20)
draft = trace_lattice("3", 53)
revised = trace_lattice("3", 100)
for name, result in [("draft", draft), ("revised", revised)]:
    print(name, result.status, "widths:", [float(part.width()) for part in result.position])
assert draft.status == revised.status == "complete"
assert any(part.width() > target_width for part in draft.position)
assert all(part.width() <= target_width for part in revised.position)
assert final_distance(revised).width() <= target_width

# %% [markdown]
# ## Proof-condition and event audit
#
# The unit-speed reflection identity supplies the reachable-region argument. All lattice centers in that region are enumerated. For each completed event, the candidate checks must establish a positive simple entrance time strictly before competing events and before the remaining-time horizon. Departure from the current circle must be positive. The final flight must miss all remaining candidates before T.
#
# The notebook and helper code use Arb operations and exact endpoint extraction. Position, direction, and elapsed time are enclosed; dependencies may widen bounds but do not invalidate inclusion under the stated model. This audit checks the recorded inequalities and inspects the corresponding code; it does not formally verify the arithmetic library.

# %%
from vc.intervals import RationalInterval as Interval
from vc.mirrors import select_first

previous_time = Interval(0)
assert len(revised.checks) == len(revised.collisions) + 1
for event, checks in zip(revised.collisions, revised.checks):
    assert len(checks) == len(revised.centers)
    assert {check.center for check in checks} == set(revised.centers)
    action, selected = select_first(checks, Interval(3) - previous_time)
    assert action == "collision" and selected.center == event.center
    assert event.departure.lo > 0
    previous_time = event.elapsed
final_checks = revised.checks[-1]
remaining = Interval(revised.final_time) - previous_time
assert len(final_checks) == len(revised.centers)
assert {check.center for check in final_checks} == set(revised.centers)
for check in final_checks:
    assert not check.status.startswith("inconclusive")
    if check.status == "hit":
        assert check.time.lo > remaining.hi
print("Recorded collision decisions support the revised short-time claim.")

# %% [markdown]
# ## Findings and author response
#
# | Finding | Effect | Correction and response |
# |---|---|---|
# | The draft treated trajectory completion as meeting a 10^-20 width target | The time-3 enclosure is valid, but its claimed accuracy is unsupported | Add explicit exact width checks; rerun from the original inputs at 100 bits |
# | Decimal display rounded both endpoints to the same visible number | The display concealed the actual interval width | Print exact endpoints and a separate width; export fraction strings |
# | The interpretation must specify the shortened horizon | A time-3 result does not answer the original time-10 SIAM question | State T=3 in the claim, certificate, and final discussion |
#
# The revised computation reaches time 3 and meets all stated coordinate and distance width targets. It certifies the mirror sequence (1,0), (−1,1), (0,2). The target is an absolute interval-width bound, not an automatic claim about correctly rounded decimal digits.
#
# ## Outcome
#
# **Supported under stated assumptions for the revised claim.** The reviewed scope is the ideal short-time model and its displayed event inequalities. Tangent events, a general mirror geometry, and the original time-10 result are outside this model audit. The completed project includes low-precision, uncertain-input, and collision-budget limitations. A classroom peer should still independently rerun and inspect the submitted notebook and record their own findings.
