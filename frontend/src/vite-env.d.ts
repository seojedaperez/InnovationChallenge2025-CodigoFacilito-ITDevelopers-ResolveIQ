/// <reference types="vite/client" />

interface ImportMetaEnv {
    readonly VITE_AZURE_AD_CLIENT_ID: string
    readonly VITE_AZURE_AD_TENANT_ID: string
    // more env variables...
}

interface ImportMeta {
    readonly env: ImportMetaEnv
}
