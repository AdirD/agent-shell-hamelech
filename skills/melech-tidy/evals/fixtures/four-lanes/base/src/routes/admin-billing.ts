import { requireRole } from '../guards/require-role'
import { listInvoices } from '../services/billing'

export const adminBillingRoute = {
    path: '/admin/billing',
    guards: [requireRole('billing-admin')],
    handler: async () => listInvoices(),
}
