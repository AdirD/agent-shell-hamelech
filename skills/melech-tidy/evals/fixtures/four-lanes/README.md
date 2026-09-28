# Four lanes fixture

Requirement: only users with the `analyst` role may open the admin reports
page. Nothing else was requested.

Repository facts:

- `src/middleware/auth.ts` runs on every request in the app.
- `src/routes/admin-reports.ts` already exposes a per-route `guards` array,
  and other admin routes put role checks there.
- A repo-wide search finds no references to `formatReportDate` outside its
  own definition.
- `skills/release/SKILL.md` already says, earlier in the file: "Run the full
  test suite before tagging a release."
- CI runs `eslint` and `npm test`. There is no formatter check.

Treat `change.diff` as the uncommitted working diff.
