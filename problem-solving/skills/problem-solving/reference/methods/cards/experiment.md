# Card: several factors at once — a two-level experiment

**Use when** two to five things you can set may each matter, and may matter together (shift pattern × checklist, template × send time, temperature × time, supplier × batch size). **Skip** when only one thing changes (use a simple trial), or when you cannot set the factors on purpose (then you only have observations — use `regress` and treat results as associations).

**Needs** the factors, a low and a high setting for each, one result to measure, and permission to run the combinations.
**Gives** a randomised run sheet, then which factors and combinations actually move the result.

## Steps
1. **Pick 2–5 factors and two settings each**, far enough apart that a real effect would show, safe enough to run.
2. **Design:** `stats_tools.py doe design <k> --reps 2` — every combination, in random order. Repeats (reps ≥ 2) let you tell effects from noise; with no repeats the script uses a noise estimate from the small effects, which needs most effects to be small.
3. **Run it as written.** Same measure as the baseline, everything else held steady, odd events noted.
4. **Analyse:** `stats_tools.py doe analyze runs.csv --factors A,B,C --response y`. Read the effects (change from low to high) and interactions (A:B — the effect of A depends on B).
5. **Confirm** the best combination with a few extra runs before adopting it, then go to `trial-and-risk.md` and `control-plan.md`.

## Rules
- Do not change one factor at a time when factors may interact: it misses the interaction and can point to the wrong setting.
- Effects hold only inside the tested range and conditions; another line, site or season is a new trial.
- More than five factors, or factors that cannot be set to two levels: name a screening design and involve someone who designs experiments.

Sources: NIST/SEMATECH e-Handbook ch. 5 (two-level full factorial designs; randomisation; interactions) — https://www.itl.nist.gov/div898/handbook/pri/section3/pri3331.htm ; Lenth, R. V. (1989). Quick and easy analysis of unreplicated factorials. *Technometrics* 31(4), 469–473.
