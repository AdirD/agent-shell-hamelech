# WHERE — system attention and expertise

Phase order, parent-led PR exploration, autonomous repository mapping, and
update timing live in `workflow.md`. This file defines how attention evidence is
ranked, represented, used, and maintained.

Developers usually have parts of a system they know deeply or repeatedly care
about. Clone should identify those areas so it can allocate more review depth
there. Maintain one relative map inside each repository's `MEMORY.md`.

The map answers:

- Which parts of this repository does the human inspect most carefully?
- Which systems or boundaries trigger deeper reasoning?
- Which areas receive lighter review by explicit preference?
- Which areas remain unknown because evidence is missing?

This is demonstrated reviewer interest or expertise, not code quality or
objective risk.

The autonomous repository writer creates a factual system/architecture graph in
the run's `repository-system.md`. That graph shows how the repository is built.
It does not rank reviewer attention. The main agent derives the attention tree
below from review behavior, corrections, and human answers.

## Build the tree

Start from the repository's actual architecture and stack: applications,
packages, services, runtime boundaries, persistence, queues, infrastructure,
external integrations, frontend surfaces, generated files, tests, and docs.
Group paths when the human appears to reason about them as one system.

Render a compact ASCII tree:

```text
Attention map — relative within this repository

repository
├── API and trust boundaries ............ high — repeated deep review
│   ├── authentication / authorization .. high — explicit human correction
│   └── external URLs and egress ........ high — repeated across PRs
├── asynchronous jobs and retries ....... medium — some substantive evidence
├── persistence and migrations .......... medium — early repeated evidence
├── frontend interaction state .......... unknown
└── generated formatting churn .......... explicitly low — human-confirmed
```

Use actual generic repository paths beneath an area when they help Clone route
attention. Keep the tree readable; do not mirror every directory.

## Rank honestly

Use only:

- `high`: repeated or explicit evidence that the human spends deeper attention
  here
- `medium`: affirmative evidence exists, but the area does not dominate the
  reviewer's attention
- `unknown`: insufficient evidence; never convert silence into a low rank
- `explicitly low`: the human directly indicates a lighter threshold or
  repeatedly removes Clone feedback there

Add a short evidence phrase where useful. Do not invent numeric precision or a
separate confidence taxonomy.

Strong WHERE signals include:

- repeated substantive comments in the area
- change requests, follow-up discussion, or re-review concentrated there
- detailed reasoning about blast radius, architecture, or failure modes
- repeated references to existing implementations or infrastructure
- substantial authorship or maintenance combined with review behavior
- other developers repeatedly seeking or relying on the human's judgment there
- the human adding a concern there after Clone missed it
- explicit human guidance

Authorship, review requests, `CODEOWNERS`, and maintenance history alone show
possible familiarity, not personal review priority. Use them to find evidence,
then confirm through behavior or the human. Silent approvals or absence of
comments must never lower an area by themselves.

Assign low priority only from affirmative evidence: the human explicitly says
they usually let it pass, repeatedly removes Clone comments there, or states a
higher intervention threshold.

## Use the map

The generated Clone should:

- inspect high-attention areas more deeply
- spend more context on boundaries connecting high-attention systems
- lower its threshold for investigating changes in demonstrated expertise areas
- use the map to choose among otherwise comparable findings
- remain cautious in unknown areas rather than treating them as unimportant
- still report clear correctness or security defects anywhere

A high rank does not manufacture a comment. An explicitly low rank does not
suppress a real defect. The map allocates attention and comment budget; the
current diff still determines whether anything is worth saying.

## Maintain it

Change the tree only when new evidence materially changes relative attention.
Record meaningful movements in `RUN.md`:

```text
Attention changes
- Persistence and migrations: unknown → medium
  Repeated human comments on rollback safety and backfill ordering.
- Generated formatting churn: unknown → explicitly low
  Human repeatedly removed Clone comments there.
```

When a rank change would materially alter review depth, search for targeted
corroboration and contrast first. Ask the human if the uncertainty still
matters; otherwise preserve it as unknown. Keep the prior rank in the run record
rather than silently rewriting the past.
