import { writable, type Readable } from 'svelte/store'

export type PromiseStore<F, P = F> = Readable<PromiseStoreValue<F, P>>

export type PromiseStoreValue<
    IFulfilled = any,
    IPending = IFulfilled
> =
    | {
          data: IPending
          status: 'pending'
          initTime: number
      }
    | {
          data: IFulfilled
          status: 'fulfilled'
          initTime: number
      }

export function newPromiseStore<IFulfilled, IPending>(
    data: Promise<IFulfilled>,
    init: IPending
): PromiseStore<IFulfilled, IPending> {
    const store = writable<PromiseStoreValue<IFulfilled, IPending>>({
        data: init,
        status: 'pending',
        initTime: Date.now()
    })

    data.then((d) =>
        store.update((curr) => ({
            ...curr,
            data: d,
            status: 'fulfilled'
        }))
    )

    return store
}
