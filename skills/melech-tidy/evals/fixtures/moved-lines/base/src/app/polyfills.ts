import { fetch as undiciFetch } from 'undici'

if (!globalThis.fetch) {
    globalThis.fetch = undiciFetch as typeof fetch
}
