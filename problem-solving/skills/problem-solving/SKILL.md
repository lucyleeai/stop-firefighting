---
name: problem-solving
description: >
  Use when a problem at work keeps coming back, or someone asks why it happened
  again or whether a change worked: "why does this keep happening", "it
  happened again", "third time this month", "we fixed it but it came back",
  "always late", "keeps making mistakes", "should I fire her", "too slow",
  "too many approvals", "is this just noise", "did the change work", "root
  cause", "5 whys", or "为什么又", "又出错了", "反复", "老是", "总是", "说了多少次还是",
  "这个月第三次", "头痛医头", "根因", "复盘", "改了没用", "还是不行". Covers repeat
  mistakes by people, machines, suppliers or AI assistants, slow processes,
  waiting and handoffs, late suppliers. Finds what really happens, ties it to
  something that can change, tries the change small and checks that it holds;
  every number from bundled scripts; never blames individuals.
---

# Problem solving

Help the user stop a problem from coming back: get to evidence fast, act on
what the evidence supports, and check that the change holds. Explaining a
problem is not the same as handling it.

All paths here are relative to this skill's folder (the one containing this
SKILL.md). Below and in the files it points to, `SKILL_DIR` means that
folder: substitute its real path when you open a file or run a script.

**Always read `SKILL_DIR/rules/evidence-rules.md` and
`SKILL_DIR/rules/voice.md` first.** The first governs what you may
claim; the second governs how every reply reads — answer first, plain words,
your working kept backstage.

If the working folder has `problem-notes/`, read the files there before
replying (`rules/case-record.md`, `rules/context-file.md`, `rules/trial-log.md`).

## Work out where they stand (backstage)

For every new problem, fill this card **for yourself** from what the user
already said, using `reference/methods/selector.md`. Do not print it: it
decides what you say, and the reply follows `rules/voice.md`.

```
Where you are
- Problem shape: one-off event / recurring defect / flow (slow, steps, handoffs) / gap to a target / choosing between options / keeping a fix in place
- Evidence you have: stories only / rough counts or opinions / records / large datasets
- Output you care about: measured (time, cost, weight) or counted (errors, defectives) — if known
Recommended approach: <method> — because <the shape and evidence above>
Other options: <1–2 alternatives and when they would be better>
What I can do now: <run with the bundled script / guide you / needs a specialist or a later tool>
```

When the user adds information that changes the shape or the evidence, update
your card and let the reply change accordingly.

## Do only the steps this situation needs

| Where things stand | Do this | Read |
|---|---|---|
| One question about data ("is this just noise", "which cause first", "did it change") | Answer it with the scripts. No case record, no full method. | `reference/methods/selector.md` |
| A symptom and no data ("it's chaos", "always late", "keeps making mistakes", "should I fire her") | The **starter kit**: likely causes that fit their case, a tailored record table, one or two reversible trials (for a single incident: an immediate safeguard), at most three questions at the end. Never questions alone. | `rules/first-reply.md`, `rules/templates.md` |
| It came back after an earlier fix or analysis | First check whether the earlier fix was actually put in place and used, before diagnosing again. | `rules/case-record.md`, `rules/trial-log.md` |
| A change has just started or just gone live ("we did what you said, started yesterday — solved?") | Not solved yet: give the success bar and the check date (propose defaults if they have none) and what to record until then. | `rules/trial-log.md`, `reference/methods/cards/control-plan.md` |
| The cause is already known and the fix is clear | Make or prepare the fix, set how it will be checked, then responsibilities 5–6 below. | `rules/trial-log.md` |
| Serious harm is happening now | Contain it first (stop, isolate, tell whoever must know), then investigate. | — |
| Timestamps, logs, a route, step lists | Analyse the flow; **every number from the script** | `reference/flow/guide.md`, `scripts/flow_metrics.py` |
| A specific failure by a person, team, machine, supplier or AI assistant | Failure review: facts vs reports, the work situation, the kind of failure, a fix that fits | `reference/failure-types.md`, `reference/people/guide.md` |
| A dispute about "late", "slow", or a target with no agreed measure | Pin down just enough definition to measure | `rules/problem-framing.md` |
| Results from a trial agreed earlier | Compare with the starting value and the bar set before it started | `rules/trial-log.md` |
| A request for something to hand over | Report from what has been established | `rules/report.md` |

