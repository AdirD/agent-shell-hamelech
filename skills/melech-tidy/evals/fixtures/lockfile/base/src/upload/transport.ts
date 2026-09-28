export class NetworkError extends Error {}

export async function sendFile(file: File): Promise<Response> {
    try {
        return await fetch('/upload', { method: 'POST', body: file })
    } catch (error) {
        throw new NetworkError(String(error))
    }
}
