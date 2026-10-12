import axios from "axios";

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_URL ||
    "http://localhost:8000/api/v1",

  /*
   * The session lives in an httpOnly cookie that JavaScript cannot read.
   * The browser must be told to send it with every API request.
   */
  withCredentials: true,
});


/*
 * CSRF token for the current session.
 *
 * It is kept in memory only (never in localStorage) and is loaded by the
 * AuthContext after login or session restore.
 */
let csrfToken: string | null = null;

export function setCsrfToken(token: string | null) {
  csrfToken = token;
}

const STATE_CHANGING_METHODS = new Set([
  "post",
  "put",
  "patch",
  "delete",
]);


/*
 * Attach the CSRF token to requests that change state.
 */
api.interceptors.request.use(
  (config) => {
    const method = (
      config.method ?? "get"
    ).toLowerCase();

    if (
      csrfToken &&
      STATE_CHANGING_METHODS.has(method)
    ) {
      config.headers["X-CSRF-Token"] =
        csrfToken;
    }

    return config;
  },
  (error) =>
    Promise.reject(error)
);


/*
 * Handle expired / invalid sessions centrally.
 *
 * A 401 means authentication failed. Notify the AuthContext so
 * React state is cleared immediately.
 */
api.interceptors.response.use(
  (response) => response,

  (error) => {
    if (
      error.response?.status === 401
    ) {
      setCsrfToken(null);

      window.dispatchEvent(
        new CustomEvent(
          "auth:unauthorized"
        )
      );
    }

    return Promise.reject(error);
  }
);


export default api;