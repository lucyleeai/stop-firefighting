---
type: llm
weight: 1
---

Judge the reply as a first response to a real, busy user who gave no data.

PASS only if ALL hold:
- It proposes measuring the process before fixing it: define start and stop (e.g. invoice received to payment made) and pull timestamps per step for a sample of invoices from the accounting/ERP system, separating waiting from work and spotting exceptions/rework (e.g. PO or price mismatches, missing approvals).
- It names the specific fields/steps to extract (a ready-to-use list of columns or steps), not just "collect data".
- It keeps payment controls (e.g. matching, approval, bank-detail verification) in place, or explicitly says not to remove them without a replacement.
- It still offers one or two things to try now, framed as trials.
FAIL if it only lists generic tips (automate AP, e-invoicing, pay faster) without a way to find where the time goes, or suggests dropping controls.
