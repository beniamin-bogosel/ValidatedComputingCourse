# Patriot failure — introductory example

Suggested placement: a short motivation in Lecture 01, revisited as a time-conversion/error-growth experiment in Lectures 02–03.

## References

- [User-supplied numerical-disasters page](https://www.iro.umontreal.ca/~mignotte/IFT2425/Disasters.html). Automated access was blocked when checked on 2026-09-11; its contents were not reviewed.
- Primary source: [GAO, *Patriot Missile Defense: Software Problem Led to System Failure at Dhahran, Saudi Arabia*, IMTEC-92-26](https://www.gao.gov/products/imtec-92-26), February 1992. [Full report](https://www.gao.gov/assets/imtec-92-26.pdf): printed pp. 5–6 explain the time conversion; p. 9 describes the incident; Appendix II, p. 15, tabulates error growth.

## Essential facts

On February 25, 1991, the Patriot battery at Dhahran failed to track and intercept a Scud that subsequently struck a barracks, killing 28 Americans. The battery had operated continuously for over 100 hours.

The clock counted integer tenths of seconds. Precision was lost when converting this count to a real-valued time using the computer's limited 24-bit registers. The resulting error increased with operating time and displaced the radar's predicted tracking region. Appendix II reports approximately 0.3433 seconds of timing error at 100 hours. These facts are documented in the GAO report linked above.

## Teaching use

Use the precise description **limited-precision time conversion and error growth**. Avoid presenting the incident as simply a loop repeatedly adding Python's binary64 `0.1`.

A future notebook can use an explicitly labelled simplified model: represent `1/10` exactly with `Fraction`, compare it with a truncated binary approximation, and multiply the conversion error by the number of clock ticks. Plot the error against elapsed time, then derive an enclosure. This illustrates the mechanism; it is not a reconstruction of the complete historical software.

Discuss how numerical error bounds depend on the operating range and duration, and how those assumptions should be tested and communicated. The example motivates validated computing without suggesting that interval arithmetic alone would have prevented every aspect of the failure.

Keep this as a brief historical reference until the opening notebooks are developed.
