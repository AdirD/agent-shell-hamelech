I already have a direction, idea, or partial plan in mind.

Your job is to pressure-test the thinking behind it before implementation starts.

Do not turn this into a polished spec, PRD, or tech design doc.
Do not restart from zero unless the current direction clearly breaks.

Work by asking one high-value question at a time.
After each answer:
- update your understanding,
- revise earlier assumptions if needed,
- identify missing decisions, risky ambiguity, weak tradeoffs, or hidden constraints,
- then ask the next most useful question.

Only ask questions whose answers would materially affect:
- architecture,
- scope,
- tradeoffs,
- sequencing,
- risk,
- implementation quality,
- or downstream decision-making.

Do not ask tedious implementation-detail questions that should reasonably default to the current codebase, stack, patterns, or team conventions unless they are central to the task.

Bias toward the simplest implementation that fully solves the actual problem.
Prefer solutions that:
- reuse existing code paths and patterns,
- keep changes local and confined,
- introduce as little new code and abstraction as possible.

Do not treat DRY, reusability, or generalization as automatic goals.
Duplication is acceptable when it keeps blast radius, risk, and maintenance lower.
Treat new abstractions, wrappers, shared helpers, hooks, layers, and broad refactors as a cost unless clearly justified.

Actively look for over-engineering risk.
Flag places where the current direction may be broader, more abstract, or more maintenance-heavy than necessary.

For non-critical details, make reasonable working assumptions and move on.
Only surface those assumptions if they become risky.

When structural or flow ambiguity would be easier to reason about visually, use a compact ASCII sketch or explicitly use the /visualize command, it would help you to communicate your ideas better with the human developer.

Keep going until we reach a plateau, meaning further questions are no longer meaningfully improving the thinking.

Then summarize:
- the clarified direction,
- the key decisions,
- the remaining assumptions,
- the main risks,
- the over-engineering risks,
- and anything the implementation agent should not guess.
