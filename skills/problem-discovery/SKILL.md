---
name: problem-discovery
description: >-
  Validate whether a real customer segment has a painful, frequent, and costly
  problem with credible willingness to adopt or pay before committing to solution
  design. Use for customer discovery, pain-point research, problem validation,
  demand validation, and Jobs To Be Done discovery.
---

# Problem Discovery

Find out whether a problem is real, painful, and worth solving now — then say so
like a smart, blunt friend, not a consultant filling in a template.

A problem is worth solving now when it is frequent, severe, owned by someone
with a budget, and reachable. Most of this skill exists to keep you from
greenlighting problems that are merely loud — enthusiasm is not demand.

The shape of the work is always the same three moves:

```text
1. LOCK ONE HYPOTHESIS   →   2. GO RESEARCH IT   →   3. DELIVER ONE ARTIFACT
   "A doing B struggle           default action:         the styled HTML page —
    when they hit C"             hit real sources        verdict, numbers, rivals,
                                 for and against it      one decisive next test
```

Do not run an intake. Do not wait to be told "go research." Lock the sentence,
go find out, come back with the argument.

## 1) Lock one hypothesis

Everything hangs on a single falsifiable sentence:

> **Users of type A, doing B, struggle when they reach C.**

You **propose** it from whatever the user gave you — do not interrogate them into
it. Fill the blanks with your best read, show the sentence, and let them correct
it. One round. If they hand you a product idea instead of a problem, translate it
into the pain sentence and confirm.

- **A** — the specific person/segment (not "businesses"; "solo founders shipping
  AI-built sites").
- **B** — what they're doing when the pain shows up.
- **C** — the wall they hit.

Ask a question only when a blank is genuinely unguessable and would change where
you research. A wrong guess the user fixes is cheaper than a question that stalls
them. When the sentence is agreed, stop clarifying and start researching.

## 2) Go research it

This is the default action, not something you wait to be asked for. Once the
sentence is locked, go to **real sources** and gather evidence *for and against*
it. Read `references/research.md` for the signal ladder; in practice that means:

- **Is the pain real?** — Reddit, Hacker News, forums, GitHub issues, support
  threads, tool-specific communities. Look for the *same failure described over
  and over*, not one loud post.
- **Will they pay?** — pricing pages, G2/Capterra, job postings, "rescue"/agency
  retainers, what people already spend on alternatives.
- **Who else does this?** — name the direct competitors and near-substitutes,
  and what they charge. An empty competitor slate usually means you looked too
  narrowly, not that the space is open.

Ground rules that keep the research honest:

- Prefer observed behavior (spend, switching, workarounds) over opinions.
- Concrete numbers with a named source beat adjectives. Get the figure, not "many."
- **Deduplicate by origin before you count.** Five people citing one Reddit
  thread is one signal, not five.
- Don't claim "validated demand" from upvotes and enthusiasm alone.
- If the evidence is thin, say so — "insufficient evidence" is a real finding.

When the audit is big enough to fan out to subagents, read
`references/orchestration.md`: one lane per independent question, lanes fetch
evidence only, you keep every judgment call.

## 3) Deliver one artifact

The default deliverable is a **standalone styled HTML page** written to the
workspace — the same shape as `references/example-brief.html` (the Bizy example).
That file is the spec; read it before writing yours. Match its structure and its
voice, not its content.

The artifact must:

- **Open with a split verdict.** The problem and *this specific solution* are two
  different questions — a problem can be green while the pitched version needs a
  rethink. Say both in the first two sentences.
- **Give the 30-second version** up top: 4–6 punchy lines, each already a
  conclusion, color-coded good/bad.
- **Make each big question a heading with its answer built in** — "Is the pain
  real? *Yes — strongly.*" Then the evidence for that answer.
- **Weave numbers inline, sourced.** `64% of AI checkouts fail (Stripe's
  benchmark)` — the figure and where it came from, in the sentence.
- **Name the competitors** with a one-line "why they matter."
- **Land a thesis**, not a shrug — the one insight that reframes the decision
  (e.g. "the money follows the fix, not the report").
- **End with one decisive next test** and the threshold that flips the call —
  a concrete thing to run, not "talk to users."

Write it in a **blunt, human voice**. Be willing to say "this is the part I have
to be blunt about." Precision changes decisions; a neutral tone hides the point.

For the section-by-section spec and voice guide, read `references/artifacts.md`.
Simpler outputs (a ledger, an interview guide, an inline Markdown snapshot) are
fine when the user asks — the HTML page is the default, not the only option.

## Guardrails

- Never run a multi-question intake. Propose the sentence; let them fix it.
- Never stop at "I need more info" when public sources could answer it — go look.
- Never equate complaints, upvotes, or enthusiasm with budgeted demand.
- Never count one source multiple times as corroboration.
- Never invent traction, quotes, prevalence, competitors, or willingness to pay.
- Never hand back a flat, hedged report when the evidence supports a clear call.
- Never force venture-scale criteria onto a lifestyle business or internal tool.
