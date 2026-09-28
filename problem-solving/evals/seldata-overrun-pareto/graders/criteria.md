---
type: llm
weight: 1
---

Ground truth: freight 17 of 40 (42.5%), price increase 11 (cumulative 70%), rush order 6 (cumulative 85%); three categories reach 85%.
PASS if the reply ranks the causes consistently with these counts, recommends starting with freight (the largest), and proposes any reasonable next step for digging in — e.g. breaking freight overruns down further (lanes, carriers, expedites), weighting by cost/amount rather than count, or checking that the logged causes are consistent.
FAIL if the ranking or counts are wrong, or the recommended priority does not follow the data.
