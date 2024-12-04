/// <reference types="vite/client" />

// API配置
const DEFAULT_API_HOST = 'https://www.blog-keeper.com';

export const API_CONFIG = {
    HOST: (() => {
        try {
            return import.meta.env.VITE_API_HOST || DEFAULT_API_HOST;
        } catch {
            console.warn('Unable to read VITE_API_HOST from environment, using default');
            return DEFAULT_API_HOST;
        }
    })()
};
