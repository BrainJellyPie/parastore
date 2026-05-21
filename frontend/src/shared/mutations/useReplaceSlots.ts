import { useMutation, useQueryClient } from "@tanstack/react-query";
import { replaceSlots, type ReplaceSlotsResponse } from "@/shared/api/client";
import type { SlotRow } from "@/shared/types/domain";
import { queryKeys } from "@/shared/queries/keys";

interface MutateInput {
  projectId: string;
  setupId: string;
  slots: SlotRow[];
}

// projects() is intentionally not invalidated — list page relies on
// stale-while-revalidate on re-entry.
export function useReplaceSlots() {
  const qc = useQueryClient();
  return useMutation<ReplaceSlotsResponse, Error, MutateInput>({
    mutationFn: ({ projectId, setupId, slots }) =>
      replaceSlots(projectId, setupId, slots),
    onSuccess: (_data, { projectId, setupId }) => {
      qc.invalidateQueries({ queryKey: queryKeys.setup(projectId, setupId) });
      qc.invalidateQueries({ queryKey: queryKeys.setups(projectId) });
      qc.invalidateQueries({ queryKey: queryKeys.project(projectId) });
    },
  });
}
