import { env } from '$env/dynamic/private'
import { loadConfig } from '$lib/config'
import type { Handle } from '@sveltejs/kit'

const config = loadConfig()
console.log('Using config:\n', config)

export const handle: Handle = async ({ event, resolve }) => {
    // @ts-ignore
    env.config = config

    const response = await resolve(event)
    return response
}
