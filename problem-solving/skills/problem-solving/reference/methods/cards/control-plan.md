# Card: keep the fix in place — control plan and handover

**Use when** a change is about to go live or has just gone live, or a problem came back after an earlier fix. **Skip** for a one-off analysis.

**Needs** the change, the step or input it controls, who does that work.
**Gives** a filled control table, a handover list, and the date of the first check.

## Choose the kind of control (strongest first)
1. **Make the error impossible or obvious** — a required field, a fixture that only fits one way, a system block, a colour that differs. Use when the failure is serious or hard to catch later.
2. **Watch it with a chart** — when the result drifts slowly and is measured regularly (`../selector.md` E).
3. **Inspect a sample** — when neither is practical. Inspection finds problems; it does not prevent them.
"Remind people" and "be careful" are not controls.

## Control table
| What is controlled (step or input) | Requirement | How it is checked | How often | Who | If it fails (reaction) |
|---|---|---|---|---|---|

Every row has a reaction: what to do with the affected work, whom to tell, when to reopen the case.

## Critical inputs: set the operating window
For each cause that is now controlled, write the window it must stay in (the
"how much" column): the setting, its range, and the evidence for that range —
a trial, a factorial run (`experiment.md`) or a regression on real data. A range
copied from habit is not evidence. Where a supplier delivers the input, the
window becomes part of what you agree with them.

## Each row traces back
Every control row names the cause it guards (ledger) and the risk it answers
(`trial-and-risk.md`), so that when a control is changed or dropped, you can
see what it was protecting.

## Going live — the implementation plan
- What changes, from which date, for whom.
- Who tells each person who does the work, how, and how you will know they got it (a test run, the first checked occurrence) — not just "sent an email".
- The documents, forms, settings or tool instructions that change, and who updates them.
- Before / trial / after on one chart: add a `phase` column and run `stats_tools.py chart imr data.csv` (limits per phase).

## Handover
- The person who does the work has the new way **at the point of work** (on the form, the bench, in the tool, in the instructions loaded at the start) — not only in a message.
- People who were away when it changed: who tells them, how you know they got it.
- Settings that must not drift back: who may change them.
- Where else the same problem exists, and whether to copy the fix (as a new trial, not assumed to work).
- When the improvement team steps back: who owns the table above.
- Upkeep: when the plan is reviewed (a date, and after any process change), how the measurement itself stays reliable (`measurement-check.md` again after staff or tool changes), and who checks occasionally that the controls are still followed.

## Status words
*In place* = evidence the real work uses it. *Held* = a later period or occurrence shows it still works. Neither is claimed from the plan alone.

Sources: ASQ, "Quality Control Plans" — https://asq.org/quality-resources/quality-plans ; ASQ Quality Glossary (poka-yoke: prevents or makes errors obvious) — https://asq.org/quality-resources/quality-glossary ; NIST/SEMATECH e-Handbook ch. 6 (process monitoring) — https://www.itl.nist.gov/div898/handbook/pmc/pmc.htm
