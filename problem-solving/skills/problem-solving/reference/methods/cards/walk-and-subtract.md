# Card: walk the real work, then subtract

**Use when** work is slow, has many steps or checks, or "nobody knows the process". **Skip** when the question is about one number.

**Needs** one recent real item (an order, a request, a ticket, a task) and someone who handled it, or its records.
**Gives** the path that item really took, where it waited, and a short list of steps to remove, merge, reorder or simplify — each with what it guards.

## Walk one real case
Follow the last real item from start to finish, from records or with the people who did it:
what was asked → what was passed on, to whom, how (form, message, file, system) → what the next person actually had → what they did → where it waited → how it was checked → what came out.
- Use the real case, not "how it usually works". Where you cannot see a step, mark it unknown.
- Timestamps, if any: compute waits with `scripts/flow_metrics.py` (`../../flow/guide.md`); with `--work-states` it also reports what share of the lead time is actual work.
- Physical routes: `flow_metrics.py path` gives distances and how often paths cross.
- **Chains of suppliers or teams:** walk each tier separately — what each one receives, decides and records — and mark where the evidence for a tier is only another tier's account of it.

## Four questions for every step
1. **Is it needed?** What would go wrong without it? Who uses its output?
2. **Can it be combined** with another step or done by the same person?
3. **Can the order change** so something waits less or is done once?
4. **Can it be simpler** — the system supplying the data, fewer fields, no retyping?

## Before removing anything
Every check, approval or field was added for a reason. Name what it guards and how often it catches something; remove or merge it only with a replacement that is verified in a trial (`../../../rules/evidence-rules.md` rule 5). Often the win is the *wait in front* of a check, not the check.

Sources: ILO, *Introduction to Work Study*, 4th rev. ed., ed. G. Kanawaty (Geneva, 1992) — questioning purpose, place, sequence, person and means to eliminate, combine, rearrange or simplify — https://webapps.ilo.org/public/libdoc/ilo/1992/92B09_329_engl.pdf ; LEI Lean Lexicon, "Gemba" — https://www.lean.org/lexicon-terms/gemba/
