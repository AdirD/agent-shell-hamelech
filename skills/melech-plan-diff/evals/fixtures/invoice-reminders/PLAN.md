# Invoice reminders

Locked.

Email the account owner one day before an invoice is due. Send one email per invoice. Skip invoices that are already paid or already reminded.

This change touches:

- `apps/api/src/billing/invoices.ts` — remember that this invoice was reminded
- `apps/api/src/billing/invoice-reminder.ts` — new file. Find invoices due tomorrow and send the email

Not in this change:

- no settings screen
- no database migration
- no in-app banner

Sending mail already exists on the invoice mailer. Do not redesign it.
