# Orchestrating Market Validation

Parallelize independent evidence collection, not judgment. One orchestrator owns
the validation contract, evidence map, thresholds, and decision throughout.

## Ownership

```text
ORCHESTRATOR
  locks the contract and thresholds
  owns the living claim/evidence map
  chooses lanes and caps
  deduplicates and reconciles contradictions
  designs fieldwork and experiments
  synthesizes and decides
        |
        +---- read-only evidence lanes
        +---- authorized first-party analysis lanes
        +---- human-gated customer/experiment work
```

Subagents return evidence, not “the market is validated.” A final decision
requires cross-lane context and remains with the orchestrator.

## Secondary-research lanes

Use only independent questions that materially affect the decision:

| Lane | Question |
|---|---|
| Problem behavior | Does the segment repeatedly encounter the costly situation? |
| Existing demand | What money, labor, workarounds, or switching already occurs? |
| Buyer and budget | Who owns the outcome, budget, and approval path? |
| Alternatives | How is the job solved today and why do customers stay? |
| Reachability | Where can this segment be found and what channels show response? |
| Counter-case | What evidence, failed attempts, or structural forces break the hypothesis? |

Do not spawn a lane per website. Sources are where a question looks, not the
unit of work.

## Lane contract

Give every evidence lane:

- the locked validation contract
- one question
- which evidence types count
- geographic and time boundaries
- a source or time cap
- the instruction to search for and against the claim

Require rows shaped like:

```json
{
  "claim": "Short factual statement",
  "validation_claim": "problem | demand | buyer | offer | reachability",
  "tier": 2,
  "source_url": "https://...",
  "source_id": "canonical origin",
  "date": "YYYY-MM-DD",
  "snippet": "Verbatim quote or datapoint",
  "supports": true,
  "confidence": "high | medium | low",
  "limits": "What this evidence cannot establish"
}
```

Lane rules:

- no overall verdict or recommendation
- no unsourced rows
- mark inference, estimates, paywalls, and stale sources
- return an empty set rather than Tier-5 padding
- stop at the declared cap

## Merge sequence

1. combine rows
2. resolve links and provenance
3. deduplicate by canonical origin
4. assign each row to one or more validation claims
5. keep supporting and contradicting evidence visible
6. weight by directness, behavior, segment fit, recency, and independence
7. update claim evidence states
8. identify the highest-impact unresolved claim
9. decide whether more desk research can change it
10. when it cannot, move to primary discovery or a behavioral test

Several lanes citing one vendor study remain one origin. Several communities
repeating one press article remain one origin.

## First-party analysis

Parallel lanes may analyze authorized aggregates such as:

- product behavior
- support themes
- churn reasons
- sales objections
- interview transcripts
- experiment results

Give every lane the same claim taxonomy and require limitations. Keep personally
identifiable or sensitive customer data out of subagent prompts unless access is
necessary and authorized.

Do not let separate lanes independently reinterpret the target segment. If
evidence suggests a new segment, return it as a contradiction or reshape
candidate for the orchestrator.

## Human gates

Customer interviews, workflow observation, outreach, and commercial tests
usually require user participation or authorized external tools.

At a human gate:

1. update the living validation brief
2. provide a run-ready protocol and capture template
3. state what result resumes the workflow
4. pause rather than simulating evidence
5. on return, verify participant fit and provenance before synthesis

The workflow is still end-to-end even when reality introduces a wait. Closing
the loop means preserving state and resuming through the decision—not pretending
the gate does not exist.

## Stop conditions

Stop a lane or the full validation effort when:

- its cap is reached with no new signal
- new sources only repeat known origins
- decisive counter-evidence invalidates the claim
- the next uncertainty requires customer behavior, not more search
- collecting the next evidence would cost more than the decision warrants

Do not keep researching merely to fill a report.
