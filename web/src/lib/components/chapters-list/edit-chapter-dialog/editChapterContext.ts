import type { ChapterDto, PageDto } from '$lib/api/dtos'
import { createFormControlRecord } from '$lib/form/form-control'
import type {
    TemplateArray,
    TemplateRecord,
    TemplateScalar,
    TemplateToControlType
} from '$lib/form/types'
import { deepCopy, throwOnStatus } from '$lib/miscUtils'
import { newPromiseStore, type PromiseStore } from '$lib/promiseStore'
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
    newPages: File[]
}

export interface EditChapterContext {
    form: Readable<EditChapterForm>
    formInitial: Readable<Readonly<EditChapterForm>>
    controls: EditChapterFormControls
    hasChanges: Readable<boolean>
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
                _type: 'scalar'
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
            form.update((curr) => ({
                ...curr,
                existingPages: pages.data.map((pg) => ({
                    action: null,
                    filename: pg.filename
                }))
            }))
        }
    })

    const ctx: EditChapterContext = {
        form,
        formInitial,
        controls,
        hasChanges,
        submit: () => submit(chapter.filename, get(form)),
        pages,
        destroy: () => unsubPages()
    }

    setContext(CTX_KEY, ctx)

    return ctx

    async function fetchPages() {
        const resp = await fetch(
            `/api/series/${series}/${chapter.filename}`
        )
        throwOnStatus(resp)

        return (await resp.json()) as PageDto[]
    }
}

export function getEditChapterContext(): EditChapterContext {
    return getContext(CTX_KEY)
}

async function submit(seriesId: string, form: EditChapterForm) {
    const formData = new FormData()

    alert('@todo')
    return

    return fetch('/api/series', {
        method: 'PATCH',
        body: formData
    })
}

function isFormEqual(
    a: EditChapterForm,
    b: EditChapterForm
): boolean {
    // @todo
    return false

    return true
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
    newPages: TemplateArray<TemplateScalar<File>>
}>

export type EditChapterFormControls =
    TemplateToControlType<EditChapterFormTemplate>
