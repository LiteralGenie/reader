<script lang="ts">
    import { goto } from '$app/navigation'
    import type { SeriesDto } from '$lib/api/dtos'
    import Button from '$lib/components/ui/button/button.svelte'
    import Input from '$lib/components/ui/input/input.svelte'
    import Label from '$lib/components/ui/label/label.svelte'
    import sanitize from 'sanitize-filename'
    import { createEventDispatcher } from 'svelte'

    const dispatch = createEventDispatcher()

    async function onSubmit(ev: SubmitEvent) {
        const data = new FormData(ev.target as HTMLFormElement)

        // Generate unique folder name
        const name = data.get('name')
        if (!name || typeof name !== 'string') {
            return
        }

        const series: SeriesDto[] = await (
            await fetch('/api/series')
        ).json()

        const baseFilename = sanitize(name)
        let nameIdx = 2

        let filename = baseFilename
        while (
            filename === null ||
            series.some((s) => s.filename === filename)
        ) {
            filename = `${baseFilename}_${nameIdx}`
            nameIdx += 1
        }

        // Send request
        const postData = new FormData()
        postData.set('filename', filename)
        postData.set('name', name)

        const cover = data.get('cover') as File
        if (cover.size > 0) {
            postData.set('cover', cover)
        }

        const resp = await fetch('/api/series', {
            method: 'POST',
            body: postData
        })

        // Show error if failed
        if (resp.status !== 200) {
            const detail = (await resp.json()).detail
            alert(detail)
            return
        }

        // Redirect on success
        goto(`/series/${filename}`)
        dispatch('close')
    }

    function onCancel() {
        dispatch('close')
    }
</script>

<form on:submit|preventDefault={onSubmit} class="flex flex-col gap-4">
    <h2 class="font-bold text-lg">Manual Import</h2>

    <div class="flex flex-col gap-2">
        <Label for="name">Series Name *</Label>
        <Input
            name="name"
            required
            accept="image/*"
            class="text-xs"
            placeholder="Knight Run"
        />
    </div>

    <div class="flex flex-col gap-1.5">
        <Label for="cover">Cover Image (optional)</Label>
        <input name="cover" type="file" class="text-sm" />
    </div>

    <div class="pt-2 flex flex-col gap-4">
        <Button on:click={onCancel} variant="secondary">Cancel</Button
        >
        <Button type="submit">Submit</Button>
    </div>
</form>
