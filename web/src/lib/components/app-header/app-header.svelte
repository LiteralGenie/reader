<script lang="ts">
    import Bars_3 from '$lib/icons/bars-3.svelte'
    import BookOpen from '$lib/icons/book-open.svelte'
    import Book from '$lib/icons/book.svelte'
    import { onMount } from 'svelte'
    import ThemeToggle from '../theme-toggle.svelte'
    import Button from '../ui/button/button.svelte'
    import DrawerFooter from './drawer-footer.svelte'
    import DrawerLink from './drawer-link.svelte'
    import HeaderDrawer from './header-drawer.svelte'

    export let isMounted = false

    onMount(() => (isMounted = true))
</script>

<div
    class="root w-full flex justify-between items-center pl-4 pr-2 py-1"
>
    <HeaderDrawer>
        <!-- 
            @todo: trigger is positioned too far right before javascript loads, 
            hence this isMounted check
        -->
        <svelte:fragment slot="trigger">
            {#if isMounted}
                <Button
                    variant="ghost"
                    class="size-10 p-0 rounded-full"
                >
                    <Bars_3 class="size-6 stroke-2" />
                </Button>
            {/if}
        </svelte:fragment>

        <div class="flex flex-col justify-between h-full">
            <nav>
                <DrawerLink href="/series" label="All Series">
                    <BookOpen
                        class="size-5 stroke-[2px]"
                        slot="icon"
                    />
                </DrawerLink>

                <DrawerLink href="/dictionary" label="Dictionary">
                    <Book class="size-5" slot="icon" />
                </DrawerLink>
            </nav>

            <DrawerFooter />
        </div>
    </HeaderDrawer>

    <div class="flex">
        <ThemeToggle
            variant="ghost"
            class="size-10 p-0 rounded-full"
        />
    </div>
</div>

<style lang="postcss">
    .root {
        background-color: var(--header);
    }

    nav {
        @apply rounded-md pt-4;

        display: grid;
        grid-template-columns: 1fr;
        grid-auto-rows: 3.5em;
        justify-items: start;
    }
</style>
