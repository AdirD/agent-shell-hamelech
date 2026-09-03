# Why `melech-consult` works this way

This skill used to convene Beit Hillel and Beit Shammai: two subagents, each assigned a side and told to build the strongest case for it, followed by a seven-part ruling that preserved both. That design was replaced. This document records why, so the reasoning is auditable and the next revision does not re-litigate it from scratch.

The short version: **assigning sides is the one configuration measured as no better than doing nothing, and the ingredient that actually works — genuinely different models, grounded in real evidence — was the part the old design treated as an implementation detail.**

---

## 1. What broke

Diagnosed from the skill text plus every real invocation in local agent transcripts.

**It never touched ground truth.** Step 1 converted the conversation into a prose brief, and every later step operated only on that brief. The word "codebase" never appeared in the skill. All seven mentions of "evidence" were about *naming* evidence someone else should later collect. So the consultation corrected the thread's conclusion bias while inheriting 100% of its premises — two fresh models handed the same unverified premise produce a confident, well-formatted wrong answer.

**The author still framed the question.** The skill removed the proposal's author from *arguing* but left it in charge of *stating the fork*, which is the more consequential half. In one real session the fork conflated the user's axis with a colleague's, and both houses then argued a question neither person had asked.

**Output weight never scaled.** Effort tiers scaled dispatch (one model, two, two plus a steelman round) but the seven-part ruling was mandatory at every tier. The tiering also contradicted itself: "Light" was defined for a "direct second opinion request", which was also the skill's headline trigger, while "Standard" was marked default.

**Two of seven sections existed to un-decide the decision.** Minority-preserved and reopen-when are right for an architecture decision record and read as hedging when someone asked who is right.

**The brief had no slot for a human party**, so "am I right or is he right" had nowhere to land. And it always emitted a ruling, never asking what artifact the user actually needed — a comment, a fix, a measurement.

---

## 2. What the research says

### Independent sampling does most of the work

