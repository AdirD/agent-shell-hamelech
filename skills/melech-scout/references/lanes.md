# Scout Lanes

How to brief parallel research lanes, where each one hunts, and what it must
return. One orchestrator owns the capability statement, the constraints, the
merge, and the recommendation. Lanes return **candidates with sources**, never
verdicts.

```text
ORCHESTRATOR
  names the capability and canonical terms
  gathers stack + constraints
  chooses lanes and caps
  merges, dedupes, kills dead entries
  ranks against constraints and recommends
        |
        +---- Canon
        +---- Ecosystem
        +---- Commercial
        +---- Already yours
        +---- Verdicts
        +---- Counter-case
        +---- Frontier        (explore intent)
        +---- User-seeded     (only if the user named sources or tools)
```

---

## Lane brief template

Give every lane the same header, then its own question and cap:

```text
CAPABILITY: <one line, implementation-free>
CANONICAL TERMS: <2-5 industry terms>
STACK: <language, runtime, framework, datastore, cloud>
INSTALLED: <relevant existing dependencies>
CONSTRAINTS: <self-host / licensing / budget / vendor policy / data residency>
SCALE: <realistic volume, concurrency, latency need>

YOUR QUESTION: <the one thing this lane answers>
CAP: <N sources or N searches>

RULES:
- Run multiple distinct searches. Do not stop at the first result page.
- Every candidate needs a URL you actually saw in results this run.
- Every candidate needs a liveness signal (last release / last commit / live pricing page).
- Never emit a package or product name from memory without confirming it exists.
- Return an empty set rather than padding with weak or dead entries.
- No overall recommendation. Candidates and evidence only.
- Stop at the cap.
```

---

## The lanes

### Canon

**Question:** What is this category called, and which options does every
comparison of it name?

Establishes the vocabulary and the obvious field. If this lane comes back
sparse, the capability statement is probably wrong — tell the orchestrator
rather than pushing on.

Searches to run: `<capability> library`, `best <capability> tools <year>`,
`<capability> comparison`, `awesome <capability>`, `<option A> vs <option B>`.

### Ecosystem

**Question:** What exists for this in *this project's* language and framework?

The right answer is frequently framework-native and unexciting — a built-in
module, a first-party package, or a maintained community standard. Check that
before third-party options.

Searches to run: `<capability> <language>`, `<capability> <framework>`,
`<framework> built-in <capability>`, registry search, `site:github.com
<capability> <language>`.

### Commercial

**Question:** Who sells this as a managed service, dev tool, or cloud primitive?

Include the boring cloud answer (the managed queue, the hosted scheduler, the
platform's built-in auth) — it is routinely the cheapest correct option and
routinely omitted from OSS-focused roundups.

Capture pricing *model* (free tier, usage-based, seat-based, enterprise-only)
and self-host availability. Quote from the pricing page or omit.

### Already yours

**Question:** Is this capability already installed, already bundled, or already
paid for?

Highest-value lane. It is mostly local work plus targeted doc lookups:

1. Read the manifests and lockfiles for direct **and transitive** deps that
   cover the capability.
2. Check the framework's and stdlib's own docs — the feature may ship in the
   box.
3. Check the cloud provider and existing vendors for a service already
   available on the current plan.
4. Check for an internal package or shared library in a monorepo.

A hit here usually ends the run.

### Verdicts

**Question:** What do practitioners say after living with these options?

Roundups are marketing. This lane finds operational truth: what breaks at
scale, what the migration cost, who moved off what and why, and which option
people quietly regret.

Searches to run: `<option> problems`, `<option> vs <option> reddit`,
`migrated from <option>`, `why we moved off <option>`, `<option> hacker news`,
`<option> postmortem`.

Weight recent, specific, first-hand accounts. Discount vendor blogs and
SEO listicles.

### Counter-case

**Question:** When is building this yourself actually correct here, and where
do the incumbents fail?

Deliberately argues against adoption so the shortlist is not a foregone
conclusion. Looks for: adoption cost, operational burden, lock-in, licensing
traps (relicensing history, BSL/SSPL changes), acquisition/sunset risk, and
credible "we replaced the library with 80 lines" accounts.

### Frontier *(explore intent)*

**Question:** What shipped or changed in this space in the last 6–12 months?

Exists because model memory is stale exactly where it matters most. Prioritize
release notes, changelogs, launch posts, and dated discussion. Every item needs
a date.

### User-seeded

**Question:** Do the tools or sources the user named actually fit?

Only spawn when the user supplied seeds ("also check X", "look at this
newsletter", "I heard about Y"). Evaluate them on the same contract as
everything else — a user-named tool is a hypothesis, not a shortlist entry.

---

## Candidate row schema

Every lane returns rows in this shape:

```json
{
  "name": "pg-boss",
  "kind": "library | oss-project | saas | cloud-primitive | existing-dependency | stdlib | pattern",
  "url": "https://...",
  "does": "One line: the capability it actually provides",
  "ecosystem": "node | python | go | language-agnostic | ...",
  "liveness": "last release YYYY-MM-DD | last commit YYYY-MM-DD | active pricing page",
  "adoption": "stars, downloads/week, notable users — only if seen in a source",
  "license_or_pricing": "MIT | BSL 1.1 | free tier + usage-based | quote-only",
  "fits_because": "Tie to a specific stated constraint",
  "does_not_cover": "What the user would still have to build",
  "risk": "lock-in, relicensing history, sunset/acquisition, maintenance by one person",
  "source_url": "https://... (where these facts were read)",
  "checked": "YYYY-MM-DD",
  "confidence": "high | medium | low"
}
```

Rules for rows:

- `url` and `source_url` may be the same only when the facts came from the
  project's own page; prefer at least one independent source for adoption and
  operational claims.
- Unknown fields are omitted, never guessed. `"adoption": "popular"` is not a
  value.
- `does_not_cover` is mandatory. A candidate with nothing in that field was not
  evaluated against the real requirement.

---

## Merge rules

1. **Verify or drop.** No live URL from this run means the row does not exist.
2. **Kill the dead.** No release or meaningful commit in ~18 months, archived
   repo, sunset notice, or defunct company. Note them once as "considered and
   dead" rather than listing them.
3. **Deduplicate identities.** Rebrands, forks, hosted-versions-of-an-OSS-core,
   and wrappers around the same engine collapse to one entry with the variants
   named.
4. **Collapse repeated origins.** Five listicles citing one benchmark are one
   piece of evidence.
5. **Cluster by approach** before ranking: managed service / self-hosted
   runtime / in-your-datastore library / framework built-in / do nothing. The
   user picks an approach, then a name inside it.
6. **Rank against the constraints from the ground-truth step** — not by stars.
   An option that violates a hard constraint is disqualified regardless of
   popularity; mention it once and say why it is out.

---

## Stop conditions

Stop a lane, or the whole run, when:

- the cap is reached with no new names appearing
- new sources only recirculate the same origins
- the "already yours" lane finds the capability already installed or already
  billed
- a hard constraint eliminates every remaining category, making the
  roll-your-own answer definitive
- further research would cost more than the decision it informs

Do not keep searching to make the report look thorough.
