---
name: melech-idea-to-canvas
description: Turn rough ideas or docs into a standalone Cursor Canvas for team understanding.
disable-model-invocation: true
---

Turn @<input> into a standalone Cursor Canvas that helps the team quickly understand and align on how we are going to build this.

Accept any starting point: a rough idea, a shower thought, a Slack thread dump, meeting notes, a decision log, a product brief, a PRD fragment, a design doc, an RFC, or a tech spec. The less structured the input, the more the skill must do the structuring work.

This is primarily a knowledge-transfer artifact — not an approval workflow, debate space, or prettier copy of the input.

Core objective:
Make what the author knows as easy as humanly possible for the team to absorb without losing important meaning, decisions, constraints, or implementation direction.

Before building the canvas, identify:
- The problem and why it matters
- The intended outcome
- The core mental model
- The proposed system and how its parts work together
- The key flows, states, boundaries, and ownership
- Important decisions and their reasoning
- Constraints, risks, assumptions, and explicit non-goals
- The implementation sequence and what each team or component owns
- Details needed for alignment versus details that can be progressively disclosed

If the input is rough or unstructured, make reasonable inferences to fill gaps, clearly mark them as inferred or assumed, and surface anything the canvas exposes that the author may not have considered.

Presentation principles:
- Less is more. Do not reproduce the input section by section.
- Prefer showing over explaining.
- Use short, direct text only where visuals cannot carry the meaning.
- Compartmentalize information into independently understandable views.
- Establish a strong hierarchy: essential understanding first, implementation detail second.
- Optimize for a reader with 5–10 minutes while allowing deeper exploration.
- Keep important decisions visible.
- Put minor mechanics and exhaustive detail in expandable sections or a compact technical appendix.
- Do not hide uncertainty, meaningful trade-offs, dependencies, or unresolved risks.
- Do not give every detail equal visual weight.
- Do not add decorative charts, generic cards, fake metrics, or visuals that explain nothing.
- Do not overemphasize sign-off, approval status, stakeholder debate, or governance.

Drawings:
- Use drawings whenever they communicate a point faster or more clearly than prose.
- Treat drawings as explanatory tools, not decoration.
- Use them to explain relationships, flows, boundaries, states, timing, ownership, and cause-and-effect.
- When a drawing carries the idea, keep its supporting text minimal.
- Every drawing should answer a specific question and be understandable without narration.
- Do not force a visual when a sentence or short list is clearer.

Choose only visual forms that genuinely clarify the idea, such as:
- A system or component map
- A user-to-system journey
- A sequence or data-flow diagram
- A lifecycle or state model
- Responsibility and ownership boundaries
- A phased implementation path
- A focused comparison for a meaningful trade-off

Suggested narrative:
1. What we are building and why
2. The one-minute mental model
3. How the system works end to end
4. The main building blocks and their responsibilities
5. Critical flows, states, and edge cases
6. Decisions that shape the implementation
7. How we will build and roll it out
8. Risks, assumptions, and intentionally deferred details
9. Compact technical reference for readers who need depth

Accuracy requirements:
- Preserve the source's intent.
- Do not invent requirements, decisions, or certainty beyond what can be reasonably inferred.
- Clearly distinguish decided, assumed, proposed, and unresolved items.
- Preserve important terminology from the source.
- If the input contains contradictions or gaps, surface them quietly and precisely without turning the canvas into a review report.

Canvas requirements:
- Create an actual `.canvas.tsx` artifact using the Cursor Canvas skill.
- Make it useful as a standalone artifact without requiring the source input beside it.
- Use strong visual hierarchy and varied composition — not a wall of identical cards.
- Use progressive disclosure for secondary details.
- Keep every view purposeful and scannable.
- Include no placeholders or empty sections.
- Before finishing, remove anything that does not improve understanding or implementation alignment.

Final test:
For every section, ask:
1. What must the reader understand here?
2. Can it be shown more clearly than written?
3. What can be removed without losing meaning?
