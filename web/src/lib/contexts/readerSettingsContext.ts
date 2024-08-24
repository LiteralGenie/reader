import { getContext, setContext } from 'svelte'
import { type Readable, writable } from 'svelte/store'
import { getWindow } from '../miscUtils'

const CTX_KEY = 'reader_settings'
const STORAGE_KEY = 'reader_settings'

const DEFAULT_SETTINGS: SettingsContextValue = {
    debugBboxs: false
}

export interface SettingsContextValue {
    debugBboxs: boolean
}

export interface SettingsContext {
    settings: Readable<SettingsContextValue>
    setSettings: (update: SettingsContextValue) => void
}

export function createReaderSettingsContext() {
    const storageSettings =
        getWindow()?.localStorage.getItem(STORAGE_KEY)

    let initSettings = { ...DEFAULT_SETTINGS }
    try {
        initSettings = {
            ...initSettings,
            ...JSON.parse(storageSettings ?? '{}')
        }
    } catch {}

    const settingsStore = writable(initSettings)

    const ctx = {
        settings: settingsStore,
        setSettings
    }

    setContext<SettingsContext>(CTX_KEY, ctx)

    return ctx

    function setSettings(settings: SettingsContextValue) {
        settingsStore.set(settings)

        getWindow()?.localStorage.setItem(
            STORAGE_KEY,
            JSON.stringify(settings)
        )
    }
}

export function getReaderSettingsContext() {
    return getContext<SettingsContext>(CTX_KEY)
}
