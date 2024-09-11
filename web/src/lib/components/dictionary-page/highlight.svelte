<script lang="ts">
    import { hangul } from '$lib/jamo'

    export let text: string
    export let target: string

    $: [head, highlighted, tail] = getParts(text, target)

    function getParts(
        text: string,
        target: string
    ): [string, string, string] {
        const defaultReturn = [text, '', ''] as [
            string,
            string,
            string
        ]

        // Get jamo-based indices of target
        const chars = text.split('')
        const jamoByChar = chars.map(
            (syl) => (hangul.decompose(syl) ?? [syl]) as string[]
        )
        const allJamo = jamoByChar
            .map((letters) => letters.join(''))
            .join('')

        const targetJamo = target
            .split('')
            .map(
                (syl) => (hangul.decompose(syl) ?? [syl]) as string[]
            )
            .map((letters) => letters.join(''))
            .join('')
        const jamoStart = allJamo.indexOf(targetJamo)
        if (jamoStart === -1) {
            return defaultReturn
        }
        let jamoEnd = jamoStart + targetJamo.length

        // Convert jamo-based indices to char-based indices
        let charStart = -1

        let jamoIdx = 0
        let charIdx = 0
        while (true) {
            const charJamo = jamoByChar[charIdx]
            if (charJamo === undefined) {
                break
            }

            const nextJamoIdx = jamoIdx + charJamo.length
            if (nextJamoIdx > jamoStart) {
                charStart = charIdx

                jamoIdx = nextJamoIdx
                charIdx += 1
                break
            }

            jamoIdx = nextJamoIdx
            charIdx += 1
        }

        if (charStart === -1) {
            console.error(
                'Couldnt map start jamo to start char',
                target,
                text
            )
            return defaultReturn
        }

        let charEnd = -1
        while (true) {
            // Assume entire tail of string matches if we run out of characters
            const charJamo = jamoByChar[charIdx]
            if (charJamo === undefined) {
                charEnd = jamoByChar.length - 1
                break
            }

            const nextJamoIdx = jamoIdx + charJamo.length
            if (nextJamoIdx > jamoEnd) {
                charEnd = charIdx
                break
            }

            jamoIdx = nextJamoIdx
            charIdx += 1

            // Ignore whitespace
            if (charJamo[0].trim() === '') {
                jamoEnd += 1
            }
        }

        const head = text.slice(0, charStart)
        const highlight = text.slice(charStart, charEnd)
        const tail = text.slice(charEnd)
        return [head, highlight, tail]
    }
</script>

<span>
    {head}<b class="text-red-700">{highlighted}</b>{tail}
</span>
