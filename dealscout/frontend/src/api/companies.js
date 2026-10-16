import apiClient from "./client";

const TOKEN_KEY = "dealscout_token";

export function setToken(token) {
  localStorage.setItem(TOKEN_KEY, token);
  apiClient.defaults.headers.common["Authorization"] = `Bearer ${token}`;
}

export function getToken() {
  return localStorage.getItem(TOKEN_KEY);
}

export function removeToken() {
  localStorage.removeItem(TOKEN_KEY);
  delete apiClient.defaults.headers.common["Authorization"];
}

export function isAuthenticated() {
  return !!getToken();
}

export async function getCompanies({ limit = 20, offset = 0 } = {}) {
  const response = await apiClient.get("/companies", {
    params: { limit, offset },
  });
  return response.data;
}

export async function getCompanyProfile(companyId) {
  const response = await apiClient.get(`/companies/${companyId}`);
  return response.data;
}

export async function getCompanyScore(companyId) {
  const response = await apiClient.get(`/companies/${companyId}/score`);
  return response.data;
}

export async function getCompanyMLScore(companyId) {
  const response = await apiClient.get(`/companies/${companyId}/ml-score`);
  return response.data;
}

export async function searchCompanies(filters = {}) {
  const response = await apiClient.get("/search", {
    params: filters,
  });
  return response.data;
}

export async function getMarketAnalysis() {
  const response = await apiClient.get("/market-analysis");
  return response.data;
}

export async function login({ username, password }) {
  const response = await apiClient.post("/auth/token", null, {
    params: { username, password },
  });
  const { access_token } = response.data;
  setToken(access_token);
  return response.data;
}

export async function logout() {
  removeToken();
}
