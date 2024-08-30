<script lang="ts">
    import { page } from '$app/stores'

    export let href: string
    export let label: string

    $: realHref = new URL($page.url.origin + href)
    $: active = $page.url.pathname === realHref.pathname
    $: console.log($page.url.pathname, realHref.pathname)
</script>

<a
    {href}
    class:active
    class="flex items-center gap-2 w-full h-full px-6 py-6 hover:bg-muted"
>
    <slot name="icon" />
    <span> {label} </span>
</a>

<style lang="postcss">
    .active {
        @apply font-bold text-primary cursor-default;

        background-color: hsl(var(--muted) / 40%);
    }
</style>
