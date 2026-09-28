---
type: llm
weight: 1
---

The expert move: parts can be "better" (less variation, still in spec) yet shifted in their average, or the old variation was masking a process that was tuned to the old parts. Our weld recipe/fixture was set up around the OLD parts' actual dimensions, so a within-spec shift of the mean (or of the distribution) can move us out of the robust window.
PASS only if the answer (a) explicitly raises that the new parts' dimensional distribution (mean/centre, not just spread) may have shifted within tolerance and that our weld process/fixture was tuned to the old parts, and (b) proposes comparing before-vs-after dimensional data for the key features (e.g. old vs new lot measurements, histograms) and re-checking/re-centring the weld window on the new parts.
FAIL if it only suggests generic checks (welder calibration, settings drift, supplier audit, incoming inspection) without the within-tolerance-shift / process-tuned-to-old-parts insight.
