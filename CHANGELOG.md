# Changelog

## 0.2.0 — 2026-10-16

- **Return finished work.** The skill now aims to hand back an analysis, filled table, fixed file, trial plan, or change ready to approve. It then states how far it got: planned / approved / in place / checked / held. Each status needs evidence. “Be more careful” or “add a reminder” does not close a case.
- **Use only the steps needed.** A single data question gets a direct answer. A recurring problem starts by checking whether the earlier fix was really in place. A change that just went live gets a success bar and a check date.
- **Cover six responsibilities as needed.** Name what to fix in the asker's words; check the facts and whether the measure can be trusted; trace the cause to something that can change; run a small trial; put the change into real work; and plan for the next occurrence and handover.
- **Review observable failures without blame.** This covers people, teams, machines, suppliers, software and AI assistants. Look for a request changed at handover, missing or outdated information, a skipped step, or a check that tests the wrong thing.
- **Resume a case across conversations.** An optional `problem-notes/` record lives in the user's project.
- **Use method cards on their own.** Cards cover requirements and boundaries; whether a measure can be trusted; walking the real work and removing steps; cause tracking; small trials and what they could break (severity first, no multiplied risk scores); two-level experiments; control plans and handover; and benefits and added burden.
- **Add script commands using only the Python standard library.** These cover control charts with all eight Nelson rules and before/after phases; process capability, which refuses an unstable process; correlation and regression; rater agreement (kappa); gauge studies; two-level factorial design and analysis; normality tests; decision matrices that check whether the winner survives weight changes; histograms, box plots and scatter plots; path crossings; and the share of lead time spent on actual work.
- **Check calculations against SciPy and statsmodels.** All 9,412 comparisons matched (`dev/verify_against_scipy.py`).
- **Recognize more English and Chinese requests.** Triggers include “it happened again,” “we fixed it but it came back,” “为什么又” and “改了没用.”

### Test results and limits

These results are indicative. They use our own synthetic test set. A separate model scored the replies without knowing which version produced them.

Across 57 cases with gpt-6-sol:

| Version | Checks passed |
|---|---:|
| No skill | 78.5% |
| v0.1.0 | 86.5% |
| v0.2.0 (before final fixes) | 89.1% |

After the final fixes, only the eight cases that had regressed were rerun, going from 87/102 to 98/102 checks passed. The full 57-case set was not rerun after the final fixes. No severe failure—personal blame, a wrong number, or a false “done”—was verified in the final retest.

With the smaller gpt-6-luna model, the skill was opened in only about half the runs, so the gain was small. With smaller models, call the skill by name.

The skill guides and computes, but cannot by itself make an agent load it or enforce a change. It is not a substitute for professional advice on safety-critical, legal or medical decisions.

## 0.1.0 — 2026-09-28 — first public release
