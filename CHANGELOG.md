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
- **Read chart values directly.** Histograms, box plots, scatter plots and control charts now show value labels on their axes. Control charts also print the limit values at the end of each line.
- **Test the hand-over of a lasting fix.** A new case checks a fix that has held for 4 weeks: who owns the check, where it lives, how often it happens, what counts as the problem coming back and what to do then.

### Test results and limits

We tested 58 synthetic cases written for this project. They covered everyday work problems such as late suppliers, slow approvals, picking errors and kitchen delays. They also included 12 blind user personas, claims of a status without evidence, and the new methods. No skill, v0.1.0 and v0.2.0 were compared on the same cases.

The main model, gpt-6-sol, had 110 runs per version. Cases where wording matters most were run 3 times. The smaller model, gpt-6-luna, had 30 cases, 1 run each.

A separate model (gpt-6-sol) scored each reply against written checks without knowing which version produced it. Checks on blame and false status used 3 votes. Every run was also checked 3 times for severe failures: blaming a person, a number that contradicts the case data, or a false claim that something was done or solved.

The test agent had general working instructions on stating evidence and not inventing numbers, the same for all three versions. This may make the measured differences smaller, not larger.

| Version | gpt-6-sol: checks passed | gpt-6-luna: checks passed |
|---|---:|---:|
| No skill | 289/364 (79.4%) | 83/109 (76.1%) |
| v0.1.0 | 316/364 (86.8%) | 87/109 (79.8%) |
| v0.2.0 | 325/364 (89.3%) | 95/109 (87.2%) |

With gpt-6-sol, v0.2.0 gained +9.9 percentage points over no skill (95% range across cases: +5.2 to +14.9), a clear gain. Against v0.1.0, it gained +2.5 points (range −0.5 to +5.5), which is not conclusive.

With gpt-6-luna, the gain over no skill was +11.0 points (range +5.0 to +17.3). Against v0.1.0, it was +7.3 points (range −0.9 to +15.5), which is not conclusive. These ranges show uncertainty in the gains; a range that crosses zero leaves open whether there was an improvement.

With v0.2.0, no severe failures were verified in 110 gpt-6-sol runs. The smaller model had one severe failure: a wrong average time. In that run, it did not open the skill or run a bundled script; it worked the number out itself. It opened the skill in 13 of 30 runs with v0.2.0, compared with 7 of 30 with v0.1.0.

The new hand-over case showed no improvement: no skill passed 15/15 checks, v0.1.0 passed 14/15, and v0.2.0 passed 14/15. The base model already handles it.

Treat these results as indicative: the test set is our own. The skill guides and computes, but cannot by itself make an agent load it or enforce a change. It is not a substitute for professional advice on safety-critical, legal or medical decisions.

## 0.1.0 — 2026-09-28 — first public release
