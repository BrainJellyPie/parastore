import { useMutation, useQueryClient } from "@tanstack/react-query";

import {
  createStore,
  type CreateStoreMeta,
  type CreateStoreResponse,
} from "@/shared/api/client";
import { queryKeys } from "@/shared/queries/keys";

interface MutateInput {
  meta: CreateStoreMeta;
  supplemental: File | null;
}

export function useCreateStore() {
  const qc = useQueryClient();
  return useMutation<CreateStoreResponse, Error, MutateInput>({
    mutationFn: ({ meta, supplemental }) => createStore(meta, supplemental),
    onSuccess: () => {
      qc.invalidateQueries({ queryKey: queryKeys.projects() });
    },
  });
}
