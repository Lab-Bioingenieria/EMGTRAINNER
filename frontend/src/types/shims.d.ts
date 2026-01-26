declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<{}, {}, any>
  export default component
}

declare module 'pinia' {
  export function defineStore(id: string, setup: any): any
  export {}
}

declare module 'vue' {
  export type Ref<T> = { value: T }
  export function ref<T = any>(value?: T): Ref<T | undefined>
  export function computed<T>(fn: () => T): Ref<T>
  export function onMounted(fn: () => void): void
  export function onUnmounted(fn: () => void): void
  export function defineComponent(opts: any): any
  export type DefineComponent = any
}

declare module 'three/examples/jsm/loaders/GLTFLoader'
