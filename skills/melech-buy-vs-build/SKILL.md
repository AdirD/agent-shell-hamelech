---
name: melech-buy-vs-build
description: Decide whether to adopt an existing tool or build a capability yourself, grounded in verified research.
disable-model-invocation: true
---

# Buy vs Build

An agent asked to "add background jobs" will happily write a `tasks` table, a
polling worker, a retry column, and a dead-letter flag. It works. It is also
BullMQ, or Trigger.dev, or Cloud Tasks, or the queue library already sitting in
`package.json` — rebuilt badly, and now owned forever.

Nobody makes the call deliberately. Repo-level review only ever asks *"does
this already exist in our code?"*, and model memory answers external questions
with confident, stale, sometimes invented package names. The expensive,
hard-to-reverse decision — own the implementation, or hand the capability to a
third party — gets made by default instead of on evidence.

`melech-buy-vs-build` owns that decision. It looks **outward** — finding what the
rest of the world already shipped for the capability, verified against live
sources — and it runs one **inward** check first: *adopt-vs-rebuild*, is this
already covered by a dependency or vendor you already have? Then it brings back
a shortlist and a verdict: adopt, or keep building.

Think *"is there an AI for that?"* — but for the build-vs-buy call, and
grounded in evidence instead of vibes.

---

## Two Intents

Both intents are **outward** research feeding one build-vs-buy verdict. Whichever
fires, run the inward **adopt-vs-rebuild** check first (step 2) — a capability you
already own beats anything you would go find or build.

| Intent | Trigger | Goal |
|---|---|---|
| **Intercept** | Code, a plan, or a diff exists and may be reinventing something. | Name what was (re)built, find the incumbents, decide adopt vs. keep building. |
| **Explore** | Open-ended: "what's out there for X", "any new tools for X", "how do people do X now". | Map the space, surface the notable and the recent, arm the user to choose. |

Do not ask which intent applies when it is obvious from the input. A diff or a
proposal means intercept. A bare capability question means explore.

---

## The One Rule That Decides Everything

**Search the capability, not the noun.**

The single reason this research fails is searching the user's own vocabulary.
An agent that greps the web for `"postgres polling table worker"` finds
blog posts. An agent that recognizes the capability as **durable background job
execution** finds the entire category.

So before any search: translate the implementation into the canonical term the
industry uses for it.

| What the agent built | What to actually search |
|---|---|
| Rows in a table + a polling worker + retry count | job queue, background jobs, durable task execution |
| Custom event bus with handler registry | pub/sub, message broker, event bus |
| Hand-rolled retry-with-jitter wrapper | retry library, resilience/backoff library |
| Bespoke role/permission matcher | authorization / policy engine, RBAC / ReBAC |
| Cron-ish `setInterval` + lockfile | job scheduler, distributed cron, workflow orchestration |
| Diff-and-apply state machine for a wizard | state machine library, workflow engine |
| Custom CSV/Excel export writer | spreadsheet / serialization library |

If unsure of the canonical term, the **first** search is for the term itself:
*"what is it called when …"*. Get the vocabulary right, then fan out.

---

## Workflow

```text
1. Name the capability  ─►  2. Read the ground truth  ─►  3. Fan out lanes  ─────────►  4. Reduce  ─►  5. Shortlist + verdict  ─►  6. Hand off
   (canonical vocabulary)     (stack, constraints)          adopt-vs-rebuild (inward) ┐   (dedupe, kill dead)   (ask_question)
                                                            outward lanes (web)       ┴─ same concurrent batch;
                                                                                          inward hit short-circuits
```

### 1. Name the capability

State in one line what the thing *does*, stripped of the local implementation.
List 2–5 canonical search terms and any obvious synonyms. Show this to the user
before fanning out — a wrong capability name wastes the whole run.

### 2. Read the ground truth (inline, must be first)

This quick read stays on the main thread because the outward lanes cannot be
briefed without it. Gather the constraints that will decide fit:

- **Language and runtime**, and what is already in the manifests
  (`package.json`, `requirements.txt`/`pyproject.toml`, `go.mod`, `Cargo.toml`,
  `Gemfile`, `pom.xml`)
- **Infrastructure already paid for**: cloud provider, Postgres/Redis/Kafka,
  vendors already in the bill
- **Hard constraints**: self-host only, data residency, licensing policy,
  air-gapped, no new vendors, budget
- **Scale reality**: 100 jobs/day and 100k jobs/second do not shortlist the same
  tools

If this cheap read already surfaces a blatant hit — the capability is *literally*
a direct dependency or an obviously enabled vendor feature — stop here and report
it. Do not fan out to buy something you already own. Otherwise, carry the
constraints into step 3 and let the deep adopt-vs-rebuild check run concurrently.

### 3. Fan out parallel lanes

Dispatch independent research lanes concurrently — one subagent per lane, each
running **multiple web searches** along its own path (except adopt-vs-rebuild,
which is mostly local). Lanes hunt different *kinds* of answers, not different
keywords. The inward lane and the outward lanes launch in the **same concurrent
batch**, so you do not pay the inward check as serial latency.

