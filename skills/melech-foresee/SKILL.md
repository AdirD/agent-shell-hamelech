---
name: melech-foresee
description: >-
  Show a settled plan as a changes-tab forecast: a file tree with red and
  green pseudo-diffs a reviewer can approve before implementation. Use when
  the user wants to foresee the solution, see the PR before approving, or
  review a fake diff without reading real code.
disable-model-invocation: true
---

# Foresee

Show the settled plan as the changes tab of a PR that does not exist yet.

You are not implementing, and you are not reopening the design. The reader is
deciding whether to approve the shape. They may be a product reader. They are
not here to deep-dive code.

If the concept is still open, stop. Name what is unsettled and point at
`melech-pre-plan`. Do not invent the plan inside the forecast.

## Produce one page

Copy [template.html](template.html) and replace `/* FORESEE_FILES */` with the
file objects. Leave the shell alone: tree on the left, red and green lines on
the right, one plain-language reason per file.

Write it next to the source plan when that plan is a file in the repo, named
`<plan-basename>-forecast.html`. When the plan lives only in the thread, write
`docs/forecasts/<short-slug>-forecast.html`, creating that directory when
`docs/` exists. If the repo has no `docs/`, write it in the worktree root and
say so. Do not put it under source that ships.

Open the file in the browser.

## Fill the tree from the plan

Read the locked decisions, then look up where this repo would actually put the
change. Folders and filenames must be places the PR would touch or sit beside.
The line bodies stay fake.

Each object:

- `folder`, `name` — real parent, real filename
- `status` — `A`, `M`, or `D`
- `add`, `del` — rough line counts. The header totals must equal the sums
- `why` — one sentence a product reader understands
- `lines` — `{ t, text }` where `t` is `hunk`, `ctx`, `add`, or `del`

Line rules:

- A hunk names the behavior in words (`@@ sending the reminder @@`), not a
  real line range.
- An add line states what the new behavior does.
- A context line states what stays.
- A del line states the behavior this PR stops.
- Write sentences. No imports, signatures, types, or code copied from the repo.
- Prefer the file that carries the behavior to be the longest. The page opens
  that file.

Header chips name what a reviewer might assume is in the diff and is not:
no settings screen, no migration, no unrelated edit. Three to six chips.
Replace the sample chips in the template.

## Reply in chat

Keep the reply short. Do not paste the diffs.

```text
The forecast is open. It is a changes-tab sketch, not the implementation: <N> files, +<add> −<del>, pseudo-code only.

`<path>`

Click a file on the left. Green is new behavior. Red is behavior this PR stops.

What that PR would contain:
- ...

What you would not see:
- ...
```

Questions about a file are answered from the forecast and the locked plan, in
the same plain language. Do not start coding, and do not grow the design,
unless the user changes the plan.

## Example entry

A locked decision "email the account owner one day before an invoice is due,
and do not add a settings screen" can include:

```js
{
  folder: "apps/api/src/billing",
  name: "invoice-reminder.ts",
  status: "A",
  add: 18,
  del: 0,
  why: "Sends one reminder the day before an invoice is due. No new screen.",
  lines: [
    { t: "hunk", text: "@@ the day before a due invoice @@" },
    { t: "add", text: "find invoices due tomorrow that have not been reminded" },
    { t: "add", text: "email the account owner once" },
    { t: "add", text: "remember that this invoice was reminded" },
    { t: "add", text: "skip invoices that are already paid or already reminded" },
  ],
}
```
