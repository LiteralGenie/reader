<script context="module" lang="ts">
    interface MetadataEvent {
        type: 'metadata'
        value: {
            urls: string[]
            chapter: string
            series: string
        }
    }

    interface PositionEvent {
        type: 'position'
        value: number
    }

    interface ProgressEvent {
        type: 'progress'
        value: {
            total: number
            done: string[]
            ignored: string[]
            phase: 'scanning' | 'downloading'
        }
    }

    type SseEvent = MetadataEvent | PositionEvent | ProgressEvent
</script>

<script lang="ts">
    import { page } from '$app/stores'
    import Loader from '$lib/components/loader.svelte'
    import Textarea from '$lib/components/ui/textarea/textarea.svelte'
    import { euc } from '$lib/miscUtils'

    import Button from '$lib/components/ui/button/button.svelte'
    import { createEventDispatcher, onMount } from 'svelte'
    import { writable } from 'svelte/store'

    export let jobId: string
    export let done = false

    const dispatch = createEventDispatcher()

    $: job = writable<MetadataEvent['value'] | null>(null)
    $: position = writable<number | null>(null)
    $: progress = writable<ProgressEvent['value'] | null>(null)
    $: href =
        new URL($page.url).origin +
        `/series/${$job?.series}/${$job?.chapter}`

    onMount(() => {
        const url = new URL($page.url.href)
        url.pathname = `/api/import_chapter/${euc(jobId)}`

        const evtSource = new EventSource(url)
        evtSource.onmessage = (ev) => {
            if (ev.data === 'close') {
                evtSource.close()
                done = true
                dispatch('done')
                return
            }

            const event = JSON.parse(ev.data) as SseEvent
            if (event.type === 'metadata') {
                job.set(event.value)
            } else if (event.type === 'position') {
                position.set(event.value)
            } else {
                progress.set(event.value)
            }
        }
    })
</script>

<div class="h-[90vh] flex flex-col">
    {#if !done}
        <div
            class="flex items-center bg-primary text-primary-foreground rounded-t-md p-6"
        >
            <Loader
                class="size-4 mr-2 stroke-primary-foreground fill-primary-foreground"
            />
            {#if $progress?.phase === 'downloading'}
                <p class="font-semibold">
                    Downloading images ({$progress.done.length +
                        $progress.ignored.length} / {$progress.total})...
                </p>
            {:else if $progress?.phase === 'scanning'}
                <p class="font-semibold">Scanning URLs...</p>
            {:else if $position !== null}
                <p class="font-semibold">
                    Waiting on {$position} other uploads...
                </p>
            {:else}
                <p class="font-semibold">
                    Checking queue position...
                </p>
            {/if}
        </div>
    {:else}
        <div class="pt-2"></div>
    {/if}

    <div class="p-4 pl-6 pr-16">
        <span class="font-bold pr-2">Chapter URL: </span>
        <a
            {href}
            target="_blank"
            class="link-color underline text-primary break-all"
        >
            {href}
        </a>
    </div>

    <hr class="mx-4" />

    <div class="flex-grow h-full flex flex-col gap-4 px-8 pt-4 pb-8">
        <div class="flex flex-col gap-1">
            <h2 class="font-semibold">
                Input URLs ({$job?.urls.length ?? 0})
            </h2>
            <Textarea
                readonly
                value={$job?.urls ?? ''}
                class="flex-grow bg-muted text-muted-foreground whitespace-pre"
            />
        </div>

        <div class="flex-grow flex flex-col gap-1">
            <h2 class="font-semibold">
                Images found ({$progress?.done.length ?? 0})
            </h2>
            <Textarea
                readonly
                value={($progress?.done ?? []).join('\n')}
                class="flex-grow bg-muted text-muted-foreground whitespace-pre"
            />
        </div>

        <div class="flex-grow flex flex-col gap-1">
            <h2 class="font-semibold">
                Images ignored ({$progress?.ignored.length ?? 0})
            </h2>
            <Textarea
                readonly
                value={($progress?.ignored ?? [])
                    .reverse()
                    .join('\n')}
                class="flex-grow bg-muted text-muted-foreground whitespace-pre"
            />
        </div>
    </div>

    {#if done}
        <hr class="mx-4" />

        <div class="flex justify-end px-6 py-6">
            <Button on:click={() => dispatch('reset')}>
                Add New Chapter
            </Button>
        </div>
    {/if}
</div>

<style lang="postcss">
    .link-color {
        color: color-mix(
            in srgb,
            hsl(var(--primary)),
            hsl(var(--foreground)) 50%
        );
    }
</style>
