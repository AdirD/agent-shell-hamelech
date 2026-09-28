import { listUsers } from '../services/users'

export const usersRoute = {
    path: '/users',
    guards: [],


    handler: async () => listUsers(),
}
