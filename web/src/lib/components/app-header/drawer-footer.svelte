<script lang="ts">
    import { getThemeContext } from '$lib/contexts/themeContext'
    import Discord from '$lib/icons/discord.svelte'
    import Github from '$lib/icons/github.svelte'
    import Button from '../ui/button/button.svelte'

    const { theme } = getThemeContext()
</script>

<div class="flex justify-center items-center py-3 border-t gap-2">
    <Button variant="ghost" class="rounded-full p-0 size-11">
        <a
            target="_blank"
            href="https://github.com/LiteralGenie/reader"
        >
            <Github variant={$theme} class="size-6" />
        </a>
    </Button>

    <Button variant="ghost" class="rounded-full p-0 size-11">
        <a target="_blank" href="https://discord.gg/RddchCRPwr">
            <Discord variant={$theme} class="size-7" />
        </a>
    </Button>
</div>
