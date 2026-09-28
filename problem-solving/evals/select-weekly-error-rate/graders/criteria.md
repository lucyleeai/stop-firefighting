---
type: llm
weight: 1
---

PASS only if ALL hold:
- It tells the user where they stand (recurring measure over time, records exist, the output is a counted proportion) and recommends a control-chart style check for stability over time.
- It recognises the weekly figures are proportions (counted data) and asks for, or says it needs, the weekly order counts and error counts (or at least the number of orders per week) to set proper limits — e.g. a p chart — rather than treating the percentages as ordinary measurements without comment.
- It does not declare "something changed" or "it's just noise" as a settled statistical conclusion from these few numbers without that data, and does not invent control limits or p-values.
- It gives a concrete next step (what data to pull, how many weeks).
FAIL if it computes or asserts limits/significance without the counts, or gives only generic advice.
