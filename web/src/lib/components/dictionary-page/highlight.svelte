<script lang="ts">
    export let text: string
    export let target: string

    $: parts = text.split(target)
</script>

<span>
    {#each parts as pt, idx}
        {pt}
        {#if idx !== parts.length - 1}
            <b class="text-red-700">{target}</b>
        {/if}
    {/each}
</span>
