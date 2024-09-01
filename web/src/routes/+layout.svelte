<script>
    import { createThemeContext } from '$lib/contexts/themeContext'
    import '$lib/css/ripple.css'
    import { onDestroy } from 'svelte'
    import '../app.css'

    const { destroy } = createThemeContext()

    onDestroy(() => destroy())
</script>

<slot />
