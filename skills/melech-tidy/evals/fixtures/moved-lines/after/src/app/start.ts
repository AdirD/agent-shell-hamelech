import { createClient } from './api-client'
import './polyfills'
import { loadSettings } from './settings'

export function start() {
    const config = loadSettings()
    const client = createClient(config.apiUrl)
    return client
}
