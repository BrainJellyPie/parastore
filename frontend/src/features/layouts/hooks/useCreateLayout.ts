import { useMutation, useQueryClient } from "@tanstack/react-query";
import { createSetup, type SetupSummaryShort } from "@/shared/api/client";
import { queryKeys } from "@/shared/queries/keys";
import { useSimulationStore } from "@/stores/simulationStore";

// "import" clones from a parent setup; "empty" creates a blank setup.
type CreateLayoutSource =
  | { kind: "import"; parentSetupId: string }
  | { kind: "empty" };

interface Params {
  projectId: string;
  name: string;
  source: CreateLayoutSource;
}

export function useCreateLayout() {
  const qc = useQueryClient();
  const setSelected = useSimulationStore((s) => s.setSelectedSetupId);

  return useMutation<SetupSummaryShort, Error, Params>({
    mutationFn: ({ projectId, name, source }) =>
      createSetup(projectId, {
        mode: source.kind === "import" ? "racks_and_items" : "empty",
        source_setup_id: source.kind === "import" ? source.parentSetupId : null,
        name,
      }),
    onSuccess: (newSetup, vars) => {
      qc.invalidateQueries({ queryKey: queryKeys.setups(vars.projectId) });
      qc.invalidateQueries({ queryKey: queryKeys.project(vars.projectId) });
      setSelected(newSetup.id);
    },
  });
}
