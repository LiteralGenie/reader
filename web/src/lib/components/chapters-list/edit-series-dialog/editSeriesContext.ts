import type { SeriesDto } from '$lib/api/dtos'
import { createFormControlRecord } from '$lib/form/form-control'
import type { FormControlRecord } from '$lib/form/types'
import { deepCopy } from '$lib/miscUtils'
import { setContext } from 'svelte'
import { get, writable, type Readable } from 'svelte/store'

const CTX_KEY = 'edit-series'

export interface EditSeriesForm {
    name: string
    md_id: string
    mu_id: string
    cover: File | null
}

export interface EditSeriesContext {
    form: Readable<EditSeriesForm>
    formInitial: Readable<Readonly<EditSeriesForm>>
    controls: FormControlRecord<EditSeriesForm>
    submit: () => Promise<any>
}

export function createEditSeriesContext(series: SeriesDto) {
    const initial = {
        name: series.name,
        md_id: series.id_mangadex,
        mu_id: series.id_mangaupdates,
        cover: null
    }

    const form = writable<EditSeriesForm>(deepCopy(initial))
    const formInitial = writable<EditSeriesForm>(deepCopy(initial))
    const controls = createFormControlRecord(form, {
        _type: 'record',
        name: {
            _type: 'scalar'
        },
        md_id: {
            _type: 'scalar'
        },
        mu_id: {
            _type: 'scalar'
        },
        cover: {
            _type: 'scalar'
        }
    })

    const ctx: EditSeriesContext = {
        form,
        formInitial,
        controls,
        submit: () => submit(series.filename, get(form))
    }

    setContext(CTX_KEY, ctx)

    return ctx
}

async function submit(seriesId: string, form: EditSeriesForm) {
    const formData = new FormData()

    formData.set('filename', seriesId)
    formData.set('name', form.name)
    formData.set('id_mangadex', form.md_id)
    formData.set('id_mangaupdates', form.mu_id)

    if (form.cover) {
        formData.set('cover', form.cover)
    }

    return fetch('/api/series', {
        method: 'PATCH',
        body: formData
    })
}
