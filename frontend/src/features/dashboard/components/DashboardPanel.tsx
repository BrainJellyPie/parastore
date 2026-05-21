import type { CustomerResult, Store } from "@/shared/types/domain";
import type { SetupDetailWithBlocked } from "@/features/grid-editor/types";
import { Lock } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/shared/components/ui/alert-dialog";
import { FloorConfigurationPanel } from "@/features/grid-editor/FloorConfigurationPanel";
import { LayoutExcelControls } from "@/features/layouts/components/LayoutExcelControls";
import { reasonIcon, reasonLabel, type Availability } from "@/views/simulation/availability";
import { PlaybackStatus } from "./sections/PlaybackStatus";
import { TimelineChart } from "./sections/TimelineChart";
import { Summary } from "./sections/Summary";
import { CustomerBehavior } from "./sections/CustomerBehavior";
import { RackRanking } from "./sections/RackRanking";
import { TopItems } from "./sections/TopItems";

export type DashboardMode = "ready" | "running" | "playback";

interface ReadyProps {
  mode: "ready";
  pid: string;
  sid: string;
  setup: SetupDetailWithBlocked;
  itemCount: number;
  onBusyChange?: (busy: boolean) => void;
  onSimulate?: () => void;
  simulating?: boolean;
  simulateError?: Error | null;
  availability?: Availability;
}

interface RunningProps {
  mode: "running";
}

interface PlaybackProps {
  mode: "playback";
  customers: CustomerResult[] | null;
  minTime: number;
  maxTime: number;
  store: Store;
}

export type DashboardPanelProps = ReadyProps | RunningProps | PlaybackProps;

export function DashboardPanel(props: DashboardPanelProps) {
  if (props.mode === "playback") {
    return <PlaybackContent {...props} />;
  }
  if (props.mode === "running") {
    return <RunningContent />;
  }
  return <ReadyContent {...props} />;
}

function PlaybackContent({ customers, minTime, maxTime, store }: PlaybackProps) {
  return (
    <div className="flex flex-col">
      <PlaybackStatus minTime={minTime} maxTime={maxTime} />
      <TimelineChart customers={customers} minTime={minTime} maxTime={maxTime} />
      <Summary />
      <CustomerBehavior />
      <RackRanking store={store} />
      <TopItems store={store} />
    </div>
  );
}

function RunningContent() {
  return (
    <div className="flex flex-col items-center gap-2 pt-12 pb-6 text-center">
      <div className="text-sm font-medium">Running simulation…</div>
      <div className="text-xs text-muted-foreground">Waiting for results</div>
    </div>
  );
}

function ReadyContent({
  pid,
  sid,
  setup,
  itemCount,
  onBusyChange,
  onSimulate,
  simulating,
  simulateError,
  availability,
}: ReadyProps) {
  const hasFloor = setup.store != null;
  const blocked = availability !== undefined && !availability.canSimulate;

  return (
    <div className="flex flex-col gap-4 px-0 pt-3 pb-6">
      {/* Step 1: FloorConfigurationPanel renders its own "Step 1" header. */}
      <section className="flex flex-col gap-2">
        <FloorConfigurationPanel
          pid={pid}
          sid={sid}
          setup={setup}
          itemCount={itemCount}
          onBusyChange={onBusyChange}
        />
      </section>

      {/* Step 2 shows a locked placeholder until the floor exists. */}
      {!hasFloor && (
        <section className="flex items-center justify-between gap-2 rounded-lg border bg-muted/40 p-4 text-sm">
          <h3 className="text-sm font-medium text-muted-foreground">
            Step 2: Item placement
          </h3>
          <Lock aria-hidden className="size-4 text-muted-foreground" />
        </section>
      )}

      {hasFloor && setup.store && (
        <section className="flex flex-col gap-2 rounded-lg border bg-card p-4 text-sm">
          <h3 className="text-sm font-medium">Step 2: Item placement</h3>
          <LayoutExcelControls
            store={setup.store}
            projectId={pid}
            setupId={sid}
          />
          <div className="mt-2 flex flex-col gap-1.5">
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button
                  size="lg"
                  disabled={simulating || blocked || !onSimulate}
                >
                  {simulating ? "Running simulation…" : "Run simulation"}
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent className="data-[size=default]:sm:max-w-lg">
                <AlertDialogHeader>
                  <AlertDialogTitle>Run simulation?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will consume API tokens based on your daily visitor cap. Continue?
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction onClick={onSimulate}>Run simulation</AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
            {blocked && availability && availability.reasons.length > 0 && (
              <ul className="flex flex-col gap-1">
                {availability.reasons.map((r) => {
                  const Icon = reasonIcon(r);
                  return (
                    <li
                      key={r}
                      className="flex items-start gap-2 rounded-md border bg-muted/40 px-2 py-1.5 text-xs"
                    >
                      <Icon
                        aria-hidden
                        className="mt-0.5 size-3 shrink-0 text-muted-foreground"
                      />
                      <span>{reasonLabel(r)}</span>
                    </li>
                  );
                })}
              </ul>
            )}
            {simulateError && (
              <p className="text-xs text-destructive">
                {simulateError instanceof Error
                  ? simulateError.message
                  : "Simulation run failed"}
              </p>
            )}
          </div>
        </section>
      )}
    </div>
  );
}
