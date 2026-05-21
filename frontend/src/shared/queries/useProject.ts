import { useSuspenseQuery } from "@tanstack/react-query";
import * as api from "@/shared/api/client";
import { queryKeys } from "./keys";

export function useProject(projectId: string) {
  return useSuspenseQuery({
    queryKey: queryKeys.project(projectId),
    queryFn: ({ signal }) => api.getProject(projectId, signal),
  });
}
