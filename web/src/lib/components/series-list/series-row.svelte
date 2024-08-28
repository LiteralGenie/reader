<script lang="ts">
    import type { SeriesDto } from '$lib/api/dtos'

    export let series: SeriesDto
</script>

<img
    src="/api/cover/{series.filename}/{series.cover}"
    class="object-cover w-full h-full"
/>

<a
    href="/series/{series.filename}"
    class="ripple pl-4 h-full w-full rounded-r-md flex justify-between items-center"
>
    <span class="flex items-center h-full">
        {series.filename}
    </span>

    <div
        class="w-24 flex flex-col text-sm text-muted-foreground leading-tight text-end pr-4"
    >
        <span>1 chapters</span>
        <span>100 pages</span>
    </div>
</a>

<style lang="postcss">
    .ripple:hover {
        background-color: color-mix(
            in srgb,
            hsl(var(--background)),
            hsl(var(--foreground)) 10%
        );

        transition: background-color 0.2s;
    }
</style>
