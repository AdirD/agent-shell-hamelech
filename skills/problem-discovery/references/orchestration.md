# Orchestrating the Audit (AI executor)

How to fan the research (SKILL.md step 2) out to subagents when the audit is big
enough to be worth it: what the orchestrator keeps, how to split the work, and
how to merge without inventing corroboration. For a quick check, just research
it yourself — this layer is for when parallel lanes genuinely save time.

Everything serves the **one locked hypothesis** ("A doing B struggle at C").
Lanes gather evidence for and against that sentence; they never redefine it.

The two failure modes this layer exists to prevent:

- **Fake triangulation** — several lanes cite the same origin (one Reddit
  thread, one vendor blog) and the merge counts it as multiple independent
  signals. Dedupe by canonical source *before* the triangulation rule runs.
- **Lane sprawl** — spawning a subagent per website instead of per independent
  question. Lanes are questions; sources are just where a lane looks.

## Who owns what

```text
ORCHESTRATOR (main agent, never delegated)
  • owns the locked hypothesis and which sub-questions are riskiest
  • decides which lanes to spawn and their stop conditions
  • holds the living evidence map
  • dedupes sources, applies the triangulation rule, scores, decides verdict
  • handles contradictions and writes the report
        │
        ▼  fan out (parallel, read-only)
  LANE SUBAGENTS (one per independent question)
  • search + read only; collect evidence rows
  • return provenance-tagged rows; no verdicts, no synthesis
```

A lane returns *evidence*; the orchestrator decides *demand*. A lane that
reports "there is strong demand" broke its job.

## Choosing lanes

Spawn a lane only when its question is independent of the others. Default lanes
map to the signal tiers in `research.md`:

| Lane | Tier | Looks at | Returns |
|---|---|---|---|
| Buying behavior | 1 | G2/Capterra, pricing pages, procurement/RFP, job posts | spend, switching, budget-owner signals |
| Workarounds | 2 | forums, GitHub issues, internal-tooling writeups | repeated manual work, tool-stitching |
| Intent proxies | 4 | Trends, keyword tools, review-complaint clusters | direction/volume of problem-intent |
| Alternatives | 1–2 | competitors, substitutes, current spend | what people pay for / do instead |

Rules:

- Tier 3 (interviews) is **human-gated** — it becomes a *next test* in the
  report, never an autonomous lane.
- Merge or drop a lane whose question overlaps another; do not pad the batch.
- If only one question is genuinely open, do not fan out — run it yourself.

## Lane contract

Every lane subagent gets the same fixed shape so the merge is mechanical.

Input to a lane:

- the single question it must answer
- the active hypotheses (segment, problem, context) for framing
- which tiers count as evidence for this lane
- the hard requirement: every row carries a resolvable source + date

Output from a lane — **evidence rows only**, one object per claim:

```json
{
  "claim": "short factual statement",
  "tier": 1,
  "source_url": "https://…",
  "source_id": "canonical: domain + author/thread + date",
  "date": "YYYY-MM or YYYY-MM-DD",
  "snippet": "verbatim quote or datapoint",
  "confidence": "high | medium | low",
  "contradicts": "row id or claim it conflicts with, if any",
  "estimated": false
}
```

Lane rules:

- No verdict, no recommendation, no cross-lane comparison.
- Prefer "insufficient evidence" over padding with Tier 5 noise.
- Flag paywalled, inferred, or estimated datapoints (`estimated: true`).
- Cap the lane (e.g. time or max sources) and return what it has at the cap.

## Subagent prompt template

```text
Role: read-only evidence collector for a problem-discovery audit. You do NOT
decide whether demand exists — you return sourced evidence rows only.

Question (your only job): <the one lane question>

Active hypotheses (context, do not try to confirm): <segment / problem / context>

Count as evidence: Tier <n> signals — <what qualifies for this lane>.

Return: a JSON array of evidence rows with fields
{claim, tier, source_url, source_id, date, snippet, confidence, contradicts, estimated}.

Hard rules:
- Every row needs a resolvable source_url and a date. No date → mark low confidence.
- source_id must be canonical (domain + author/thread + date) so duplicates collapse.
- Quote verbatim in snippet; do not paraphrase into stronger language.
- No verdicts, no synthesis, no comparison to other sources.
- If you cannot find credible evidence, return [] and say why in one line.
- Stop at <cap> and return what you have.
```

## Merge and decide (orchestrator)

Run these in order — the sequence is what prevents fake triangulation:

1. **Collect** all lane rows into one table.
2. **Dedupe by `source_id`.** Rows sharing an origin collapse to one; keep the
   strongest-tier instance and note the collision. This happens *before* any
   counting.
3. **Apply the triangulation rule** (`research.md` §B) against the deduped set:
   at least one Tier 1/2 behavioral signal **and** one Tier 3/strong-Tier 4
   narrative signal **and** no unresolved decision-reversing contradiction.
4. **Handle contradictions** (`research.md` §E): keep both sides visible, weight
   by strength and recency, name the minimal test to resolve.
5. **Score** each surviving segment/problem hypothesis (`research.md` §D).
5b. **Check the depth bar** (SKILL.md §2): >= 3 of 4 questions each backed by
   >= 2 independent origins, >= 1 hard Tier 1-2 signal, competitors named, and
   disconfirming evidence actually sought. If it is not met and the cap is not
   hit, **spawn more lanes / deeper queries — do not proceed to a verdict yet.**
6. **Decide** Proceed / Refine / Hold / Stop — or "insufficient evidence" plus
   the single fastest next test that would change the decision.

If dedupe leaves the triangulation rule unmet, the honest output is
**insufficient evidence**, not a softened yes.

## Report pipeline

When the user asked for a report, assemble it from lane outputs — do not
re-research during writing.

```text
lock the hypothesis
   → pick the riskiest sub-questions
   → spawn lanes (parallel)     ── gate: each lane returned rows or "[] + reason"
   → dedupe by source_id        ── gate: no source counted twice
   → triangulation rule         ── gate: behavioral + narrative + no fatal conflict
   → score + contradictions
   → verdict + next test
   → emit coverage panel (queries, origins, tiers, collisions, per-answer confidence)
   → write the Problem Validation Page   (references/artifacts.md §1)
```

The page maps straight onto this run: its evidence is the deduped set, its
split verdict is the merge outcome, its one test is the fastest next step from
step 6 (often the human-gated Tier 3 interviews). Numbers carry their source
inline — claims with no source are a draft, not a result.
