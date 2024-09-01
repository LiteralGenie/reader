import { getContext, setContext } from 'svelte'
import {
    derived,
    type Readable,
    type Writable,
    writable
} from 'svelte/store'
import { getWindow, type Unsubscribe } from '../miscUtils'

const CTX_KEY = 'theme'
const STORAGE_KEY = 'theme'

const ALL_THEMES = ['auto', 'dark', 'light'] as const
export type RawTheme = (typeof ALL_THEMES)[number]
export type Theme = Exclude<RawTheme, 'auto'>

const DEFAULT_THEME = 'dark'

export interface ThemeContext {
    rawTheme: Writable<RawTheme>
    theme: Readable<Theme>
    setTheme: (theme: RawTheme) => void
    destroy: Unsubscribe
}

export function createThemeContext() {
    const storageTheme =
        getWindow()?.localStorage.getItem(STORAGE_KEY)
    const initTheme = ALL_THEMES.includes(storageTheme as any)
        ? (storageTheme as RawTheme)
        : 'auto'

    const rawThemeStore = writable(initTheme)
    rawThemeStore.subscribe((theme) => {
        let realTheme: Theme
        if (theme === 'auto') {
            realTheme = getMediaTheme() ?? DEFAULT_THEME
        } else {
            realTheme = theme
        }
    })

    const themeStore = derived(rawThemeStore, (theme) => {
        let realTheme: Theme
        if (theme === 'auto') {
            realTheme = getMediaTheme() ?? DEFAULT_THEME
        } else {
            realTheme = theme
        }

        return realTheme
    })

    const unsubTheme = themeStore.subscribe((theme) => {
        if (theme === 'light') {
            getWindow()?.document.body.classList.remove('dark')
        } else {
            getWindow()?.document.body.classList.add('dark')
        }
    })

    const ctx = {
        rawTheme: rawThemeStore,
        theme: themeStore,
        setTheme,
        destroy: unsubTheme
    }

    setContext<ThemeContext>(CTX_KEY, ctx)

    return ctx

    function setTheme(theme: RawTheme) {
        rawThemeStore.set(theme)

        getWindow()?.localStorage.setItem(STORAGE_KEY, theme)
    }
}

export function getThemeContext() {
    return getContext<ThemeContext>(CTX_KEY)
}

function getMediaTheme(): Theme | null {
    const prefersDark = getWindow()?.matchMedia?.(
        '(prefers-color-scheme: dark)'
    ).matches
    if (prefersDark === undefined) {
        return null
    }

    return prefersDark ? 'dark' : 'light'
}
