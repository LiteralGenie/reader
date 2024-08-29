<script context="module" lang="ts">
    interface Progress {
        total: number
        done: string[]
        ignored: string[]
        phase: 'scanning' | 'downloading'
    }
</script>

<script lang="ts">
    import { page } from '$app/stores'
    import Loader from '$lib/components/loader.svelte'
    import Textarea from '$lib/components/ui/textarea/textarea.svelte'
    import { euc } from '$lib/miscUtils'

    import Button from '$lib/components/ui/button/button.svelte'
    import { createEventDispatcher, onMount } from 'svelte'
    import { writable } from 'svelte/store'
    import type { AddChapterJob } from './add-chapter-dialog.svelte'

    export let job: AddChapterJob
    export let done = false

    const dispatch = createEventDispatcher()

    $: progress = writable<Progress | null>(null)
    $: href =
        new URL($page.url).origin +
        `/series/${job.seriesId}/${job.chapterId}`

    onMount(() => {
        const url = new URL(window.location.href)
        url.pathname = `/api/import_chapter/${euc(job.jobId)}`

        const evtSource = new EventSource(url)
        evtSource.onmessage = (ev) => {
            if (ev.data === 'close') {
                evtSource.close()
                done = true
                dispatch('done')
                return
            }

            const update: Progress = JSON.parse(ev.data)
            progress.set(update)
        }
    })
</script>

<div class="h-[90vh] flex flex-col">
    {#if !done}
        <div
            class="flex items-center bg-primary text-primary-foreground rounded-t-md p-6"
        >
            {#if !$progress || $progress?.phase === 'scanning'}
                <Loader
                    class="size-4 mr-1 stroke-primary-foreground fill-primary-foreground"
                />

                <p class="font-semibold">Scanning URLs...</p>
            {:else if $progress?.phase === 'downloading'}
                <Loader
                    class="size-4 mr-1 stroke-primary-foreground fill-primary-foreground"
                />

                <p class="font-semibold">
                    Downloading images ({$progress.done.length +
                        $progress.ignored.length} / {$progress.total})...
                </p>
            {/if}
        </div>
    {:else}
        <div class="pt-2"></div>
    {/if}

    <div class="p-4 px-6">
        <span class="font-bold pr-2">Chapter URL: </span>
        <a
            {href}
            target="_blank"
            class="link-color underline text-primary"
        >
            {href}
        </a>
    </div>

    <hr class="border-muted mx-4" />

    <div class="flex-grow h-full flex flex-col gap-4 px-8 pt-4 pb-8">
        <div class="flex flex-col gap-1">
            <h2 class="font-semibold">
                Input URLs ({$progress?.done.length ?? 0})
            </h2>
            <Textarea
                readonly
                value={job.urls}
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
        <hr class="border-muted mx-4" />

        <div class="flex justify-end px-6 py-4">
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
