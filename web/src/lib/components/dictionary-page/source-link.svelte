<script lang="ts">
    export let source: string

    $: label = getLabel(source)
    $: hrefs = getHrefs(source)

    // @todo: move source to backend
    function getLabel(source: string): string {
        switch (source) {
            case 'wiktionary':
                return '- Wiktionary'
            case 'krdict':
                return "- the Korean-English Learners' Dictionary"
            case 'Helsinki-NLP/open_subtitles':
                return '- OpenSubtitles.org'
            case 'msarmi9_ted-talks':
                return '- TED Talks'
            default:
                return `- ${source}`
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
    <a href={hrefs[0]} target="_blank" class="hover:underline">
        {label}
    </a>
{:else if hrefs.length > 1}
    <span>
        <span>{label}</span>
        {#each hrefs as href, idx}
            <a {href} target="_blank" class="hover:underline">
                [{idx}]
            </a>
        {/each}
    </span>
{:else if hrefs.length === 0}
    <span>{label}</span>
{/if}
