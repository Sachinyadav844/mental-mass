/** Backend origin — match Flask (see backend config FLASK_PORT). Override with VITE_API_URL in .env */
export const API_BASE_URL =
  import.meta.env.VITE_API_URL?.replace(/\/$/, "") ??
  "http://localhost:5000";
