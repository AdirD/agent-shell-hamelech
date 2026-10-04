---
name: melech-plan-diff
description: >-
  Foresee a solution before approval as a changes tab: a file tree of red and
  green pseudo-code, for a product reader, not a code deep dive. Use when the
  user wants to see what would change, a git-like diff, or the PR as if it
  were ready.
disable-model-invocation: true
---

# Plan diff

Foresee this solution before they approve it. Show what would change, and what
they should expect, as a file tree of git-like red and green lines, as if the
PR is ready and they are looking at the changes tab.

The page is for them or a product reader. They are not looking to deep-dive
the code.

Mark each part of a file with a blue `@@ section @@` line. Indent the way a
diff would. Write a sentence when the behavior is the point. Write a short
code line when that is easier to read than the sentence. Do not paste the
surrounding implementation.

Copy [template.html](template.html), fill every `{{TOKEN}}`, and open the page.
