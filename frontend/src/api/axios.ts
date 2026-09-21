import axios from "axios";

const api = axios.create({
  baseURL:
    import.meta.env.VITE_API_URL ||
    "http://127.0.0.1:8000/api/v1",
});


/*
 * Attach the current access token to every API request.
 */
api.interceptors.request.use(
  (config) => {
    const token =
      localStorage.getItem(
        "access_token"
      );

    if (token) {
      config.headers.Authorization =
        `Bearer ${token}`;
    }

    return config;
  },
  (error) =>
    Promise.reject(error)
);


/*
 * Handle expired / invalid JWTs centrally.
 *
 * A 401 means authentication failed.
 * Remove the invalid token and notify the AuthContext so
 * React state is cleared immediately as well.
 */
api.interceptors.response.use(
  (response) => response,

  (error) => {
    if (
      error.response?.status === 401
    ) {
      localStorage.removeItem(
        "access_token"
      );

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