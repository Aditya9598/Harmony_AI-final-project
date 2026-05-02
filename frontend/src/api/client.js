import axios from "axios";

const apiBaseUrl = import.meta.env.VITE_API_BASE_URL;

if (!apiBaseUrl) {
  throw new Error("VITE_API_BASE_URL is missing in frontend/.env");
}

export const api = axios.create({
  baseURL: apiBaseUrl,
  timeout: 30000,
});
