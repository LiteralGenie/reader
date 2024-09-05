import { dev } from '$app/environment'
import * as fs from 'fs'
import * as path from 'path'
import * as toml from 'toml'

// dev      /reader/web/src/hooks.server.ts
// preview  /reader/web/.svelte-kit/output/server/chunks/hooks.server.js
// prod     /reader/web/build/server/chunks/hooks.server-BJa2SaKc.js
export function loadConfig(): Config {
    let fpConfig: string
    if (dev) {
        fpConfig = path.resolve(
            import.meta.filename,
            '..',
            '..',
            '..',
            '..',
            'config.toml'
        )
    } else if (
        import.meta.filename.endsWith(
            '.svelte-kit/output/server/chunks/hooks.server.js'
        )
    ) {
        fpConfig = path.resolve(
            import.meta.filename,
            '..',
            '..',
            '..',
            '..',
            'config.toml'
        )
    } else {
        fpConfig = path.resolve(
            import.meta.filename,
            '..',
            '..',
            '..',
            '..',
            '..',
            'config.toml'
        )
    }

    const config = Config.loadToml(fpConfig)

    return config
}

export class Config {
    constructor(
        public root_image_folder: string,
        public api_host: number,
        public api_port: number
    ) {}

    static loadToml(fp: string) {
        const data: any = toml.parse(
            fs.readFileSync(fp, { encoding: 'utf-8' })
        )

        return Config.load(data)
    }

    static load(data: any) {
        return new Config(
            data.root_image_folder,
            data.api_host,
            data.api_port
        )
    }

    get apiUrl(): string {
        return `http://${this.api_host}:${this.api_port}`
    }
}
