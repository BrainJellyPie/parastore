import { useEffect } from "react";
import { useQueryClient } from "@tanstack/react-query";

import { useRunStatus } from "@/shared/queries/useRunStatus";
import { queryKeys } from "@/shared/queries/keys";
import { useSimulationStore } from "@/stores/simulationStore";
import { useStoreAssets } from "@/features/store-viewer/hooks/useStoreAssets";
import { usePersonaData } from "@/features/playback/hooks/usePersonaData";

import { ProjectShell } from "@/views/simulation/ProjectShell";
import { SimulationLayout } from "@/views/simulation/SimulationLayout";
import { SidePanel } from "@/views/simulation/SidePanel";

import type { LayoutTabProps, ViewCommon } from "./types";

export function RunningView({
  pid,
  setupId,
  runId,
  setup,
  personas,
  location,
  layouts,
  selectedSetupId,
  onLayoutSelect,
  onAddLayout,
}: ViewCommon & { setupId: string; runId: string } & LayoutTabProps) {
  const qc = useQueryClient();
  const statusQuery = useRunStatus(pid, runId);
  const status = statusQuery.data;
  const assets = useStoreAssets(setup.store);
  const { personaNames, personaGenders } = usePersonaData(personas);
  const activeTab = useSimulationStore((s) => s.activeTab);
  const setActiveTab = useSimulationStore((s) => s.setActiveTab);

  useEffect(() => {
    if (status?.status === "completed") {
      qc.invalidateQueries({ queryKey: queryKeys.runs(pid, setupId) });
    }
  }, [status?.status, qc, pid, setupId]);

  if (statusQuery.error) {
    throw statusQuery.error;
  }
  if (status?.status === "failed") {
    throw new Error(status.error ?? "Simulation failed");
  }

  // While a simulation runs the setup is locked (status="running") on the backend,
  // so PUT /slots is rejected with 409. Hide the entry point to prevent the invalid
  // action — to refill slots the user must create a new layout and upload to that draft.
  return (
    <ProjectShell
      layouts={layouts}
      selectedLayoutId={selectedSetupId}
      onLayoutSelect={onLayoutSelect}
      onAddLayout={onAddLayout}
      centerSlot={
        <SimulationLayout
          key={setup.id}
          storeId={setup.store.id}
          assets={assets}
          personaNames={personaNames}
          personaGenders={personaGenders}
          customers={null}
          heatmap={null}
          mode="running"
        />
      }
      sidePanelSlot={
        <SidePanel
          mode="running"
          customers={null}
          minTime={assets.minTime}
          maxTime={assets.maxTime}
          store={setup.store}
          summary={null}
          personas={personas}
          location={location}
          editableLayout={false}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />
      }
    />
  );
}
