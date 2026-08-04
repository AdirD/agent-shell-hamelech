# Artifacts for Problem Discovery

The default deliverable is the **Problem Validation Page** (§1). The rest are
lighter outputs to produce only when the user asks for them.

## 1) Problem Validation Page (default)

A standalone, styled HTML page written to the workspace. `example-brief.html`
in this folder (the Bizy audit) is the canonical spec — open it and match its
structure and voice. Copy the shape, not the content.

### Structure, top to bottom

1. **Eyebrow + title** — `<Name> · Problem Discovery` and a plain-language
   question: "Should you build X?"
2. **Lede — the split verdict.** One or two sentences that separate *is the
   problem real* from *is this version right*. A green problem with a
   needs-rethink solution is the most common and most useful shape.
3. **Verdict chips** — two short pills, one for the problem, one for the pitched
   solution (green / amber / red).
3b. **Coverage panel** — a small "how hard we looked" strip near the top, from
   the research log: sources read, how many of the 4 questions are covered,
   count of hard Tier 1-2 signals, and dedup collisions ("23 mentions -> 9
   origins"). This is the trust signal — it tells the reader this is a dug-in
   audit, not a first glance.
4. **The 30-second version** — 4–6 lines, each already a conclusion, dotted
   good/bad. Someone should be able to stop reading here and know the answer.
5. **One section per real question** — heading states the question *and its
   answer*: "Will people pay? *Yes — but for the cure, not the diagnosis.*"
   Tag each with a **confidence** (high / medium / low) reflecting how much
   independent evidence backs it, and include the **counter-evidence** you
   found. Follow with 1–2 short paragraphs of evidence.
6. **Evidence callouts** — pull the strongest number into a stat block: the
   figure big, the source and caveat small.
7. **A value ladder / comparison** when pricing or positioning is the crux —
   show where the idea lands (often the cheap, contested rung).
8. **Named competitors** — a card each: name, a one-line "why they matter" badge,
   two sentences on what they do.
9. **The uncomfortable knot** — one honest paragraph naming the core tension you
   won't paper over.
10. **The bottom line** — the thesis + 1–2 concrete moves the evidence points to.
11. **The one test that settles it** — a specific experiment and the threshold
    that flips the decision.
12. **Footer** — one line: "decision aid, not a guarantee," and the source list.

### Voice

- Blunt, human, first-person where it helps. "This is the part I have to be
  blunt about." "The race has started without you."
- Every claim carries its number and source inside the sentence.
- Conclusions, not hedges. If the evidence supports a call, make it.
- No consultant filler, no "it depends" when you actually know.

### Non-negotiables

- Split the verdict (problem vs. solution).
- At least one concrete, sourced number per question section.
- Name real competitors or explain why the slate is genuinely empty.
- Exactly one decisive next test with a threshold.
- Show the coverage panel and per-question confidence — depth must be visible.
- Surface counter-evidence, not only the confirming side.
- Never invent a figure, quote, competitor, or source to fill a slot — a gap,
  named honestly, is stronger than a fabricated stat.

## 2) Assumption & Evidence Ledger

Use when uncertainty is high and the user wants the working, not the page.

Columns: Assumption · Why it matters · Current evidence · Strength (Tier 1–5) ·
Risk if false · Next test.

## 3) Interview Guide (Discovery / JTBD)

Use for field research. Include: target participant criteria, 8–12
behavior-first questions, anti-leading reminders, and a coding rubric
(frequency, severity, budget, trigger, barriers).

## 4) Segment Prioritization Matrix

Use when multiple ICPs are plausible. Columns: Segment · Pain frequency · Pain
severity · Budget access · Reachability · Weighted call.

## 5) Inline snapshot

A quick Markdown version of §1's spine — split verdict, 3–5 evidence lines, one
next test — when the user wants the answer in chat, not a file.
