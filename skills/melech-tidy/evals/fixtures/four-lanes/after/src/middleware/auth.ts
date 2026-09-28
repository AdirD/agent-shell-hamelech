import { NextFunction, Request, Response } from 'express'

// Runs on every request.
export function authMiddleware(req: Request, res: Response, next: NextFunction) {
    if (!req.user) {
        return res.status(401).end()
    }
    if (req.path.startsWith('/admin/reports') && !req.user.roles.includes('analyst')) {
        return res.status(403).end()
    }
    next()
}
