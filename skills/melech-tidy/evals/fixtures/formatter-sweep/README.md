# Formatter sweep fixture

Requirement: fix the checkout crash when `cart.discount` is undefined in
`calculateTotal`. Nothing else was requested.

Repository facts:

- The base style in `src/checkout/` is 4-space indentation, single quotes, and
  no semicolons.
- CI runs `eslint` and `npm test` only. There is no formatter check.
- The agent's editor reformatted the file on save with a different style.

Treat `change.diff` as the uncommitted working diff.
