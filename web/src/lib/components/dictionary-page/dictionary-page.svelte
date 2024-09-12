<script lang="ts">
    import { goto } from '$app/navigation'
    import type {
        DefinitionDto,
        ExampleDto,
        PartialDefinition
    } from '$lib/api/dtos'
    import ArrowRight from '$lib/icons/arrow-right.svelte'
    import { euc } from '$lib/miscUtils'
    import { draw } from 'radash'
    import Button from '../ui/button/button.svelte'
    import Input from '../ui/input/input.svelte'
    import Definitions from './definitions-preview.svelte'
    import ExamplesPreview from './examples-preview.svelte'
    import ExternalSearchButton from './external-search-button.svelte'
    import PartialDefinitionsPreview from './partial-definitions-preview.svelte'

    export let query: string
    export let definitions: DefinitionDto[]
    export let definitionCount: Promise<number>
    export let partialDefinitions: Record<string, PartialDefinition>
    export let examples: ExampleDto[]
    export let exampleCount: Promise<number>

    const placeholders = [
        'ㄹ 수 있다',
        '면 되다',
        '지 못하다',
        'ㄹ 걸',
        'ㄴ다니',
        //
        '안녕하세요',
        '15세 이상 감상을 권장합니다',
        '방과 후 전쟁활동',
        '모기전쟁',
        '잔불의 기사',
        '네가 있는 마을',
        '거꾸로 핀 꽃'
    ]

    let formEl: HTMLFormElement

    function onSubmit() {
        const formData = new FormData(formEl)

        let newQuery = formData.get('search') as string | null
        newQuery = (newQuery ?? '').trim()
        if (newQuery) {
            goto(`/dictionary?query=${newQuery}`)
        }
    }
</script>

<div class="flex flex-col">
    <form
        on:submit|preventDefault={onSubmit}
        bind:this={formEl}
        class="flex items-center px-6 pt-8"
    >
        <Input
            name="search"
            class="h-12 text-xl border-primary bg-muted rounded-r-none rounded-l-xl"
            placeholder={query || draw(placeholders)}
            value={query}
        />

        <Button
            type="submit"
            class="h-12 w-16 p-0 rounded-l-none rounded-r-xl"
        >
            <ArrowRight
                class="p-3.5 stroke-[2px] stroke-primary-foreground"
            />
        </Button>
    </form>

    {#if query.trim().length}
        <div class="pt-3 pb-4 px-6 flex gap-2 flex-wrap">
            <ExternalSearchButton
                label="Naver"
                href="https://en.dict.naver.com/#/search?query={euc(
                    query
                )}"
            />

            <ExternalSearchButton
                label="Wiktionary"
                href="https://en.wiktionary.org/w/index.php?search={euc(
                    query
                )}"
            />

            <ExternalSearchButton
                label="krdict"
                href="https://krdict.korean.go.kr/eng/dicMarinerSearch/search?nation=eng&nationCode=6&ParaWordNo=&mainSearchWord={euc(
                    query
                )}"
            />

            <ExternalSearchButton
                label="Google"
                href="https://www.google.com/search?q={euc(
                    query + ' 뜻'
                )}"
            />
        </div>
    {:else}
        <div class="pt-4"></div>
    {/if}

    <div class="flex flex-col gap-8 px-4 pt-8 pb-16">
        <Definitions {query} {definitions} count={definitionCount} />

        <ExamplesPreview {query} {examples} count={exampleCount} />

        <PartialDefinitionsPreview {query} {partialDefinitions} />
    </div>
</div>
