import { useRun } from "@/shared/queries/useRun";
import { useSimulationStore } from "@/stores/simulationStore";
import { useStoreAssets } from "@/features/store-viewer/hooks/useStoreAssets";
import { usePersonaData } from "@/features/playback/hooks/usePersonaData";

import { ProjectShell } from "@/views/simulation/ProjectShell";
import { SimulationLayout } from "@/views/simulation/SimulationLayout";
import { SidePanel } from "@/views/simulation/SidePanel";

import type { LayoutTabProps } from "./types";

export function PlaybackView({
  pid,
  runId,
  location,
  layouts,
  selectedSetupId,
  onLayoutSelect,
  onAddLayout,
}: { pid: string; runId: string; location: string } & LayoutTabProps) {
  const run = useRun(pid, runId).data;
  const assets = useStoreAssets(run.store);
  const { personaNames, personaGenders } = usePersonaData(run.personas);
  const activeTab = useSimulationStore((s) => s.activeTab);
  const setActiveTab = useSimulationStore((s) => s.setActiveTab);

  return (
    <ProjectShell
      layouts={layouts}
      selectedLayoutId={selectedSetupId}
      onLayoutSelect={onLayoutSelect}
      onAddLayout={onAddLayout}
      centerSlot={
        <SimulationLayout
          key={run.store.id}
          storeId={run.store.id}
          assets={assets}
          personaNames={personaNames}
          personaGenders={personaGenders}
          customers={run.customers}
          heatmap={run.heatmap}
          mode="playback"
        />
      }
      sidePanelSlot={
        <SidePanel
          mode="playback"
          customers={run.customers}
          minTime={assets.minTime}
          maxTime={assets.maxTime}
          store={run.store}
          summary={run.summary}
          personas={run.personas}
          location={location}
          editableLayout={false}
          activeTab={activeTab}
          setActiveTab={setActiveTab}
        />
      }
    />
  );
}
