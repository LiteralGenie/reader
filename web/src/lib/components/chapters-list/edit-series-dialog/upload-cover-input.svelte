<script lang="ts">
    import type { SeriesDto } from '$lib/api/dtos'
    import Button from '$lib/components/ui/button/button.svelte'
    import Label from '$lib/components/ui/label/label.svelte'
    import type { FormControl } from '$lib/form/types'
    import ArrowUpTray from '$lib/icons/arrow-up-tray.svelte'
    import PencilSquare from '$lib/icons/pencil-square.svelte'

    export let series: SeriesDto
    export let control: FormControl<File | null | string>
    export let disabled: boolean

    let inputEl: HTMLInputElement
    let showImageOverlay = false

    let previewEl: HTMLImageElement
    $: ({ value } = control)
    $: {
        if ($value instanceof File && previewEl) {
            previewEl.src = URL.createObjectURL($value)
            showImageOverlay = false
        }
    }

    let downloadEl: HTMLAnchorElement

    function onUpload() {
        control.setValue(inputEl.files?.[0] ?? null)
    }

    function onDownload() {
        if (!$value) {
            return
        }

        if ($value instanceof File) {
            downloadEl.href = URL.createObjectURL($value)
            downloadEl.download = $value.name
        } else {
            downloadEl.href = `/api/cover/${series.filename}/${$value}`

            let filename =
                $value.split('/').slice(-1)[0] ?? 'cover.png'
            filename = filename.split('?')[0]
            downloadEl.download = filename
        }

        downloadEl.click()
    }
</script>

<div class="flex flex-col gap-1.5">
    <Label for="cover">Cover Image</Label>

    <div class="flex flex-col gap-2">
        <div class="relative">
            <button
                on:click={() => inputEl.click()}
                on:mouseenter={() => (showImageOverlay = true)}
                on:mouseleave={() => (showImageOverlay = false)}
                class:pointer-events-none={disabled}
                class="w-full flex justify-center"
                type="button"
            >
                {#if $value instanceof File}
                    <img
                        class="cover object-scale-down min-w-0 max-h-[40em] bg-[#050505] w-full"
                        bind:this={previewEl}
                    />
                {:else if typeof $value === 'string'}
                    <img
                        src="/api/cover/{series.filename}/{$value}"
                        class="cover object-scale-down min-w-0 max-h-[40em] bg-[#050505] w-full"
                    />
                {:else}
                    <div
                        class="placeholder h-[20em] w-full bg-[#303030] flex flex-col gap-2 items-center justify-center text-sm"
                    >
                        <ArrowUpTray class="size-12 stroke-2" />
                        <span class="font-bold">Tap to Upload</span>
                    </div>
                {/if}
            </button>

            <input
                on:change={onUpload}
                bind:this={inputEl}
                type="file"
                accept="image/*"
                hidden
                {disabled}
            />

            <div
                class="overlay absolute top-0 bottom-0 left-0 right-0 p-0 flex items-center justify-center pointer-events-none"
                class:invisible={!showImageOverlay}
            >
                {#if $value}
                    <PencilSquare class="size-16 stroke-white" />
                {/if}
            </div>
        </div>

        <div class="flex gap-2 justify-center">
            <Button
                on:click={() => control.setValue(null)}
                class="px-6 w-full flex gap-2 items-center"
                variant="secondary"
                {disabled}
            >
                Clear
            </Button>
            <Button
                on:click={onDownload}
                class="px-6 w-full"
                variant="secondary"
                disabled={$value === null}
            >
                Download
            </Button>
        </div>
    </div>
</div>

<a bind:this={downloadEl} class="hidden"></a>

<style lang="postcss">
    .overlay {
        background-color: rgba(0, 0, 0, 70%);
    }

    .placeholder {
        color: color-mix(
            in srgb,
            hsl(var(--muted-foreground)),
            hsl(var(--primary-foreground)) 70%
        );
    }
</style>
