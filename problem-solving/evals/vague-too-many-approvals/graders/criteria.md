---
type: llm
weight: 1
---

Judge the reply as a first response to a real, busy user who gave no data.

PASS only if ALL hold:
- It proposes mapping the current steps (who does what, in what order) and measuring where time goes (waiting vs work) for a sample of real requests.
- For each step/approval it asks what risk or failure it guards against and whether it is actually used or has caught anything — before removing it; it does not recommend cutting approvals blindly.
- It offers ways to cut waiting while keeping necessary controls (e.g. thresholds, parallel approvals, delegation, SLAs), framed as trials with a way to check the guarded risk does not return.
- It gives something ready to use (a table/template for the step review).
FAIL if it just lists steps to delete or generic "streamline" advice without the per-step what-does-it-guard review.
