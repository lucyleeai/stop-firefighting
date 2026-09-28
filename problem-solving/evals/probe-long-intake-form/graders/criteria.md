---
type: llm
weight: 1
---

The expert move: treat each question as a control. For each: what failure it was added to prevent, whether it has actually caught anything, whether the answer is used by anyone downstream, and whether the system/master data could supply it automatically. Remove or merge those that are unused or duplicated, automate what can be looked up, keep true controls, and trial removals with monitoring for the specific failure they guarded.
PASS only if it proposes a per-question review that asks (a) what failure/risk it was added for and (b) whether the answer is actually used or has ever caught anything, plus (c) automating/pre-filling from existing systems where possible, and (d) trialling removals with a way to detect the guarded failure returning.
FAIL if it only suggests generic simplification (conditional logic, shorter form, user research) without the per-question "what does it guard / is it used / can the system supply it" review and a monitored trial.
