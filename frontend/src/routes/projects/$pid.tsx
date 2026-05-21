import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Suspense, useEffect, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import { usePlaybackControlStore } from "@/stores/playbackControlStore";
import { useSimulationMetricsStore } from "@/stores/simulationMetricsStore";
import { useSimulationStore } from "@/stores/simulationStore";
import { useProject } from "@/shared/queries/useProject";
import { useSetup } from "@/shared/queries/useSetup";
import { useRuns } from "@/shared/queries/useRuns";
import { useSetupGeneration } from "@/shared/queries/useSetupGeneration";
import { deleteProject } from "@/shared/api/client";
import { queryKeys } from "@/shared/queries/keys";
import { PreparingView } from "@/views/simulation/states/PreparingView";
import { ReadyView } from "@/views/simulation/states/ReadyView";
import { RunningView } from "@/views/simulation/states/RunningView";
import { PlaybackView } from "@/views/simulation/states/PlaybackView";
import { EmptyFloorReadyView } from "@/views/simulation/states/EmptyFloorReadyView";
import { useLayouts, type Layout } from "@/features/layouts/hooks/useLayouts";
import { useSwitchLayout } from "@/features/layouts/hooks/useSwitchLayout";
import { AddLayoutDialog } from "@/features/layouts/components/AddLayoutDialog";
import type { ProjectDetail, SetupDetail } from "@/shared/api/client";
import type { Store } from "@/shared/types/domain";

export const Route = createFileRoute("/projects/$pid")({
  component: SimulationPage,
});

function SimulationPage() {
  const { pid } = Route.useParams();
  return <SimulationPageInner pid={pid} />;
}

function SimulationPageInner({ pid }: { pid: string }) {
  const project = useProject(pid).data;
  const layoutsQuery = useLayouts(pid);
  const layouts = layoutsQuery.data;
  const selectedSetupId = useSimulationStore((s) => s.selectedSetupId);
  const switchLayout = useSwitchLayout();

  useEffect(() => {
    if (!selectedSetupId && layouts && layouts.length > 0) {
      switchLayout(layouts[0]!.id);
    }
  }, [selectedSetupId, layouts, switchLayout]);

  useEffect(() => {
    return () => {
      usePlaybackControlStore.getState().reset();
      useSimulationMetricsStore.getState().reset();
      useSimulationStore.getState().reset();
    };
  }, []);

  const effectiveSetupId = selectedSetupId ?? layouts?.[0]?.id;
  const [addLayoutOpen, setAddLayoutOpen] = useState(false);

  if (!effectiveSetupId || !layouts) {
    return (
      <div className="flex flex-1 items-center justify-center text-sm text-muted-foreground">
        Loading layout…
      </div>
    );
  }

  return (
    <>
      {/*
        Local Suspense — on layout switch, if useSetup(useSuspenseQuery)'s cache miss
        bubbles up to the root Suspense, SimulationPageInner itself unmounts and the
        cleanup useEffect (below) calls simulationStore.reset(), which nulls
        selectedSetupId. On remount, the initial useEffect restores it to layouts[0],
        producing a regression where "selection snaps back to layout 1". A local
        Suspense boundary scopes the remount to SimulationPageContent and preserves
        inner state. fallback=null works with startTransition so the previous content
        stays visible until the transition completes.
      */}
      <Suspense fallback={null}>
        <SimulationPageContent
          pid={pid}
          project={project}
          effectiveSetupId={effectiveSetupId}
          layouts={layouts}
          onLayoutSelect={switchLayout}
          onAddLayout={() => setAddLayoutOpen(true)}
        />
      </Suspense>
      <AddLayoutDialog
        open={addLayoutOpen}
        onOpenChange={setAddLayoutOpen}
        projectId={pid}
        parentSetupId={effectiveSetupId}
        layouts={layouts}
      />
    </>
  );
}

interface SimulationPageContentProps {
  pid: string;
  project: ProjectDetail;
  effectiveSetupId: string;
  layouts: Layout[];
  onLayoutSelect: (id: string) => void;
  onAddLayout: () => void;
}

function SimulationPageContent({
  pid,
  project,
  effectiveSetupId,
  layouts,
  onLayoutSelect,
  onAddLayout,
}: SimulationPageContentProps) {
  const setup = useSetup(pid, effectiveSetupId).data;
  const runs = useRuns(pid, effectiveSetupId).data;
  const navigate = useNavigate();
  const qc = useQueryClient();

  const generation = useSetupGeneration(pid, effectiveSetupId);

  const location = project.metadata.address;

  const completedRun = [...runs]
    .filter((r) => r.status === "completed")
    .sort((a, b) => b.created_at.localeCompare(a.created_at))[0];
  const runningRun = runs.find((r) => r.status === "running");

  const tabProps = {
    layouts,
    selectedSetupId: effectiveSetupId,
    onLayoutSelect,
    onAddLayout,
  };

  const reasons = setup.readiness?.reasons ?? [];

  const layoutPending =
    generation.phase === "layout" || reasons.includes("layout_pending");
  const personaPending =
    generation.phase === "persona" || reasons.includes("personas_pending");
  const personaMissing = reasons.includes("no_personas");
  const isFailedLayoutCtx =
    generation.phase === "failed" && generation.kind === "layout";
  const isFailedPersonaCtx =
    generation.phase === "failed" && generation.kind === "persona";
  const isPreparing =
    layoutPending ||
    personaPending ||
    isFailedPersonaCtx ||
    isFailedLayoutCtx ||
    personaMissing;

  const contextKind: "layout" | "persona" =
    layoutPending || isFailedLayoutCtx ? "layout" : "persona";

  // Mode resolver — priority order (spec §7):
  //   1) any layout/persona signal → PreparingView
  //   2) (all above false) store==null → EmptyFloorReadyView (post-wizard + persona ready)
  //   3) store!=null → existing RunningView/PlaybackView/ReadyView flow
  // PreparingView renders outside SimulationLayout — SimulationLayout's store asset
  // hook blows up on a null store, so it can't be reused.
  if (isPreparing) {
    return (
      <PreparingView
        generation={generation}
        contextKind={contextKind}
        onAbandonProject={() => {
          void deleteProject(pid).finally(() => {
            qc.invalidateQueries({ queryKey: queryKeys.projects() });
            void navigate({ to: "/projects/new" });
          });
        }}
      />
    );
  }

  const hasFloor = setup.store != null;

  if (!hasFloor) {
    return (
      <EmptyFloorReadyView
        pid={pid}
        setupId={effectiveSetupId}
        setup={setup}
        personas={project.personas}
        location={location}
        {...tabProps}
      />
    );
  }
  const setupWithStore: SetupDetail & { store: Store } = {
    ...setup,
    store: setup.store!,
  };

  if (completedRun) {
    return (
      <PlaybackView
        pid={pid}
        runId={completedRun.run_id}
        location={location}
        {...tabProps}
      />
    );
  }
  if (runningRun) {
    return (
      <RunningView
        pid={pid}
        setupId={effectiveSetupId}
        runId={runningRun.run_id}
        setup={setupWithStore}
        personas={project.personas}
        location={location}
        {...tabProps}
      />
    );
  }
  return (
    <ReadyView
      pid={pid}
      setupId={effectiveSetupId}
      setup={setupWithStore}
      personas={project.personas}
      location={location}
      {...tabProps}
    />
  );
}
