<script lang="ts">
    import { createEventDispatcher } from 'svelte'

    export let maxPage: number

    let inputEl: HTMLInputElement

    const dispatch = createEventDispatcher()

    function onSubmit() {
        const val = parseInt(inputEl.value)
        if (val > 0 && val <= maxPage) {
            dispatch('pagechange', val)
        }
        inputEl.value = ''
    }
</script>

<form on:submit|preventDefault={onSubmit}>
    <input
        bind:this={inputEl}
        max={maxPage}
        placeholder="..."
        class="rounded-md h-10 py-2 w-10 font-medium flex items-center justify-center text-center"
        on:blur={onSubmit}
    />
</form>
