<script>
    import { getThemeContext } from '$lib/contexts/themeContext'
    import Moon from '$lib/icons/moon.svelte'
    import Sun from '$lib/icons/sun.svelte'
    import Button from './ui/button/button.svelte'

    const { theme, setTheme } = getThemeContext()

    function onClick() {
        console.log('click', $theme)
        const nextTheme = $theme === 'light' ? 'dark' : 'light'
        setTheme(nextTheme)
    }
</script>

<Button on:click={onClick} {...$$props}>
    {#if $theme === 'dark'}
        <Sun class="size-6" />
    {:else}
        <Moon class="size-6" />
    {/if}
</Button>
