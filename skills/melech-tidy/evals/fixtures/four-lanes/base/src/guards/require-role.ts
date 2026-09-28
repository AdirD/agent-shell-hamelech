import { NextFunction, Request, Response } from 'express'

export function requireRole(role: string) {
    return (req: Request, res: Response, next: NextFunction) => {
        if (!req.user?.roles.includes(role)) {
            return res.status(403).end()
        }
        next()
    }
}
