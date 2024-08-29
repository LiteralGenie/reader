<script lang="ts">
    import Input from '$lib/components/ui/input/input.svelte'
    import Label from '$lib/components/ui/label/label.svelte'
    import * as RadioGroup from '$lib/components/ui/radio-group'
    import Textarea from '$lib/components/ui/textarea/textarea.svelte'

    export let isSubmitting: boolean

    let mode: 'file-mode' | 'url-mode' = 'url-mode'
</script>

<div class={$$restProps.class ?? ''}>
    <div class="flex gap-4 items-center pb-2">
        <Label>Import from:</Label>

        <RadioGroup.Root
            disabled={isSubmitting}
            class="flex gap-4"
            bind:value={mode}
        >
            <button
                type="button"
                class="flex items-center gap-1"
                on:click|preventDefault={() => (mode = 'file-mode')}
                disabled={isSubmitting}
            >
                <RadioGroup.Item value="file-mode" name="file-mode" />
                <Label for="file-mode" class="cursor-[unset]">
                    File
                </Label>
            </button>

            <button
                type="button"
                class="flex items-center gap-1.5"
                on:click|preventDefault={() => (mode = 'url-mode')}
                disabled={isSubmitting}
            >
                <RadioGroup.Item value="url-mode" name="url-mode" />
                <Label for="url-mode" class="cursor-[unset]">
                    URL
                </Label>
            </button>
        </RadioGroup.Root>
    </div>

    {#if mode === 'file-mode'}
        <div class="text-sm flex flex-col gap-2 pt-1">
            <input
                type="file"
                accept="image/*"
                multiple
                name="files"
                disabled={isSubmitting}
                required
            />

            <p class="text-muted-foreground italic text-xs">
                Pages will be ordered by file name.
            </p>
        </div>
    {:else}
        <div class="flex flex-col gap-1.5">
            <Textarea
                name="urls"
                placeholder="https://abc.xyz/read/ch01
https://abc.xyz/ch09/001.png
https://abc.xyz/ch09/002.png"
                disabled={isSubmitting}
                class="whitespace-pre"
            />

            <p class="text-muted-foreground italic text-xs">
                URLs may point to a single image or multiple images.
                Enter one URL per line.
            </p>
        </div>

        <div class="flex pt-4 gap-4">
            <div>
                <Label for="min-width">Min. Width</Label>
                <Input
                    type="number"
                    name="min-width"
                    placeholder="300"
                />
            </div>
            <div>
                <Label for="min-height">Min. Height</Label>
                <Input
                    type="number"
                    name="min-height"
                    placeholder="300"
                />
            </div>
        </div>

        <div class="flex flex-col gap-1.5 pt-6">
            <Label for="url-regex">URL Regex</Label>
            <Input
                type="text"
                name="url-regex"
                placeholder="http://.*whatever.*png"
            />
            <p class="text-muted-foreground italic text-xs">
                For URLs that link to multiple images, each image URL
                must match this pattern if provided.
            </p>
        </div>

        <hr class="py-2 border-0" />
    {/if}
</div>
