<script context="module" lang="ts">
    interface Progress {
        total: number
        done: string[]
        ignored: string[]
        phase: 'scanning' | 'downloading'
    }
</script>

<script lang="ts">
    import Loader from '$lib/components/loader.svelte'
    import { euc } from '$lib/miscUtils'

    import { createEventDispatcher, onMount } from 'svelte'
    import { writable } from 'svelte/store'

    export let jobId: string

    const dispatch = createEventDispatcher()

    $: progress = writable<Progress | null>(null)

    onMount(() => {
        const url = new URL(window.location.href)
        url.pathname = `/api/import_chapter/${euc(jobId)}`

        const evtSource = new EventSource(url)
        evtSource.onmessage = (ev) => {
            if (ev.data === 'close') {
                evtSource.close()
                dispatch('done')
                return
            }

            const update: Progress = JSON.parse(ev.data)
            progress.set(update)
        }
    })
</script>

<div class="flex items-center font-semibold">
    {#if !$progress || $progress?.phase === 'scanning'}
        <p>Scanning URLs...</p>
    {:else if $progress?.phase === 'downloading'}
        <Loader
            class="size-4 mr-1 stroke-primary-foreground fill-primary-foreground"
        />

        <p>
            Downloading images ({$progress.done.length +
                $progress.ignored.length} / {$progress.total})...
        </p>
    {/if}
</div>
