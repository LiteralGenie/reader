<script lang="ts">
    export let source: string

    $: label = getLabel(source)
    $: hrefs = getHrefs(source)

    // @todo: move source to backend
    function getLabel(source: string): string {
        switch (source) {
            case 'wiktionary':
                return 'from Wiktionary'
            case 'krdict':
                return "from the Korean-English Learners' Dictionary"
            case 'Helsinki-NLP/open_subtitles':
                return 'from OpenSubtitles.org'
            case 'msarmi9_ted-talks':
                return 'from TED Talks'
            default:
                return `from ${source}`
        }
    }

    function getHrefs(source: string): string[] {
        switch (source) {
            case 'wiktionary':
                return [
                    'https://www.wiktionary.org/',
                    'https://kaikki.org/dictionary/Korean/index.html'
                ]
            case 'krdict':
                return ['https://krdict.korean.go.kr/eng/mainAction']
            case 'Helsinki-NLP/open_subtitles':
                return [
                    'http://www.opensubtitles.org/',
                    'https://huggingface.co/datasets/Helsinki-NLP/open_subtitles'
                ]
            case 'msarmi9_ted-talks':
                return [
                    'https://www.ted.com/talks',
                    'https://huggingface.co/datasets/msarmi9/korean-english-multitarget-ted-talks-task'
                ]
            default:
                return []
        }
    }
</script>

{#if hrefs.length === 1}
    <a class="hover:underline" href={hrefs[0]}>{label}</a>
{:else if hrefs.length > 1}
    <span>
        <span>{label}</span>
        {#each hrefs as href, idx}
            <a {href} class="hover:underline">[{idx}]</a>
            <span></span>
        {/each}
    </span>
{:else if hrefs.length === 0}
    <span>{label}</span>
{/if}