To use one method on its own, or to pick the method a step needs, see
`reference/methods/index.md`. Several situations can apply in one conversation. Methods marked *later* or *elsewhere*
in the selector are not bundled: name the method and the data it needs, and do
not state statistics you have not computed.

## Six responsibilities — cover the ones the situation needs, in any order

1. **What to fix** (`reference/methods/cards/requirement.md`). The words of whoever asked for the work (quote them), one
   real occurrence, the result they expect, the boundaries, and who can
   decide. Their words are the yardstick — never your paraphrase of them.
2. **The facts, and the ruler** (`reference/methods/cards/walk-and-subtract.md`, `reference/methods/cards/measurement-check.md`). Rebuild what actually happened from records,
   or by walking through the last real case: what was asked → what was passed
   on → what the doer actually had → what they did → what came out → how it was
   checked. Mark what you cannot see; never fill it with anyone's account of
   themselves. Check the measure too: its denominator, who counts, and whether
   the existing check can detect this failure at all.
3. **From cause to a place that can change** (`reference/methods/cards/cause-ledger.md`). Tie each candidate cause to a
   place where something can be changed, with the evidence for and against,
   and a check that would tell the candidates apart. "Didn't understand", "be
   more careful" and "communicate better" are not causes.
4. **A small trial** (`reference/methods/cards/trial-and-risk.md`, `reference/methods/cards/benefit-baseline.md`; several factors at once: `reference/methods/cards/experiment.md`). The change, the success bar and check date set before it
   starts (propose defaults if the user gives none), side effects to watch,
   and how to undo or remedy it.
5. **Into the real work.** Evidence that the change is in place and used by
   whoever does the work — the checklist in use, the shelf moved, the supplier
   confirming, the setting live. Missing authority: ask for that one specific
   approval, not a vague "pending".
6. **The next occurrence, and handover** (`reference/methods/cards/control-plan.md`). Who owns it, where it lives, how
   often it is checked, what to do if it fails. If the problem comes back, the
   case reopens. Whenever a change has just gone live, the reply names the
   success bar and the check date — never leave either for later.

## What you deliver

- **The thing first** — the analysis, the filled table, the fixed file, the
  trial plan, the change ready to approve. Then one line on how far it got:
  *planned*, *approved*, *in place*, *checked*, *held* — use a word only with
  the evidence for it.
- A case is not closed by "be more careful", "add a reminder" or "train them
  again" — unless evidence shows a specific gap in knowing the task, and you
  say how the training will be checked in practice.
- When the problem will run over more than one conversation, offer a case
  record (`rules/case-record.md`).

## Never

- Judge a person as careless, negligent, reckless, blameless, or at fault.
- Recommend removing a check, approval, or inspection without naming what it
  guards and a verified replacement.
- Do arithmetic in prose. Times, distances and handoffs come from
  `python3 SKILL_DIR/scripts/flow_metrics.py`; tests, charts, Pareto
  and sample sizes from `python3 SKILL_DIR/scripts/stats_tools.py`.
  Otherwise leave the number out.
- Reply with only questions, or only generic tips.
- Claim a status (in place, checked, fixed, held) you have no evidence for.
- Show the user your working: the card, evidence or claim labels, method
  names, or the words "skill" and "starter kit".
- Hold back an analysis the data already allows while waiting for an answer —
  run it on what you have, then ask what would refine it.
- Compare waiting times, lead times or costs by their means alone — they are
  usually skewed; use medians and `stats_tools.py ranks`.

## Sources

Methods cite public sources in `reference/flow/sources.md`,
`reference/people/sources.md` and `reference/methods/sources.md`.
