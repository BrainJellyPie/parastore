import { useQuery } from "@tanstack/react-query";
import * as api from "@/shared/api/client";
import { queryKeys } from "./keys";

export function useProjects() {
  return useQuery({
    queryKey: queryKeys.projects(),
    queryFn: ({ signal }) => api.getProjects(signal),
  });
}
