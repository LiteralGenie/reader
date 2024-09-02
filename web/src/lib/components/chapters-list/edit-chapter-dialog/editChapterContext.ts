import type { ChapterDto, PageDto } from '$lib/api/dtos'
import { createFormControlRecord } from '$lib/form/form-control'
import type {
    TemplateArray,
    TemplateRecord,
    TemplateScalar,
    TemplateToControlType
} from '$lib/form/types'
import { deepCopy, isFileEqual, throwOnStatus } from '$lib/miscUtils'
import { newPromiseStore, type PromiseStore } from '$lib/promiseStore'
import { counting, isEqual, zip } from 'radash'
import { getContext, setContext } from 'svelte'
import { derived, get, writable, type Readable } from 'svelte/store'

const CTX_KEY = 'edit-chapter'

export interface EditChapterForm {
    name: string
    existingPages: Array<{
        filename: string
        action:
            | { type: 'delete' }
            | { type: 'rename'; filename: string }
            | null
    }>
    newPages: Array<{
        id: string
        file: File
        newFilename: string | null
    }>
}

export interface EditChapterContext {
    form: Readable<EditChapterForm>
    formInitial: Readable<Readonly<EditChapterForm>>
    controls: EditChapterFormControls
    hasChanges: Readable<boolean>
    errors: Readable<EditChapterFormErrors>
    submit: () => Promise<any>
    destroy: () => void

    pages: PromiseStore<PageDto[], null>
}

export function createEditChapterContext(
    series: string,
    chapter: ChapterDto
) {
    const initial = {
        name: chapter.name,
        existingPages: [],
        newPages: []
    } satisfies EditChapterForm

    const form = writable<EditChapterForm>(deepCopy(initial))
    const formInitial = writable<EditChapterForm>(deepCopy(initial))
    const controls = createFormControlRecord(form, {
        _type: 'record',
        name: {
            _type: 'scalar'
        },
        existingPages: {
            _type: 'array',
            children: {
                _type: 'record',
                filename: {
                    _type: 'scalar'
                },
                action: {
                    _type: 'scalar'
                }
            }
        },
        newPages: {
            _type: 'array',
            children: {
                _type: 'record',
                id: { _type: 'scalar' },
                file: { _type: 'scalar' },
                newFilename: { _type: 'scalar' }
            }
        }
    } as EditChapterFormTemplate)

    const hasChanges = derived(
        [formInitial, form],
        ([before, after]) => !isFormEqual(before, after)
    )

    const pages = newPromiseStore(fetchPages(), null)
    const unsubPages = pages.subscribe((pages) => {
        if (pages.data) {
            const existingPages = pages.data.map((pg) => ({
                action: null,
                filename: pg.filename
            }))

            form.update((curr) => ({
                ...curr,
                existingPages
            }))

            formInitial.update((curr) => ({
                ...curr,
                existingPages
            }))
        }
    })

    const errors = derived(form, (curr) => checkErrors(curr))

    const ctx: EditChapterContext = {
        form,
        formInitial,
        controls,
        hasChanges,
        errors,
        submit: () => submit(series, chapter.filename, get(form)),
        destroy: () => unsubPages(),
        pages
    }

    setContext(CTX_KEY, ctx)

    return ctx

    async function fetchPages() {
        const resp = await fetch(
            `/api/series/${series}/${chapter.filename}`
        )
        await throwOnStatus(resp)

        return (await resp.json()) as PageDto[]
    }
}

export function getEditChapterContext(): EditChapterContext {
    return getContext(CTX_KEY)
}

async function submit(
    series: string,
    chapter: string,
    form: EditChapterForm
) {
    const formData = new FormData()

    formData.set('series', series)
    formData.set('chapter', chapter)
    formData.set('name', form.name)

    const to_modify: Record<string, string> = {}
    for (let pg of form.existingPages) {
        if (pg.action?.type === 'delete') {
            formData.append('pages_deleted', pg.filename)
        } else if (pg.action?.type === 'rename') {
            to_modify[pg.filename] = pg.action.filename
        }
    }
    formData.set('pages_modified', JSON.stringify(to_modify))

    for (let pg of form.newPages) {
        let file = pg.file
        if (pg.newFilename) {
            file = new File([file], pg.newFilename, {
                type: file.type
            })
        }
        formData.append('pages_added', pg.file)
    }

    const resp = await fetch('/api/chapter', {
        method: 'PATCH',
        body: formData
    })

    return resp
}

function isFormEqual(
    a: EditChapterForm,
    b: EditChapterForm
): boolean {
    if (a.name !== b.name) {
        return false
    }

    if (a.existingPages.length !== b.existingPages.length) {
        return false
    }
    for (let [pgA, pgB] of zip(a.existingPages, b.existingPages)) {
        if (!isEqual(pgA, pgB)) {
            return false
        }
    }

    if (a.newPages.length !== b.newPages.length) {
        return false
    }
    for (let [pgA, pgB] of zip(a.newPages, b.newPages)) {
        if (pgA.id !== pgB.id) {
            return false
        }

        if (!isFileEqual(pgA.file, pgB.file)) {
            return false
        }

        if (pgA.newFilename !== pgB.newFilename) {
            return false
        }
    }

    return true
}

function checkErrors(form: EditChapterForm): EditChapterFormErrors {
    const errors = {} as EditChapterFormErrors

    const existingNames = form.existingPages.map((pg) =>
        pg.action?.type === 'rename'
            ? pg.action.filename
            : pg.filename
    )
    const newNames = form.newPages.map(
        (pg) => pg.newFilename || pg.file.name
    )
    const tally = counting(
        [...existingNames, ...newNames],
        (name) => name
    )
    for (let [name, count] of Object.entries(tally)) {
        if (count <= 1) {
            continue
        }

        errors['duplicates'] = errors['duplicates'] ?? []
        errors['duplicates'].push(name)
    }

    return errors
}

export type EditChapterFormTemplate = TemplateRecord<{
    name: TemplateScalar<string>
    existingPages: TemplateArray<
        TemplateRecord<{
            filename: TemplateScalar<string>
            action: TemplateScalar<
                | { type: 'delete' }
                | { type: 'rename'; filename: string }
                | null
            >
        }>
    >
    newPages: TemplateArray<
        TemplateRecord<{
            id: TemplateScalar<string>
            file: TemplateScalar<File>
            newFilename: TemplateScalar<string | null>
        }>
    >
}>

export type EditChapterFormControls =
    TemplateToControlType<EditChapterFormTemplate>

export interface EditChapterFormErrors {
    duplicates?: string[]
}
