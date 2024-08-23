<script lang="ts">
    import { goto } from '$app/navigation'
    import EllipsisButton from './ellipsis-button.svelte'
    import NextButton from './next-button.svelte'
    import PageButton from './page-button.svelte'
    import PreviousButton from './previous-button.svelte'

    export let currentPage: number
    export let maxPage: number
    export let hrefBuilder: (pageIdx: number) => string

    function onPageChange(ev: CustomEvent<number>) {
        const href = hrefBuilder(ev.detail)
        goto(href)
    }
</script>

<div class="flex flex-wrap gap-1 justify-center">
    <PreviousButton
        href={hrefBuilder(currentPage - 1)}
        disabled={currentPage === 1}
    />

    {#if currentPage > 1}
        <PageButton label={String(1)} href={hrefBuilder(1)} />
    {/if}

    {#if currentPage - 3 > 1}
        <EllipsisButton
            {maxPage}
            on:pagechange={(ev) => onPageChange(ev)}
        />
    {/if}

    {#if currentPage - 2 > 1}
        <PageButton
            label={String(currentPage - 2)}
            href={hrefBuilder(currentPage - 2)}
        />
    {/if}
    {#if currentPage - 1 > 1}
        <PageButton
            label={String(currentPage - 1)}
            href={hrefBuilder(currentPage - 1)}
        />
    {/if}

    <PageButton
        label={String(currentPage)}
        href={hrefBuilder(currentPage)}
        disabled
    />

    {#if currentPage + 1 < maxPage}
        <PageButton
            label={String(currentPage + 1)}
            href={hrefBuilder(currentPage + 1)}
        />
    {/if}
    {#if currentPage + 2 < maxPage}
        <PageButton
            label={String(currentPage + 2)}
            href={hrefBuilder(currentPage + 2)}
        />
    {/if}

    {#if currentPage + 3 < maxPage}
        <EllipsisButton
            {maxPage}
            on:pagechange={(ev) => onPageChange(ev)}
        />
    {/if}

    {#if currentPage < maxPage}
        <PageButton
            label={String(maxPage)}
            href={hrefBuilder(maxPage)}
        />
    {/if}

    <NextButton
        href={hrefBuilder(currentPage + 1)}
        disabled={currentPage === maxPage}
    />
</div>
