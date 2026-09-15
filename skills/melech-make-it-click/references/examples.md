# Make It Click — grounded examples

These examples are adapted from real agent conversations. They show three
different failure modes: answering too broadly, leaving an abstract term
unmapped, and explaining complexity that should be removed.

## 1. Resolve the one feared consequence

### Before

The agent explains that a live chat model has a 160k context window while a
smaller summarizer can read only 120k at a time. It discusses separate budgets,
trigger math, overflow handling, and chunk-and-fold summarization.

The user asks:

> I don't understand. If the chat reached 160k and the summarizer only reads
> 120k, are we missing data?

### `/melech-make-it-click`

> The remaining 40k is included; it does not disappear.
>
> The summarizer cannot read all 160k at once, so it does two passes:
>
> 1. First 120k → summary A
> 2. Remaining 40k → summary B
> 3. A + B → final summary
>
> Every part of the conversation is fed into the process. The tradeoff is that
> summarization is lossy, so the summaries may omit details.

### Why this route works

The user's blocker is not the architecture. It is one feared consequence:
"does the last 40k disappear?" The recovery answers that first with one concrete
160k example.

## 2. Replace an abstract term with a tiny executable model

### Before

The agent says that the Lighthouse Node API returns a report "in memory" and
then lists report objects, artifacts, CLI behavior, temporary browser profiles,
and disk output.

The user asks:

> What do you mean by in memory? Simulate it.

### `/melech-make-it-click`

> It means the result is held in a JavaScript variable while the program is
> running:
>
> ```js
> const report = await lighthouse(url);
> console.log(report.lhr.categories.performance.score);
> ```
>
> `report` exists just like `const answer = 2 + 2`. Lighthouse has not saved a
> file or database row. When the program ends, that variable disappears.
>
> To keep it, your code must explicitly write it somewhere.

### Why this route works

"In memory" sounds like infrastructure until it is mapped to an ordinary local
variable. A tiny code example creates the missing mental object faster than a
more complete description of Lighthouse.

## 3. Notice when the confusing concept should not exist

### Before

The agent says:

> UUID is the skill ID in the agent context; slug is REST-only, so there is no
> identifier confusion.

The user asks whether existing skills need a migration, then asks why system
skills need slugs when user skills do not have them.

### `/melech-make-it-click`

> They do not need slugs.
>
> Existing user skills already use one UUID everywhere. We proposed giving
> system skills two identifiers:
>
> - UUID for internal lookups
> - slug for prettier API URLs
>
> The slug adds a column, validation, and a second lookup path without solving a
> real need. Use the UUID everywhere, like existing skills. No migration of
> existing user skills is needed.

### Why this route works

The problem is not that "slug" needs a friendlier definition. The proposed
concept is unnecessary. Making it click means deleting the false complexity,
not explaining it more patiently.
