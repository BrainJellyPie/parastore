import { useSuspenseQuery } from "@tanstack/react-query";
import * as api from "@/shared/api/client";
import { queryKeys } from "./keys";

export function useSetup(projectId: string, setupId: string) {
  return useSuspenseQuery({
    queryKey: queryKeys.setup(projectId, setupId),
    queryFn: ({ signal }) => api.getSetup(projectId, setupId, signal),
  });
}
