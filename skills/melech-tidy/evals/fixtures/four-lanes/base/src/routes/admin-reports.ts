import { listReports } from '../services/reports'

export const adminReportsRoute = {
    path: '/admin/reports',
    guards: [],
    handler: async () => listReports(),
}
