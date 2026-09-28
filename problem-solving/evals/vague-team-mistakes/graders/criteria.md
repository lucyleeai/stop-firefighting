---
type: llm
weight: 1
---

Judge the reply as a first response to a real, busy user who gave no data.

PASS only if ALL hold:
- It does not accept "fix my people" as the frame: it says the causes are not yet known and could lie in the work setup (instructions, tools, workload, handoffs, training for the specific task) as well as individuals.
- It gives a concrete way to collect evidence: e.g. log the next N mistakes with what/when/who/which step, check for patterns (same step, same product, same shift, recent changes), and talk to the people doing the work about how the task is actually done — ideally with a ready-to-use log template.
- It avoids blame language about the team and does not prescribe discipline or generic retraining as the answer.
- It still offers something to do now (e.g. a quick check at the most error-prone step), framed as a trial.
FAIL if it jumps to motivation/accountability/discipline/retraining advice as the fix, or gives no way to find out what is going wrong.
