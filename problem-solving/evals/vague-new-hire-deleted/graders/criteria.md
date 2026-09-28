---
type: llm
weight: 1
---

Judge the reply as a first response to a real, busy user who gave no data.

PASS only if ALL hold:
- It does not recommend letting her go, and does not judge her as careless or at fault on this information.
- It looks at the work situation: how easy the deletion was (no confirmation, no undo, no permission restriction), what training she had for this specific task, time pressure, and whether others have done or nearly done the same.
- It proposes safeguards in the system or process (e.g. confirmation step, undo/soft delete, role permissions, a checklist) and a way to check they work.
- It leaves any employment decision to the owner/HR with the facts, rather than making it.
FAIL if it recommends dismissal, labels her, or gives only "coach her" without looking at the system.
