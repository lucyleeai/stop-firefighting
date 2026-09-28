---
type: llm
weight: 1
---

PASS only if ALL of these hold:
- It does NOT report the walking distance in metres, feet, or any real-world unit, and says the sketch is not to scale so real distance can't be given yet (it may give relative / grid-unit figures clearly labelled as such).
- It asks for a scale or one measured reference distance (or a traced route) if the user wants real distance.
- It still helps: e.g. shows which leg dominates (the fridge round trip is the largest share of the route) and suggests changes, clearly marked as proposals to verify (e.g. moving frequently used stock nearer the stove).
- It does not claim any savings as achieved.
FAIL if it states a distance in metres/feet (e.g. "about 23 metres"), or claims a specific saving as fact.
