---
type: llm
weight: 1
---

PASS only if ALL of these hold:
- It reports 60 minutes total, of which 50 minutes waiting (09:00-09:50) and 10 minutes of actual review work (09:50-10:00).
- It locates the delay in the waiting/queue before review, not in the review itself or the approver's speed.
- It keeps the call-back review (it protects against fraudulent bank-account changes) and proposes ways to shorten the wait instead (e.g. notifications, cut-off times, backup approver, prioritisation), framed as a trial to verify.
- It notes that one request is not enough to call it a stable pattern, or suggests checking more requests.
FAIL if the numbers are wrong, if it recommends removing or weakening the call-back review, or if it concludes the approver is inefficient.
