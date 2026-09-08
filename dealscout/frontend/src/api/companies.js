import apiClient from "./client";

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
