/*
useSearch.js — Hook React Query pour la recherche (Palier G)

useQuery() branché sur api/companies.js searchCompanies,
avec les filtres en dépendances de la query key.
*/

import { useQuery } from "@tanstack/react-query";
import { searchCompanies } from "../api/companies";

export function useSearch(filters, enabled = true) {
  return useQuery({
    queryKey: ["search", filters],
    queryFn: () => searchCompanies(filters),
    enabled: enabled && Object.values(filters).some((v) => v !== "" && v != null),
    staleTime: 5 * 60 * 1000,
    refetchOnWindowFocus: false,
  });
}
