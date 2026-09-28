export function loadSettings() {
    return { apiUrl: process.env.API_URL ?? 'http://localhost:3000' }
}
