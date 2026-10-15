# Card: keep track of causes — and of what is actually known

**Use when** there are several possible causes, or a case runs over more than one conversation. **Skip** when the cause is plain and the fix is quick: fix it and check.

**Needs** the candidate causes and whatever evidence exists.
**Gives** the causes table in the case record (`../../../rules/case-record.md`), each cause with a place that can change and its status.

## The table
| Candidate cause | Place it could change | Evidence for | Evidence against | Check that would tell it apart | Status |
|---|---|---|---|---|---|
Status: **open** → **supported** (evidence goes with it) → **confirmed** (a trial or comparison ruled out other explanations) — or **ruled out**. Keep the *fix* status separately (planned / in place / checked / held): a confirmed cause does not mean the fix works, and a fix that works does not prove the cause.

## Finding candidates
- **Fishbone**: list possible causes under the work method, materials and information, tools and systems, environment, measurement, and people's knowledge — to make sure nothing obvious is missed. It produces candidates, not causes.
- **5 Whys**: on one specific occurrence, ask why until you reach something that can be changed. Stop there — do not force five levels, and branch when there are several answers.
- **Counts by category** (Pareto, `scripts/stats_tools.py pareto`) when occurrences are recorded.

## Rules
- A chart, a Pareto or a significant test reaches *associated*, not *confirmed* (`../../../rules/evidence-rules.md` rule 6).
- "Not careful enough", "communication" and "attitude" are not causes; ask what about the work made it easy to go wrong.
- When new evidence contradicts a supported cause, change the status — do not defend it.

Sources: ASQ, "What is a Fishbone Diagram?" — https://asq.org/quality-resources/fishbone ; ASQ, "Five Whys and Five Hows" — https://asq.org/quality-resources/five-whys ; ASQ, "What is a Pareto Chart?" — https://asq.org/quality-resources/pareto
