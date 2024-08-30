import type { SeriesDto } from '$lib/api/dtos'
import { createFormControlRecord } from '$lib/form/form-control'
import type { FormControlRecord } from '$lib/form/types'
import { deepCopy } from '$lib/miscUtils'
import { setContext } from 'svelte'
import { writable, type Readable } from 'svelte/store'

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
        type: 'record',
        name: {
            type: 'scalar'
        },
        md_id: {
            type: 'scalar'
        },
        mu_id: {
            type: 'scalar'
        },
        cover: {
            type: 'scalar'
        }
    })

    const ctx: EditSeriesContext = {
        form,
        formInitial,
        controls
    }

    setContext(CTX_KEY, ctx)

    return ctx
}
