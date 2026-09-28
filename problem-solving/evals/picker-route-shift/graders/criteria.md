---
type: llm
weight: 1
---

Ground truth (computed by script): T1 = 41.6 m per trip, T2 = 50.8 m, T3 = 30.4 m (along the recorded points). Per shift: T1 22 × 41.6 = 915.2 m, T2 9 × 50.8 = 457.4 m, T3 31 × 30.4 = 942.4 m; total about 2,315 m (2.3 km).

PASS only if ALL of these hold:
- Per-trip distances and the per-shift total match the ground truth within rounding (total 2,314–2,316 m or 2.3 km).
- It identifies T3 (shortest per trip but most frequent) as the largest share of daily walking, with T1 close behind, rather than choosing T2 just because it is the longest single trip.
- It does not claim a saving as achieved (proposals only).
FAIL otherwise.
