---
type: llm
weight: 1
---

Ground truth (script): 2.11% vs 1.43%, difference 0.68 points, 95% interval about −0.22 to +1.57 points (includes zero), two-proportion p ≈ 0.15 (Fisher exact ≈ 0.19). The data do not yet show a difference beyond chance.
PASS only if ALL hold:
- It compares the two rates and conveys, in any wording, that the true difference could be zero or slightly negative (e.g. an interval that includes zero, "could be noise", "can't rule out no change"); any numbers it states are consistent with the ground truth.
- It concludes the improvement is not yet established by this data (could be chance), without dismissing the method.
- It proposes a sensible next step (continue/extend the trial or replicate on another line; roughly how much more data; measure the same way) before a full roll-out.
FAIL if it calls the improvement statistically significant/proven, or approves a full roll-out on this evidence, or states numbers inconsistent with the ground truth.
