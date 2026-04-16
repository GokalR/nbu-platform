/**
 * Base URL for the backend API.
 * In production, points directly to Railway. In dev, uses local proxy (empty string).
 */
export const BACKEND_URL = import.meta.env.VITE_BACKEND_URL?.replace(/\/$/, '') || ''
