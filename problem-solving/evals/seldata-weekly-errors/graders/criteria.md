---
type: llm
weight: 1
---

Ground truth (script): with the counts, a p chart (proportion defective with limits that vary by weekly volume) has centre ≈ 4.07%; weeks W19 and W20 are beyond the upper limit; W18 is not; no other week signals on rules 1–2. (An individuals chart on the percentages would also flag W16 — a known distortion when counts are ignored.)
Whether it used the counts is checked separately from the tool call; do not require the reply to name the chart type.
PASS only if ALL hold:
- It identifies W19 and W20 as signals of a real change, and does not flag W16 as a signal.
- Any centre line or limit it states is consistent with the ground truth (centre about 4.1%).
- It recommends looking for what changed around W19 (and treats it as a lead to investigate), not a vague "keep monitoring".
FAIL if it flags W16, misses W19/W20, or states limits/percentages inconsistent with the data.
