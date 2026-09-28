---
type: llm
weight: 1
---

The expert move: a two-humped (bimodal) distribution usually means two different processes are mixed — e.g. two filler heads/nozzles, two shifts/operators, two batches of sauce viscosity, before/after a change. Stratify the data by that factor before doing anything else; treating it as one process (one mean/sd, one capability number) is misleading.
PASS only if it (a) says the two humps likely indicate two distinct sources/sub-processes mixed together and (b) recommends splitting (stratifying) the data by candidate factors such as filler head, shift, line, batch or time before computing capability or changing the target.
FAIL if it treats the data as one process (e.g. just computes an overall mean/sd or tells them to lower the target) without the stratification step.
