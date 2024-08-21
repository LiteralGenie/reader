import { max, min, sort, sum } from 'radash'
import type { OcrMatch } from './api/ocr'
import { abs } from './misc_utils'

type Bbox = [number, number, number, number]

export class StitchedLine {
    constructor(public matches: OcrMatch[]) {}

    get value() {
        return this.matches.map((m) => m.value).join(' ')
    }

    get confidence() {
        return (
            sum(this.matches.map((m) => m.confidence)) /
            this.matches.length
        )
    }

    get bbox(): Bbox {
        const y1 = min(this.matches.map((m) => m.bbox[0]))!
        const x1 = min(this.matches.map((m) => m.bbox[1]))!
        const y2 = max(this.matches.map((m) => m.bbox[2]))!
        const x2 = max(this.matches.map((m) => m.bbox[3]))!
        return [y1, x2, y2, x1]
    }

    get width() {
        return this.bbox[3] - this.bbox[1]
    }

    get height() {
        return this.bbox[3] - this.bbox[1]
    }

    get center() {
        const cx = this.bbox[1] + this.width / 2
        const cy = this.bbox[0] + this.height / 2
        return [cx, cy]
    }
}

export class StitchedBlock {
    constructor(public lines: StitchedLine[]) {}

    get value() {
        return this.lines.map((ln) => ln.value).join(' ')
    }

    get confidence() {
        return (
            sum(this.lines.map((m) => m.confidence)) /
            this.lines.length
        )
    }

    get bbox(): Bbox {
        const y1 = min(this.lines.map((m) => m.bbox[0]))!
        const x1 = min(this.lines.map((m) => m.bbox[1]))!
        const y2 = max(this.lines.map((m) => m.bbox[2]))!
        const x2 = max(this.lines.map((m) => m.bbox[3]))!
        return [y1, x2, y2, x1]
    }
}

export function stitchLines(
    matches: OcrMatch[],
    maxEdgeDx = 0.5,
    maxCenterDy = 0.25
): StitchedLine[] {
    /**
     * Group words into lines
     *
     * The maximum edge-to-edge x-distance is (line_height * max_edge_dx)
     * The maximum center-to-center y-distance is (line_height * max_center_dy)
     **/

    const lines: OcrMatch[][] = []

    let rem = [...matches]
    while (rem.length > 0) {
        // Pick arbitrary starting point
        const base = rem.pop()!
        let ln = [base]

        while (true) {
            const y1 = min(ln.map((m) => m.bbox[0]))!
            const x1 = min(ln.map((m) => m.bbox[1]))!
            const y2 = max(ln.map((m) => m.bbox[2]))!
            const x2 = max(ln.map((m) => m.bbox[3]))!
            const bbox: Bbox = [y1, x1, y2, x2]

            const toAdd: number[] = []
            for (let idx = 0; idx < rem.length; idx++) {
                const m = rem[idx]

                const dy = abs(getCenter(base)[1] - getCenter(m)[1])
                if (dy > getHeight(base) * maxCenterDy) {
                    continue
                }

                const dx = edgeToEdgeDist(bbox, m.bbox, 'x')
                if (dx > getHeight(base) * maxEdgeDx) {
                    continue
                }

                toAdd.push(idx)
            }

            if (toAdd.length === 0) {
                break
            }

            for (let idx of toAdd) {
                ln.push(rem[idx])
            }

            rem = rem.filter((m) => !ln.find((x) => x === m))
        }

        ln = sort(ln, ({ bbox: [y1, x1, y2, x2] }) => x1)
        lines.push(ln)
    }

    const stitchedLines = lines.map((ln) => new StitchedLine(ln))
    return stitchedLines
}

export function stitchBlocks(
    lines: StitchedLine[],
    maxEdgeDx = 0.5,
    maxEdgeDy = 0.5
): StitchedBlock[] {
    /**
     * Group words into lines
     *
     * The maximum edge-to-edge x-distance is (line_height * max_edge_dx)
     * The maximum edge-to-edge y-distance is (line_height * max_edge_dy)
     **/

    const blocks: StitchedLine[][] = []

    let rem = [...lines]
    while (rem.length > 0) {
        // Pick arbitrary starting point
        const base = rem.pop()!
        let blk = [base]

        while (true) {
            const y1 = min(blk.map((ln) => ln.bbox[0]))!
            const x1 = min(blk.map((ln) => ln.bbox[1]))!
            const y2 = max(blk.map((ln) => ln.bbox[2]))!
            const x2 = max(blk.map((ln) => ln.bbox[3]))!
            const bbox: Bbox = [y1, x1, y2, x2]

            const toAdd: number[] = []
            for (let idx = 0; idx < rem.length; idx++) {
                const ln = rem[idx]

                const dy = edgeToEdgeDist(bbox, ln.bbox, 'y')
                if (dy > base.height * maxEdgeDy) {
                    continue
                }

                const dx = edgeToEdgeDist(bbox, ln.bbox, 'x')
                if (dx > base.height * maxEdgeDx) {
                    continue
                }

                toAdd.push(idx)
            }

            if (toAdd.length === 0) {
                break
            }

            for (let idx of toAdd) {
                blk.push(rem[idx])
            }

            rem = rem.filter((ln) => !blk.find((x) => x === ln))
        }

        blk = sort(blk, ({ bbox: [y1, x1, y2, x2] }) => y1)
        blocks.push(blk)
    }

    const stitchedBlocks = blocks.map((ln) => new StitchedBlock(ln))
    return stitchedBlocks
}

function edgeToEdgeDist(a: Bbox, b: Bbox, axis: 'x' | 'y'): number {
    let av1, av2, bv1, bv2
    if (axis === 'x') {
        ;[av1, av2] = [a[1], a[3]]
        ;[bv1, bv2] = [b[1], b[3]]
    } else {
        ;[av1, av2] = [a[0], a[2]]
        ;[bv1, bv2] = [b[0], b[2]]
    }

    const hasOverlap =
        anyBetween(av1, av2, [bv1, bv2]) ||
        anyBetween(bv1, bv2, [av1, av2])
    if (hasOverlap) {
        return 0
    }

    const dist = min([abs(av1 - bv2), abs(bv1 - av2)])
    return dist
}

function getWidth(match: OcrMatch) {
    return match.bbox[3] - match.bbox[1]
}

function getHeight(match: OcrMatch) {
    return match.bbox[2] - match.bbox[0]
}

function getCenter(match: OcrMatch) {
    const w = getWidth(match)
    const cx = match.bbox[1] + w / 2

    const h = getHeight(match)
    const cy = match.bbox[0] + h / 2

    return [cx, cy]
}

function between(start: number, end: number, x: number) {
    return x >= start && x <= end
}

function anyBetween(start: number, end: number, xs: number[]) {
    return xs.some((x) => between(start, end, x))
}
