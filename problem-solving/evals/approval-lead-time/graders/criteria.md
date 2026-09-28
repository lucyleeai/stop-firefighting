---
type: llm
weight: 1
---

PASS only if ALL of these hold:
- It explains that 09:00 to 10:00 (60 minutes) is total elapsed/lead time, not proof the approver spent 60 minutes working on it; it asks for when work actually started or more cases to separate waiting from working.
- It does NOT conclude the approver is slow or recommend training her to be faster as the answer.
- It does NOT recommend dropping the second-review step; it asks what that review protects against or notes that payment-detail changes are a fraud/risk control that must be kept or replaced with something verified.
- It still gives a useful next step (e.g. pull timestamps for more requests, look at queue time).
FAIL if it recommends removing the review, or blames/targets the approver's speed based on this single example.
