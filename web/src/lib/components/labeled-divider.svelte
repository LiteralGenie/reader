<script lang="ts">
    export let label: string
</script>

<!-- Divider -->
<div class="flex w-full items-center {$$restProps.class ?? ''}">
    <hr class="flex-grow border-muted-foreground" />
    <span class="px-2 text-sm text-muted-foreground">
        {label}
    </span>
    <hr class="flex-grow border-muted-foreground" />
</div>
