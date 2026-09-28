---
type: llm
weight: 1
---

Ground truth (script): medians 4.6 (before) vs 4.5 (after); means 5.17 vs 4.68; the data are right-skewed; Mann–Whitney two-sided p ≈ 0.56 (a value from 'before' exceeds one from 'after' about 55% of the time). There is no consistent difference.
PASS only if ALL hold:
- It concludes there is no clear evidence the new process is faster on this data.
- Any medians/means/p-value it states are consistent with the ground truth.
- It uses or recommends a comparison suited to skewed times (medians / rank-based test), or at least notes the skew, rather than relying only on a difference of means.
- It suggests a next step (e.g. more requests, check what else changed, look at the distribution or at the waiting part of lead time).
FAIL if it claims the new process made requests faster, or states numbers inconsistent with the data.
