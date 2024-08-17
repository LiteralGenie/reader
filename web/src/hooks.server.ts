import { dev } from '$app/environment'
import { env } from '$env/dynamic/private'
import type { Handle } from '@sveltejs/kit'
import * as fs from 'fs'
import * as path from 'path'
import * as toml from 'toml'

// dev      /reader/web/src/hooks.server.ts
// preview  /reader/web/.svelte-kit/output/server/chunks/hooks.server.js
// prod     /reader/web/build/server/chunks/hooks.server-BJa2SaKc.js

let fpConfig: string
if (dev) {
    fpConfig = path.resolve(import.meta.filename, '..', '..', '..', 'config.toml')
} else if (import.meta.filename.endsWith('.svelte-kit/output/server/chunks/hooks.server.js')) {
    fpConfig = path.resolve(import.meta.filename, '..', '..', '..', '..', 'config.toml')
} else {
    fpConfig = path.resolve(import.meta.filename, '..', '..', '..', '..', '..', 'config.toml')
}

const config = toml.parse(fs.readFileSync(fpConfig, { encoding: 'utf-8' }))
console.log('Using config:\n', config)

export const handle: Handle = async ({ event, resolve }) => {
    // @ts-ignore
    env.CONFIG = config

    const response = await resolve(event)
    return response
}