[**Debate or Vote: Which Yields Better Decisions in Multi-Agent LLMs?**](https://arxiv.org/pdf/2508.17536) decomposed multi-agent debate into ensembling and inter-agent communication across seven benchmarks. Majority voting alone accounted for most of the gains usually credited to debate. They prove debate induces a **martingale** over agents' belief trajectories — expected correctness is unchanged across rounds.

Two conditions on that result matter enormously here:

- **Proposition 1** — the martingale holds when agents are *homogeneous and fully connected*, *fully isolated*, or *isolated homogeneous cliques*. **Appendix D.4** notes that heterogeneous, fully connected agents are *not necessarily* a martingale. So debate can help, but heterogeneity is the escape hatch.
- **Section 6 / Table 4** tested *persona* heterogeneity — Mathematician, Lawyer, Economist, Programmer; Doctor, Psychologist, Programmer — on a single model. The conclusion held. **Persona diversity does not buy decorrelated errors.** Job titles are costume; different models are real.

This is why the skill mandates different providers and forbids `inherit`, and why it does not lean on personas.

### Models cannot argue their way out of a shared error

[**Breaking the Martingale Curse**](https://arxiv.org/html/2603.06801) shows the neutrality result assumes independent errors, while real LLMs have *correlated* errors — the same logical traps. On subsets where the initial majority is wrong, majority voting reaches 14% and standard debate only 22%: debate **amplifies** a shared wrong belief.

Consequence for the design: external evidence is the only thing that escapes correlated error. That is what makes the grounding step non-negotiable rather than hygiene.

### Diversity and calibrated confidence are the mechanisms that help

[**Demystifying Multi-Agent Debate: The Role of Confidence and Diversity**](https://aclanthology.org/2026.findings-acl.1694/) (ACL 2026 Findings) identifies the two ingredients missing from vanilla debate: **diversity of initial viewpoints**, which raises the odds a correct hypothesis is in the pool at all, and **explicit calibrated confidence** that agents condition updates on. With both, it beats vanilla debate and majority vote.

This is why every consultant must return a 1–10 confidence plus what would change it, and why synthesis weights confidence over eloquence. It is also the sharpest argument against assigned sides: an agent ordered to argue a position cannot report that it believes the position is wrong, so the confidence signal is destroyed by construction.

### Escalate only when needed

[**Statistical Scouting Finds Debate-Safe but Not Debate-Useful Cases**](https://arxiv.org/html/2605.09618v1) finds the best protocol varies per example, and that routing only high-uncertainty cases to expensive interaction sharply reduces "debate backfire" while cutting cost. Hence: three independent reads first, escalate only on real disagreement.

### Collaborative beats adversarial for open decisions

**M3MADBench** ([arXiv 2601.02854](https://arxiv.org/pdf/2601.02854)) reports collaborative diverse debate outperforming adversarial debate "by a substantial margin" across modalities for open questions, plans, and decisions — the exact category consult serves.

### Only an attack on the *emerged* answer produces real disagreement

[**Inducing Disagreement in Multi-Agent LLM Executive Teams**](https://openreview.net/forum?id=mxBmj5LYU2) (OpenReview 2026) and [**LLM-Powered Devil's Advocate**](https://dl.acm.org/doi/10.1145/3640543.3645199) (IUI 2024): soft role-framing and "please dissent" instructions test **statistically indistinguishable from baseline** at producing genuine disagreement. A dedicated devil's advocate attacking the *emerging* answer measurably raises decision accuracy.

Beit Hillel and Beit Shammai were soft role-framing applied at the start — the configuration measured as equivalent to doing nothing. The single devil's advocate in step 4, aimed at the converged answer, is the configuration the evidence supports, at one call instead of three.

### Sycophancy is the failure mode to design against

[**Peacemaker or Troublemaker**](https://arxiv.org/pdf/2509.23055) (2026) and [**CONSENSAGENT**](https://aclanthology.org/2025.findings-acl.1141/) (ACL 2025): LLMs defer to each other and to the answer implied by the framing, which can drop a council *below* single-agent accuracy.

This is the direct justification for the hardest rule in the skill — consultants receive the artifact and never the conversation. Pasting thread history is handing every consultant the answer to defer to. It also motivates the standing instruction not to defer to the answer the framing expects.

### Reasoning-method diversity

**DMAD** ([ICLR 2025](https://openreview.net/forum?id=t6QHYUOQL7)) shows agents applying distinct *reasoning methods* outperform homogeneous ones. Offered as an optional lever in step 4 (inversion, decomposition, dependency-and-base-rate), stacked on top of model diversity rather than replacing it.

---

## 3. Evidence from actual usage

An earlier revision of this skill described itself as a *"proof-and-verify circuit"* that packaged the proposal into an objective brief for fresh isolated subagents. It was later rewritten around machloket. Splitting real invocations by which revision was live:

| Revision | Invocations | Outcome |
|---|---|---|
| proof-and-verify | onboarding-prompt diagnosis, article-audience fix, design disagreement with a colleague | two clean wins; one good analysis delivered in the wrong format |
| machloket / houses | article section, skill naming | *"more confused now"*; ruling rejected over an unstated constraint |

Every success dispatched an independent **panel**. Every "more confused" outcome ran the **two houses**.

Caveat worth stating plainly: single user, roughly six invocations. On its own that is anecdote. Its value is that it points the same direction as the published work — two independent lines of evidence agreeing.

Recurring gap across the corpus: users invoked consult wanting **escape velocity from a thread they had stopped trusting** — a fact or a verdict. The old skill assumed the hard part was choosing between two defensible worlds, when the hard part was usually "is this premise even true?" or "write the thing."

---

## 4. Design decisions

| Decision | Rationale |
|---|---|
| Verify premises before consulting; allow the skill to end there | Correlated error is only broken by external evidence |
| Consultants receive artifacts, never conversation | Sycophancy / conformity can push a panel below a single agent |
| Three independent consultants, no assigned sides | Independent sampling accounts for most measured gains; advocacy destroys the confidence signal |
| Different providers, never `inherit` | Heterogeneity is the documented escape from the martingale; persona diversity was tested and failed |
| Mandatory 1–10 confidence plus what would change it | Confidence-modulated aggregation is what makes deliberation drift toward truth |
| Consultants explicitly invited to reject the framing | Fixed two-option framing cannot surface a third answer or a false premise |
| One devil's advocate, only on disagreement, aimed at the emerging answer | The only configuration shown to induce genuine disagreement; adaptive routing cuts backfire and cost |
| Four output shapes, length scaled to the finding | The old mandatory seven-part ruling produced "more confused now" on small questions |
| Explicit refuse-cheaply path | Running a panel on a settled question is the most visible failure |
| Dispatch disclosed honestly, including failures | Undisclosed same-model panels masquerade as corroboration |
| Beit Hillel / Beit Shammai removed as machinery | Assigned-side framing is baseline-equivalent; `psak` and the machloket ethic are retained as the library's voice |

---

## 5. Prior art

- **LLM Council** — [Andrej Karpathy](https://github.com/karpathy/llm-council). The original independent-panel-plus-chairman shape, using different LLMs.
- [**ngmeyer/council-review**](https://github.com/ngmeyer/council-review) — the strongest public implementation of this pattern: method diversity, anonymized peer review, "what did all five miss?", confidence weighting, adaptive stopping, mediating assessments, dissent preservation. Worth reading before revising this skill. It costs 12 agent calls and states its own limitation — *"this skill uses persona/method diversity, not model diversity"* — which is precisely the gap `melech-consult` fills with cross-provider dispatch plus repo grounding.

Where this skill deliberately differs: it stays cheap (three calls, escalating to four) because it is invoked as a mid-flow interrupt with a human waiting, and it treats verification against the real repository as a required step rather than optional context-gathering.

---

## 6. Citation provenance

Read directly from the source: *Debate or Vote*, *Breaking the Martingale Curse*, *Statistical Scouting*, *Demystifying MAD* (abstract).

Taken from `council-review`'s bibliography and not read in full: *M3MADBench*, *DMAD (ICLR 2025)*, the two devil's-advocate papers, *Peacemaker or Troublemaker*, *CONSENSAGENT*. Their claims are reported as that skill characterizes them. Verify before treating any of them as load-bearing in a future revision.
