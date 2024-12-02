/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_API_HOST: string
    // More env variables can be added here
    [key: string]: any
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}

declare module '*.vue' {
    import type { DefineComponent } from 'vue'
    const component: DefineComponent<{}, {}, any>
    export default component
}
