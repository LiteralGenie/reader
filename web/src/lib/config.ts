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
        public series_folder: string,
        public api: ApiConfig
    ) {}

    static loadToml(fp: string) {
        const data: any = toml.parse(
            fs.readFileSync(fp, { encoding: 'utf-8' })
        )

        data.api = ApiConfig.load(data.api)

        return Config.load(data)
    }

    static load(data: any) {
        return new Config(data.series_folder, data.api)
    }

    get apiUrl(): string {
        return `http://localhost:${this.api.port}`
    }
}

export class ApiConfig {
    constructor(public port: number) {}

    static load(data: any) {
        return new ApiConfig(data.port)
    }
}
