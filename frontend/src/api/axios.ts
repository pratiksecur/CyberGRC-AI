import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000/api/v1",
});

api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");

    console.log("TOKEN:", token);

    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
      console.log("AUTH HEADER:", config.headers.Authorization);
    }

    return config;
  },
  (error) => Promise.reject(error)
);

export default api;