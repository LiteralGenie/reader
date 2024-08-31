import type { SeriesDto } from '$lib/api/dtos'
import { createFormControlRecord } from '$lib/form/form-control'
import type { FormControlRecord } from '$lib/form/types'
import { deepCopy, isFileEqual } from '$lib/miscUtils'
import { getContext, setContext } from 'svelte'
import { derived, get, writable, type Readable } from 'svelte/store'

const CTX_KEY = 'edit-series'

export interface EditSeriesForm {
    name: string
    id_dex: string
    id_mu: string
    cover: File | null
}

export interface EditSeriesContext {
    form: Readable<EditSeriesForm>
    formInitial: Readable<Readonly<EditSeriesForm>>
    controls: FormControlRecord<EditSeriesForm>
    hasChanges: Readable<boolean>
    submit: () => Promise<any>
}

export function createEditSeriesContext(series: SeriesDto) {
    const initial = {
        name: series.name,
        id_dex: series.id_mangadex,
        id_mu: series.id_mangaupdates,
        cover: null
    }

    const form = writable<EditSeriesForm>(deepCopy(initial))
    const formInitial = writable<EditSeriesForm>(deepCopy(initial))
    const controls = createFormControlRecord(form, {
        _type: 'record',
        name: {
            _type: 'scalar'
        },
        id_dex: {
            _type: 'scalar'
        },
        id_mu: {
            _type: 'scalar'
        },
        cover: {
            _type: 'scalar'
        }
    })
    const hasChanges = derived(
        [formInitial, form],
        ([before, after]) => isFormEqual(before, after)
    )

    const ctx: EditSeriesContext = {
        form,
        formInitial,
        controls,
        hasChanges,
        submit: () => submit(series.filename, get(form))
    }

    setContext(CTX_KEY, ctx)

    return ctx
}

export function getEditSeriesContext(): EditSeriesContext {
    return getContext(CTX_KEY)
}

async function submit(seriesId: string, form: EditSeriesForm) {
    const formData = new FormData()

    formData.set('filename', seriesId)
    formData.set('name', form.name)
    formData.set('id_mangadex', form.id_dex)
    formData.set('id_mangaupdates', form.id_mu)

    if (form.cover) {
        formData.set('cover', form.cover)
    }

    return fetch('/api/series', {
        method: 'PATCH',
        body: formData
    })
}

function isFormEqual(a: EditSeriesForm, b: EditSeriesForm): boolean {
    if (!isFileEqual(a.cover, b.cover)) {
        return true
    }

    const props = ['name', 'id_dex', 'id_mu'] as const
    for (let p of props) {
        if (a[p] !== b[p]) {
            return true
        }
    }

    return false
}
