/// <reference types="vite/client" />
declare module '*.vue' {
  import type { DefineComponent } from 'vue'
  const component: DefineComponent<Record<string, unknown>, Record<string, unknown>, any>
  export default component
}

declare module '*.glb' { const src: string; export default src }
declare module '*.gltf' { const src: string; export default src }
declare module '*.obj' { const src: string; export default src }

