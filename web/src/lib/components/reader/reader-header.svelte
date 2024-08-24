<script lang="ts">
    import ArrowLongLeft from '$lib/icons/arrow-long-left.svelte'
    import Cog_6 from '$lib/icons/cog-6.svelte'
    import ThemeToggle from '../theme-toggle.svelte'
    import Button from '../ui/button/button.svelte'

    export let seriesId: string

    $: href = `/series/${seriesId}`
</script>

<div class="w-full h-16 flex justify-between items-center">
    <Button
        variant="link"
        {href}
        class="py-0 px-4 h-full hover:no-underline"
    >
        <div
            class="flex gap-2 items-center hover:border-b border-primary"
        >
            <ArrowLongLeft class="w-6 stroke-2 stroke-foreground" />

            <span class="text-foreground text-lg">
                {seriesId}
            </span>
        </div>
    </Button>

    <div class="pr-2 flex">
        <ThemeToggle variant="ghost" class="size-12 p-0" />

        <Button variant="ghost" class="size-12 p-0">
            <Cog_6 class="size-6" />
        </Button>
    </div>
</div>
