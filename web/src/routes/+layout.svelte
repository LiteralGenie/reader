<script>
    import { createThemeContext } from '$lib/contexts/themeContext'
    import '$lib/css/ripple.css'
    import '../app.css'

    createThemeContext()
</script>

<slot />
