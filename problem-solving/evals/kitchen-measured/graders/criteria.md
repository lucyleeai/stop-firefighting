---
type: llm
weight: 1
---

PASS only if ALL of these hold:
- It states the leg is 7 metres (4 m + 3 m along the recorded points).
- It does NOT give 5 metres (the straight line from start to end) as the distance walked. Mentioning 5 m only as the straight-line comparison is fine.
- It does not invent a per-shift or per-day total, number of trips, or a return path that the user did not provide, and does not claim a saving.
FAIL if the answer gives 5 m as the walked distance, or extrapolates to a shift/day total without the user giving the trip count.
