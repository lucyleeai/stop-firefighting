# Card: can the ruler be trusted?

**Use when** a number will decide something — a rate, a count, an "on time" share, a pass/fail check, an automated test or review gate. **Skip** for one-off estimates nobody will act on.

**Needs** how the number is produced: who or what records it, from which record, by which definition.
**Gives** a short verdict — usable / usable with limits / not usable yet — and what to fix in the measure first.

## Questions, in order
1. **Definition.** Is "late", "error", "done" written down, and do the people counting use the same one? Test: give two people the same five cases.
2. **Denominator.** Is there one? Counts without the number of items handled measure workload, not quality. Turn counts into rates with the script.
3. **Coverage.** Which cases never get recorded (weekends, phone orders, errors fixed quietly, complaints that go elsewhere)?
4. **Repeatability.** Would the same person, or two people, record the same item the same way?
   - Judgements (pass/fail, category, "late", a reviewer's or an AI grader's verdict): have 2+ raters judge the same 30–50 items, plus a reference answer if one exists → `stats_tools.py agree ratings.csv --standard reference` (kappa, % agreement, accuracy per rater).
   - Measured values (weight, time, size): about 10 items × 2–3 people × 2–3 repeats → `stats_tools.py grr data.csv --tol <tolerance>` (how much of the variation is the measurement itself).
   - Instruments: also resolution, bias, drift.
5. **Does the check see this failure?** A check can pass while the real problem goes through: a gate that looks for a word or a file, not for the result; an inspection after the point where the error is made. Write one failing example and see whether the check stops it.
6. **Who benefits from the number?** If the people counted also do the counting, expect under-reporting; look for a second source.

## Then
- Not usable yet → fix the measure first (a definition, a log with a denominator, a second recorder) and say which conclusions wait.
- Usable with limits → state the limit in the same sentence as the result.

Sources: Cohen, J. (1960). A coefficient of agreement for nominal scales. *Educational and Psychological Measurement* 20(1); Fleiss, J. L. (1971). Measuring nominal scale agreement among many raters. *Psychological Bulletin* 76(5) ; NIST/SEMATECH e-Handbook §2.4 (measurement system analysis: gauge studies, bias, repeatability) — https://www.itl.nist.gov/div898/handbook/mpc/section4/mpc4.htm ; ASQ Six Sigma Green Belt Body of Knowledge 2022 (measurement system analysis; data collection) — https://www.asq.org/cert/resource/pdf/certification/2022-SSGB-BoK.pdf
