# Method index

Each card can be used on its own — when the user asks for one method ("just do a Pareto", "help me write the requirement"), use that card directly without the full process. When working a whole problem, `SKILL.md` decides which cards the situation needs.

| Card | Use when | Gives | Runs a script? |
|---|---|---|---|
| `cards/requirement.md` | the problem is in someone's words; a target arrives; people disagree on "late" or "wrong" | a result measure, a sourced requirement, the edges | no |
| `cards/measurement-check.md` | a number or a check will decide something | whether the ruler can be trusted, what to fix first | rates via `stats_tools.py` |
| `cards/walk-and-subtract.md` | slow, many steps, many checks, nobody knows the process | the real path of one item; steps to remove, merge, reorder, simplify | waits via `flow_metrics.py` |
| `cards/cause-ledger.md` | several possible causes; the case spans conversations | causes with a place to change, evidence, status | Pareto via `stats_tools.py` |
| `cards/trial-and-risk.md` | a change is proposed | trial plan, what it could break, stop rule, way back | sizes via `stats_tools.py` |
| `cards/control-plan.md` | a change goes live, or a problem came back | control table with reactions, handover list | charts via `stats_tools.py` |
| `cards/benefit-baseline.md` | someone will ask "was it worth it?" | before/after record, cash vs time vs burden | comparisons via `stats_tools.py` |
| `selector.md` | choosing a statistical method or chart | the method, run with the scripts | yes |
| `../flow/guide.md` | timestamps, routes, handoffs | waiting vs work, spaghetti, handoff counts | `flow_metrics.py` |
| `../people/guide.md` | a person's action is part of a failure | kind of error and the countermeasure that fits | no |
| `../failure-types.md` | any failure, any actor | observable failure type and fitting changes | no |

Not bundled (name it, say what it needs, do not compute by hand): full designed experiments, formal gauge studies, multi-variable regression. Capability and simple regression are in `stats_tools.py` (`capability`, `regress`). Never used as a basis for decisions: automatic personal blame, charts as proof of cause, generic error probabilities or unverified minimum sample sizes.
