# ROI receipt examples

Use these as structural examples, not fixed wording or scoring fixtures. Ground
every label, count, severity, score, and rank in the current diff, PR, or
discussion. Never invent candidate solutions merely to populate a ranking.

## Example 1: narrow problem, broad solution

```text
╭────────────── CHANGE ROI RECEIPT ──────────────╮
│ Prevent duplicate checkout submissions         │
│                                                │
│ ROI                                      58/100 │
│ GRADE                                        C– │
├────────────────────────────────────────────────┤
│ PROBLEM REACH                                  │
│ Checkout submits only        █ 1 path          │
│                                                │
│ SOLUTION REACH                                 │
│ All incoming requests        ███████████ 47    │
├────────────────────────────────────────────────┤
│ VALUE RECEIVED                                 │
│ ✓ Complete fix                                 │
│ ✓ Durable                                      │
│ ✓ Covers the known failure                     │
│                                                │
│ COST CHARGED                                   │
│ ● Shared middleware changed               HIGH │
│ ● Unrelated requests carry the logic       HIGH │
│ ● New persisted state                    MEDIUM │
│ ● New cleanup lifecycle                  MEDIUM │
├────────────────────────────────────────────────┤
│ LARGEST CHARGE                                 │
│ 47 request paths carry a fix that benefits 1.  │
├────────────────────────────────────────────────┤
│ VERDICT                                        │
│ The solution works, but its reach is larger    │
│ than the problem it solves.                    │
╰────────────────────────────────────────────────╯
```

## Example 2: systemic problem, shared solution

```text
╭────────────── CHANGE ROI RECEIPT ──────────────╮
│ Reject expired sessions consistently           │
│                                                │
│ ROI                                      92/100 │
│ GRADE                                         A │
├────────────────────────────────────────────────┤
│ PROBLEM REACH                                  │
│ Protected request paths      ███████████ 38    │
│                                                │
│ SOLUTION REACH                                 │
│ Protected request paths      ███████████ 38    │
├────────────────────────────────────────────────┤
│ VALUE RECEIVED                                 │
│ ✓ Closes the failure on every affected path    │
│ ✓ Enforces one consistent contract             │
│ ✓ Removes per-handler behavior drift           │
│                                                │
│ COST CHARGED                                   │
│ ● Shared authentication boundary changed  HIGH │
│ ● Regression exposure across 38 paths      HIGH │
│ ● No new persisted state                    LOW │
│ ● No new lifecycle                          LOW │
├────────────────────────────────────────────────┤
│ LARGEST CHARGE                                 │
│ A shared boundary changes, but all 38 paths     │
│ receive the benefit they now carry.             │
├────────────────────────────────────────────────┤
│ VERDICT                                        │
│ The solution's reach matches the problem's      │
│ reach.                                         │
╰────────────────────────────────────────────────╯
```

## Example 3: durable value with real operating cost

```text
╭────────────── CHANGE ROI RECEIPT ──────────────╮
│ Retry failed report exports                    │
│                                                │
│ ROI                                      76/100 │
│ GRADE                                         B │
├────────────────────────────────────────────────┤
│ PROBLEM REACH                                  │
│ Failed export jobs           ███████ 12%       │
│                                                │
│ SOLUTION REACH                                 │
│ All export jobs              ███████████ 100%  │
├────────────────────────────────────────────────┤
│ VALUE RECEIVED                                 │
│ ✓ Recovers transient failures automatically    │
│ ✓ Prevents users from rebuilding reports       │
│ ✓ Produces durable delivery state              │
│                                                │
│ COST CHARGED                                   │
│ ● New retry state                         HIGH │
│ ● New worker lifecycle                    HIGH │
│ ● All exports enter retry-aware handling MEDIUM │
│ ● Behavior remains inside export subsystem LOW │
├────────────────────────────────────────────────┤
│ LARGEST CHARGE                                 │
│ Every export now carries a retry lifecycle,     │
│ including the 88% that succeed immediately.     │
├────────────────────────────────────────────────┤
│ VERDICT                                        │
│ The value justifies meaningful machinery, but   │
│ the machinery has permanent operating cost.     │
╰────────────────────────────────────────────────╯
```

## Example 4: ranking only solutions already raised

The discussion already contains three concrete solutions. Evaluate each one;
do not add a fourth.

```text
ROI RANKING — 3 SOLUTIONS RAISED

#1  Handler-level deduplication       84/100  B+
#2  Shared request middleware         58/100  C–
#3  New deduplication service         34/100  F
```

```text
╭────────────── CHANGE ROI RECEIPT ──────────────╮
│ Shared request middleware                      │
│                                                │
│ ROI                                      58/100 │
│ GRADE                                        C– │
│ RANK                           #2 of 3 raised   │
├────────────────────────────────────────────────┤
│ PROBLEM REACH                                  │
│ One submission path          █ 1               │
│                                                │
│ SOLUTION REACH                                 │
│ All request paths            ███████████ 47    │
├────────────────────────────────────────────────┤
│ VALUE RECEIVED                                 │
│ ✓ Fixes the complete duplicate-submit case     │
│ ✓ Centralizes enforcement                      │
│                                                │
│ COST CHARGED                                   │
│ ● Shared middleware changed               HIGH │
│ ● Unrelated requests carry the logic       HIGH │
│ ● New persisted state                    MEDIUM │
├────────────────────────────────────────────────┤
│ LARGEST CHARGE                                 │
│ Most paths carrying the solution cannot receive │
│ its benefit.                                   │
├────────────────────────────────────────────────┤
│ VERDICT                                        │
│ Complete fix; disproportionate solution reach. │
╰────────────────────────────────────────────────╯
```

## Example 5: evidence is incomplete

Do not manufacture precise counts or confident grades when evaluating an idea
that has not yet become code.

```text
╭────────────── CHANGE ROI RECEIPT ──────────────╮
│ Cache generated previews                       │
│                                                │
│ ROI                                      67/100 │
│ GRADE                                         C │
│ CONFIDENCE                                   LOW │
├────────────────────────────────────────────────┤
│ PROBLEM REACH                                  │
│ Slow preview requests        ███ unknown       │
│                                                │
│ SOLUTION REACH                                 │
│ Preview generation pipeline  █████ estimated   │
├────────────────────────────────────────────────┤
│ VALUE RECEIVED                                 │
│ ? Expected latency reduction                   │
│ ? Frequency not yet measured                   │
│                                                │
│ COST CHARGED                                   │
│ ● Cache invalidation lifecycle          MEDIUM │
│ ● Additional storage dependency         MEDIUM │
│ ? Operational volume unknown             UNKNOWN │
├────────────────────────────────────────────────┤
│ LARGEST CHARGE                                 │
│ The proposed lifecycle is concrete; the volume │
│ of users receiving the benefit is not.         │
├────────────────────────────────────────────────┤
│ VERDICT                                        │
│ Potentially proportionate, with low confidence │
│ until problem frequency is known.              │
╰────────────────────────────────────────────────╯
```

