# Failure review for any actor

The same failure can come from a person, a team, a machine, a supplier, a
software system or an AI assistant. Do not start from *who* failed; start from
*what can be observed* about how the work went wrong. These types are not
exclusive — one problem often shows several. Use them together with
`reference/people/guide.md` when a person's action is involved.

| What can be observed | Look at | Changes that fit |
|---|---|---|
| **The request changed on the way** — what reached the doer is not what was asked | Compare the asker's original words with each handover (brief, ticket, message, order) and with the result. Find the first place the meaning shifted. | Fewer relays; pass the original words along; a check at the handover that the request still matches. |
| **Needed information did not arrive, or an old version did** | What the doer actually had at the time — not what was saved somewhere. Versions and dates. | Put the information where the work happens (on the form, in the tool, in the instructions loaded at the start); remove old versions. "It was written down" does not prove it was there. |
| **A step was skipped, or its result was misused** | Records of what was actually done (logs, timestamps, photos, tool calls), not a description of what should be done. | Make the step part of the flow (cannot proceed without it); make the result visible to the next step. |
| **Inputs were complete, and it still failed** | Repeat the same task with the same inputs; does it fail the same way? | Change the task (smaller steps, a worked example, a different tool or person or model), add a check at the risky step. Do not assume missing information. |
| **The check passed the wrong thing, or the work ended too early** | What the check actually tests versus what matters to the asker. | Check against the asker's words and the real result, not the presence of a document or a keyword. |
| **A limit was broken** — an action outside agreed rules or authority | The rule, whether it was known and usable at that moment, what made breaking it easier. | Fix what makes the rule hard to follow; block the action where it matters. Do not infer intent. |

## People

For a person's action, `reference/people/guide.md` adds the kinds of human
error (slips and lapses, rule-based and knowledge-based mistakes, deliberate
deviations) and the countermeasures that fit each.

## AI assistants and automation

- An AI assistant's own explanation of why it failed is a **reported** account,
  not a record of what happened inside it. Check against the actual trace:
  what it was given, what it called, what it produced.
- "It promised to do better" and "a rule was added" are not changes in place.
  A change is in place when the next run actually receives it and its output
  shows it — check that on the next real task.
- Another model reviewing the work is not automatically independent. The
  checker needs the original request, the actual trace and the output — not
  the previous analysis.
- Evidence of a change can be a configuration, a file, a hook — but also a
  changed handover, a smaller task, or a person checking at one step. Do not
  count only code changes as improvement.
