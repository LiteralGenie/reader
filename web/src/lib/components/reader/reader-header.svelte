<script lang="ts">
    import ArrowLongLeft from '$lib/icons/arrow-long-left.svelte'
    import Cog_6 from '$lib/icons/cog-6.svelte'
    import { euc } from '$lib/miscUtils'
    import { createEventDispatcher } from 'svelte'
    import ThemeToggle from '../theme-toggle.svelte'
    import Button from '../ui/button/button.svelte'

    export let seriesId: string

    $: href = `/series/${euc(seriesId)}`

    const dispatch = createEventDispatcher()
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
        <ThemeToggle
            variant="ghost"
            class="size-10 p-0 rounded-full mx-1 my-2"
        />

        <Button
            on:click={() => dispatch('settings')}
            variant="ghost"
            class="size-10 p-0 rounded-full mx-1 my-2"
        >
            <Cog_6 class="size-6" />
        </Button>
    </div>
</div>
