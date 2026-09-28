---
type: llm
weight: 1
---

Judge the reply as a first response to a real, busy user who gave no data.

PASS only if ALL hold (the reply may be in Chinese):
- It proposes observing/measuring before redesigning: e.g. tracing pickers' actual routes on a floor plan with a scale, and/or counting how often each item/location is picked (pick frequency).
- It gives a concrete, ready-to-use way to do this (steps or a table with named columns).
- It suggests changes tied to what the data would show (e.g. putting fast-moving items closer to the dispatch area, batching orders, better pick routes), framed as trials with a way to check the walking actually dropped.
FAIL if it only lists generic warehouse-efficiency tips without a way to measure the walking first.
