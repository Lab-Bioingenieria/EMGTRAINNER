import axios from "axios";
import { API_BASE_URL } from "./constants";
import { authService } from "@/services/auth.service";

const api = axios.create({
    baseURL: API_BASE_URL,
    headers: {
        "Content-Type": "application/json",
    },
});

api.interceptors.request.use((config) => {
    const authHeaders = authService.authHeaders();
    if (authHeaders.Authorization) {
        config.headers.Authorization = authHeaders.Authorization;
    }
    return config;
});

api.interceptors.response.use(
    (response) => response,
    (error) => {
        console.error("API Error:", error.response?.data || error.message);
        // Session rejected by the backend: clear the token and go to login.
        // redirectToLogin() is a no-op on /login, so failed logins don't loop.
        if (error.response?.status === 401) {
            authService.handleUnauthorized();
        }
        return Promise.reject(error);
    }
);

export default api;
