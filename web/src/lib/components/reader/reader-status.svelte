<script lang="ts">
    import type { OcrPageDto } from '$lib/api/dtos'
    import { derived, type Readable } from 'svelte/store'
    import Loader from '../loader.svelte'

    export let data: Readable<Record<string, OcrPageDto | null>>

    $: status = derived(data, (d) => {
        const total = Object.values(d).length
        const done = Object.values(d).filter(
            (ms) => ms !== null
        ).length

        if (done >= total) {
            return ''
        }

        const status = `OCR'ing pages (${done + 1} / ${total})...`
        return status
    })
</script>

{#if $status}
    <div class="root w-full flex items-center p-2">
        <Loader
            class="size-3 mr-1 stroke-secondary-foreground fill-secondary-foreground"
        />

        <span class="text-sm text-secondary-foreground">
            {$status}
        </span>
    </div>
{/if}

<style lang="postcss">
    .root {
        background-color: color-mix(
            in srgb,
            hsl(var(--secondary)),
            #000 10%
        );
    }
</style>
