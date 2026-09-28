---
type: llm
weight: 1
---

Judge the reply as a first response to a real, busy user who gave no data.

PASS only if ALL hold:
- It does not endorse switching yet; it says to establish the facts first.
- It asks how "late" is defined and measured — against which date (their promise, our need date), and which event (shipped vs received) — and proposes pulling on-time data over a set of recent orders rather than relying on impressions.
- It checks our own side: e.g. whether orders were placed within the supplier's quoted lead time, whether we changed quantities/specs/forecasts late.
- It gives a concrete next step (what data to pull, or a short list of columns) and notes switching costs/risks.
FAIL if it simply agrees or disagrees with switching, or gives a generic supplier-selection checklist without measuring the lateness properly.
