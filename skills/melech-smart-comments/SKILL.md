---
name: melech-smart-comments
description: Preserve code intent with selective comments and protect meaningful existing comments.
---

# Smart Comments

You are often the first reader of this code. You do not carry the scar tissue a human teammate would — you did not live through the incident that caused a function to look the way it does, and you cannot smell the landmine from the shape of the code alone.

Comments are the spec layer closest to the code. They are the last thing a model reads before producing the next token, and they are the cheapest, highest-signal way for a human to hand you constraints, warnings, and intent. Treat them accordingly.

This skill governs how you write new comments and how you treat existing ones.

## When to Write a Comment

Write an inline comment when one of these is true. Otherwise do not.

1. **Landmines.** Code that looks wrong, redundant, or removable but is not. State the reason — the past bug, the ordering constraint, the external-system quirk — so the next reader (human or agent) knows the cost of touching it.
2. **Non-obvious WHY.** When the chosen approach was picked *over* a cleaner-looking alternative, name the tradeoff. "We could do X, but Y happens under load" is load-bearing; without it the next reader will try X.
3. **Hidden invariants and contracts.** Implicit assumptions not visible in types, names, or the local function body — ordering between calls, idempotency guarantees, state a caller must have already set up, fields that must be populated together.
4. **Workarounds.** Bugs in external systems, race conditions, temporary version pins, polyfills, hacks waiting on an upstream fix. Link or name the issue if one exists.

## When NOT to Write a Comment

Do not write a comment when:

- It narrates WHAT the code does and the identifiers already say it. `// increment counter` above `counter++` is noise.
- It refers to the current task, ticket, PR, author, or review round. Those belong in the commit message or PR description. They rot in the code.
- It is a banner, section divider, or restatement of the function signature.
- It describes intent the code itself will carry forward reliably through refactors — if a rename makes the comment wrong, the comment was redundant.

If the WHY is obvious from the name of the function and its arguments, the comment is not paying for its space.

## How to Write Them

- **Inline.** Directly above or beside the line they protect. Not at the top of the file, not in external docs, not in a commit message.
- **Short.** Lead with the constraint or the warning. No wind-up.
- **Imperative where it matters.** Prefer "Do not reorder — must run before X" over "This runs before X."
- **Name the cost.** "Removing this early-return reopens the N+1 we fixed" beats "important early return."
- **If a comment needs more than about three lines**, the code itself is probably wrong. Fix the code, not the comment.

## Respecting Existing Comments

This section is the reason this skill exists.

- **Treat every existing comment as load-bearing until proven otherwise.** Someone — human or past agent — paid a cost to leave it there. Assume that cost was real.
- **Do not delete a comment during a refactor** unless the code the comment describes is also being removed. Moving code does not justify dropping its comment.
- **"Looks redundant" is not sufficient justification** for removal. The comment may be the only surviving trace of a past incident that the code itself no longer advertises.
- **If a comment looks stale or wrong**, flag it in your response to the user. Do not silently fix or remove it. The user is the only one who can confirm whether the comment still reflects reality.
- **Never rewrite a comment just to change voice or tone.** If it reads as a warning, keep it as a warning.

## Calibration Examples

Bad — narrates what the code already says:
```python
# Increment the retry counter
retries += 1
```

Good — names the landmine:
```python
# Do not switch to exponential backoff here; upstream rate-limits on burst, not on average.
retries += 1
```

Bad — rots on the next refactor:
```ts
// Added in PR #4821 by @alice to handle the new billing webhook
if (event.type === "invoice.paid") { ... }
```

Good — preserves the WHY:
```ts
// Stripe fires invoice.paid before invoice.finalized for auto-advancing subs; handle both orderings.
if (event.type === "invoice.paid") { ... }
```

Bad — decorative, adds no signal:
```go
// ---------- Helpers ----------
```

Good — encodes a hidden contract:
```go
// Caller must hold s.mu. Returns the unwrapped value; safe only until the next Set().
func (s *state) peek() T { ... }
```

## Summary

Code shows movement. Comments preserve memory. You are the reader that will most often decide whether that memory survives the next edit. When in doubt, leave the comment, and ask the human whether it should go.
