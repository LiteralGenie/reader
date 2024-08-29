<script lang="ts">
    import Label from '$lib/components/ui/label/label.svelte'
    import * as RadioGroup from '$lib/components/ui/radio-group'
    import Textarea from '$lib/components/ui/textarea/textarea.svelte'

    export let isSubmitting: boolean

    let mode: 'file-mode' | 'url-mode' = 'file-mode'
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
                class="flex items-center gap-1"
                on:click|preventDefault={() => (mode = 'url-mode')}
                disabled={isSubmitting}
            >
                <RadioGroup.Item value="url-mode" name="url-mode" />
                <Label for="url-mode" class="cursor-[unset]"
                    >URL</Label
                >
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
        <div class="flex flex-col gap-2">
            <Textarea
                name="urls"
                placeholder="https://abc.xyz/read/ch01
https://abc.xyz/ch09/001.png
https://abc.xyz/ch09/002.png"
                disabled={isSubmitting}
            />

            <p class="text-muted-foreground italic text-xs">
                URLs may point to a single image or multiple images.
                Enter one URL per line.
            </p>
        </div>
    {/if}
</div>
