---
type: llm
weight: 1
---

Judge the reply as a first response to a real, busy user who gave no data.

PASS only if ALL hold:
- It explains that the amount of overfill needed depends on how much fill weights vary, so the first step is to measure: weigh a sample of bags and look at the spread, ideally split by filler/head, shift or product.
- It does not simply recommend lowering the setpoint by some amount without data.
- It mentions the legal/regulatory limits on underweight packs (average quantity / tolerable negative error or equivalent) as a constraint.
- It gives a concrete sampling plan or template.
FAIL if it just says "reduce the target weight" or gives generic tips without the measure-variation-first step.
