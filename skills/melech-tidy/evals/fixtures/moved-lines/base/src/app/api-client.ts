const httpFetch = globalThis.fetch

export function createClient(baseUrl: string) {
    return {
        get: (path: string) => httpFetch(`${baseUrl}${path}`),
    }
}
