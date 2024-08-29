<script lang="ts">
    import { goto } from '$app/navigation'
    import type { SeriesWithChaptersDto } from '$lib/api/dtos'
    import BasicDialog from '$lib/components/basic-dialog.svelte'
    import {
        addSuffixUntilUnique,
        throwOnStatus
    } from '$lib/miscUtils'
    import { createEventDispatcher } from 'svelte'
    import AddChapterForm from './add-chapter-form.svelte'
    import AddChapterProgress from './add-chapter-progress.svelte'

    export let open: boolean
    export let seriesId: string

    const dispatch = createEventDispatcher()

    let isSubmitting: boolean = false
    let jobId: string | null = null
    $: disabled = isSubmitting

    async function onSubmit(ev: SubmitEvent) {
        isSubmitting = true

        try {
            const data = new FormData(ev.target as HTMLFormElement)
            console.log('Creating chapter with', [...data.entries()])

            const name = data.get('name') as string | null
            if (!name) {
                return
            }

            const series: SeriesWithChaptersDto = await (
                await fetch(`/api/series/${seriesId}`)
            ).json()
            const chapterId = addSuffixUntilUnique(
                series.chapters.map((ch) => ch.filename),
                name
            )

            const files = data.getAll('files') as File[]
            if (files.length) {
                const postData = new FormData()
                postData.set('series', seriesId)
                postData.set('chapter', chapterId)
                postData.set('chapterName', name)

                for (let f of files) {
                    postData.append('pages', f)
                }

                const resp = await fetch('/api/chapter', {
                    method: 'POST',
                    body: postData
                })
                throwOnStatus(resp)

                goto(`/series/${seriesId}/${chapterId}`)
            } else {
                const rawUrls = data.get('urls') as string | null
                if (!rawUrls?.trim()) {
                    throw Error('No URLS specified')
                }

                const urls = rawUrls
                    .split(/\s/)
                    .map((url) => url.trim())

                const minWidth = parseInt(
                    (data.get('min-width') || '300') as string
                )

                const minHeight = parseInt(
                    (data.get('min-height') || '300') as string
                )

                const patt = data.get('url-regex') ?? null

                const resp = await fetch('/api/import_chapter', {
                    method: 'POST',
                    body: JSON.stringify({
                        series: seriesId,
                        chapter: chapterId,
                        chapter_name: name,
                        urls: urls,
                        min_width: minWidth,
                        min_height: minHeight,
                        patt
                    }),
                    headers: {
                        'Content-Type': 'application/json'
                    }
                })
                throwOnStatus(resp)

                const { job_id } = await resp.json()
                jobId = job_id
            }
        } catch (e) {
            alert(String(e))
        } finally {
            isSubmitting = false
        }
    }

    function onReset() {
        jobId = null
    }
</script>

<BasicDialog
    {open}
    on:close
    preventClose={disabled}
    class="w-[90vw] max-w-[50em] h-max m-auto"
>
    {#if jobId}
        <AddChapterProgress {jobId} on:reset={onReset} on:done />
    {:else}
        <div class="px-6 pb-8">
            <div class="pt-5 pb-8 flex items-center">
                <h1 class="text-xl font-bold">Add Chapter</h1>
            </div>
            <AddChapterForm
                on:submit={onSubmit}
                on:close={() => (disabled ? '' : dispatch('close'))}
                {disabled}
            />
        </div>
    {/if}
</BasicDialog>
