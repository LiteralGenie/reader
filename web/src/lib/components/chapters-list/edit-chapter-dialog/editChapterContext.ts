import type { ChapterDto } from '$lib/api/dtos'
import { createFormControlRecord } from '$lib/form/form-control'
import type { FormControlRecord } from '$lib/form/types'
import { deepCopy } from '$lib/miscUtils'
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
    controls: FormControlRecord<EditChapterForm>
    hasChanges: Readable<boolean>
    submit: () => Promise<any>
}

export function createEditChapterContext(chapter: ChapterDto) {
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
    })
    const hasChanges = derived(
        [formInitial, form],
        ([before, after]) => !isFormEqual(before, after)
    )

    const ctx: EditChapterContext = {
        form,
        formInitial,
        controls,
        hasChanges,
        submit: () => submit(chapter.filename, get(form))
    }

    setContext(CTX_KEY, ctx)

    return ctx
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
