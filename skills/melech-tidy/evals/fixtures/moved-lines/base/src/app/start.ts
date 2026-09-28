import './polyfills'
import { createClient } from './api-client'
import { loadSettings } from './settings'

export function start() {
    const client = createClient(config.apiUrl)
    const config = loadSettings()
    return client
}