| Lane | What it hunts |
|---|---|
| **Adopt-vs-rebuild** *(inward, privileged)* | The deep version of the step-2 check: transitive deps, framework/stdlib built-ins, a vendor plan that already covers this, an internal monorepo library. Mostly local work plus targeted doc lookups. **Short-circuit authority** — see below. |
| **Canon** | The category's standard name and the 3–8 options every comparison lists. Awesome-lists, category pages, "X vs Y" roundups. |
| **Ecosystem** | Libraries and OSS in *this project's* language. Package registries, GitHub, framework-native answers. |
| **Commercial** | Managed services, dev tools, SaaS, cloud primitives. Includes the boring cloud answer nobody mentions. |
| **Verdicts** | What practitioners actually say: HN/Reddit threads, "we migrated off X", postmortems, why people regret each option. |
| **Counter-case** | Why rolling your own is sometimes right here, and the known failure modes of the incumbents. Keeps the shortlist honest. |

For **explore** intent, add a **Frontier** lane for what shipped in the last
6–12 months, since that is exactly where model memory is stale.

**Short-circuit rule:** if the adopt-vs-rebuild lane returns a confirmed hit —
a real, live capability you already own that covers the need — the run ends. The
outward lanes' results are discarded (that wasted compute is the price of running
inward and outward in parallel instead of gating). Report the owned option and
stop; do not shop for a replacement for something already paid for.

Scale the lane count to the stakes: 3 lanes for "is there a retry library",
all 6 for "should we build our own orchestrator". Do not spawn a lane per
website — a source is where a lane looks, not the unit of work.

If the user supplied seed names, sources, or "check X too", route those into a
dedicated lane rather than diluting the others.

Lane briefs, query patterns, hunting grounds, and the candidate row schema live
in `references/lanes.md`. Give every lane the capability statement, the
constraints from step 2, its one question, a source cap, and the evidence
contract.

### 4. Reduce

Merge all lanes, then: verify-or-drop → kill dead → dedupe identities → cluster
by *approach* (not name) → rank by fit to the step-2 constraints (popularity is
only a tiebreaker, never the criterion). The full merge rules — dead-cutoffs,
identity and origin collapsing, hard-constraint disqualification — live in
`references/lanes.md`.

### 5. Deliver the shortlist and the verdict

Cap at **3–6 candidates**. A list of twenty is a research dump, not a
recommendation.

```markdown
### ⚖️ Buy vs Build: durable background jobs (Node/TypeScript, Postgres, no new vendors)

| Option | Kind | Why it fits | Cost | What you give up | Adoption effort |
|---|---|---|---|---|---|
| `pg-boss` | OSS lib | Runs on the Postgres you already have; no new infra. | Free | Throughput ceiling vs. Redis-backed. | ~half a day |
| BullMQ | OSS lib | Mature, huge ecosystem, good observability. | Free + Redis | Requires Redis you don't run today. | ~2 days incl. infra |
| Trigger.dev | SaaS/OSS | Durable workflows + retries + UI out of the box. | Paid tier / self-host | New vendor; violates the stated constraint. | ~1 day hosted |

**Already in your stack**: none — `bull` is not installed; Redis is not provisioned.

**What no option gives you**: the per-tenant fairness rule in `worker.ts:88`.
Any adoption keeps that logic as your own scheduling layer.

**When rolling your own still wins here**: fewer than ~1k jobs/day, no fan-out,
no cross-process coordination — then your table plus a cron is genuinely less
total complexity than a queue runtime.
```

Then put the decision to the user with `ask_question`:

1. `Adopt <recommended option> and remove the hand-rolled version`
2. `Adopt, but keep the custom layer for <the part nothing covers>`
3. `Keep the custom implementation (record why)`
4. `Research further — different constraints or more options`

**Never rip out working code on your own initiative.** This skill reports and
recommends the buy-vs-build call. The user rules.

### 6. Hand off

- **Adopt** → integrate it via the smallest path, or realign the design if the
  swap reshapes it.
- **Keep building** → proceed, and leave one WHY comment recording what was
  evaluated and rejected, so the next agent does not re-run this debate.
- **The need itself now looks shaky** → revisit whether the need is real.
- **A shortlisted option needs stress-testing before commitment** → proof the
  pick before writing code.

---

## Evidence Contract

Models hallucinate confident, plausible, nonexistent packages. This skill is
worthless if it invents `@vercel/queue-kit`.

**Always web search. Memory generates hypotheses; only search produces
candidates.**

- Every candidate carries a URL that appeared in live results this run.
- Every candidate carries a liveness signal: last release, last commit,
  or a current pricing/docs page.
- Recalled-but-unverified names are labeled as such and must be confirmed
  before they reach the shortlist.
- Version numbers, pricing, limits, and license terms are quoted from the
  source or omitted. Never estimated.
- Report an empty lane honestly. "Nothing credible found in this ecosystem" is
  a real and useful finding.

---

## Do / Don't

**Do:** "This is a job queue. Canonical terms: background jobs, durable task
execution, work queue. Searching those before anything else."

**Don't:** Search the user's phrasing (`"tasks table with status column"`) and
conclude nothing exists.

**Do:** Check the manifests first — "`p-retry` is already a transitive dep;
your custom backoff wrapper is 40 lines of it."

**Don't:** Recommend a new vendor when the capability is already installed or
already billed.

**Do:** "Three of these are dead: last release 2021, repo archived, company
acquired and sunset. Dropping them."

**Don't:** Pad the shortlist with abandoned projects to look thorough.

**Do:** "None of these handle your per-tenant fairness rule. That part stays
yours either way."

**Don't:** Imply a library is a drop-in replacement without saying what it
misses.

**Do:** "At your volume, the hand-rolled version is genuinely simpler. Keep it."

**Don't:** Conclude "use a library" every time. A skill that always says adopt
is not research, it is a reflex.

**Do:** Present the shortlist and let the user choose.

**Don't:** Start swapping out working code because a more popular option exists.
