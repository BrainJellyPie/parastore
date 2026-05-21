import { useMutation } from "@tanstack/react-query";
import { regeneratePersona } from "@/shared/api/client";

interface MutateInput {
  projectId: string;
  setupId: string;
}

// Triggers regen only; polling and invalidation live in useSetupGeneration via the returned gen_id.
export function useRegeneratePersona() {
  return useMutation<{ gen_id: string }, Error, MutateInput>({
    mutationFn: ({ projectId, setupId }) => regeneratePersona(projectId, setupId),
  });
}
