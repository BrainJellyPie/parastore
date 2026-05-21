import { Play, Pause, SkipForward, RotateCcw, ChevronLeft, ChevronRight, Layers } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { ToggleGroup, ToggleGroupItem } from "@/shared/components/ui/toggle-group";
import { usePlaybackControlStore, type PlaybackSpeed } from "@/stores/playbackControlStore";
import { useSimulationMetricsStore } from "@/stores/simulationMetricsStore";
import { useSimulationStore } from "@/stores/simulationStore";

interface Props {
  minTime: number;
  maxTime: number;
}

const SPEED_LABEL: Record<PlaybackSpeed, string> = {
  60: "Normal",
  600: "Fast",
  3600: "Very fast",
};
const SPEED_VALUES: PlaybackSpeed[] = [60, 600, 3600];

const WEEKDAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] as const;

function formatClock12h(sec: number): string {
  const h = Math.floor(sec / 3600) % 24;
  const m = Math.floor((sec % 3600) / 60);
  const ampm = h < 12 ? "am" : "pm";
  const hh = h === 0 ? 12 : h > 12 ? h - 12 : h;
  return `${hh}:${String(m).padStart(2, "0")} ${ampm}`;
}

export function TimeBar({ minTime, maxTime }: Props) {
  const playing = usePlaybackControlStore((s) => s.playing);
  const speed = usePlaybackControlStore((s) => s.speed);
  const togglePlay = usePlaybackControlStore((s) => s.togglePlay);
  const setSpeed = usePlaybackControlStore((s) => s.setSpeed);
  const seek = usePlaybackControlStore((s) => s.seek);
  const currentDay = usePlaybackControlStore((s) => s.currentDay);
  const availableDays = usePlaybackControlStore((s) => s.availableDays);
  const nextDay = usePlaybackControlStore((s) => s.nextDay);
  const prevDay = usePlaybackControlStore((s) => s.prevDay);
  const currentMinute = useSimulationMetricsStore((s) => s.currentMinute);
  const finished = useSimulationMetricsStore((s) => s.finished);
  const heatmapOn = useSimulationStore((s) => s.heatmapOn);
  const toggleHeatmap = useSimulationStore((s) => s.toggleHeatmap);

  const disabled = maxTime <= minTime;
  const dayIdx = availableDays.indexOf(currentDay);
  const isFirst = dayIdx <= 0;
  const isLast = dayIdx >= availableDays.length - 1;
  const weekdayLabel = WEEKDAYS[(currentDay - 1) % 7];

  const handleReset = () => {
    usePlaybackControlStore.getState().setDay(availableDays[0] ?? 1);
    seek(minTime);
  };

  return (
    <div className="absolute top-4 right-4 w-[380px] rounded-lg border bg-background/95 p-4 shadow-md">
      <div className="flex items-start justify-between gap-3">
        <div className="flex flex-col gap-2.5">
          <div className="flex items-center gap-1">
            <Button
              variant="ghost"
              size="sm"
              className="size-5 p-0"
              disabled={isFirst}
              onClick={prevDay}
            >
              <ChevronLeft className="size-3" />
            </Button>
            <span className="text-xs font-medium text-muted-foreground">
              Day {dayIdx + 1} ({weekdayLabel})
            </span>
            <Button
              variant="ghost"
              size="sm"
              className="size-5 p-0"
              disabled={isLast}
              onClick={nextDay}
            >
              <ChevronRight className="size-3" />
            </Button>
          </div>
          <div className="font-mono text-3xl font-bold tabular-nums leading-none">
            {finished ? "End" : formatClock12h(currentMinute)}
          </div>
        </div>

        <div className="flex shrink-0 items-center gap-1.5">
          {finished ? (
            <Button
              variant="outline"
              size="sm"
              className="h-8 gap-1 text-xs"
              onClick={handleReset}
            >
              <RotateCcw className="size-3" />
              Reset
            </Button>
          ) : (
            <>
              <Button
                variant="outline"
                size="sm"
                className="h-8 gap-1 text-xs"
                disabled={disabled}
                onClick={() => seek(maxTime)}
              >
                <SkipForward className="size-3" />
                Skip
              </Button>
              <Button
                size="sm"
                className="h-8 gap-1 px-3 text-xs"
                disabled={disabled}
                onClick={togglePlay}
              >
                {playing ? <Pause className="size-3.5" /> : <Play className="size-3.5" />}
                {playing ? "Pause" : "Play"}
              </Button>
            </>
          )}
        </div>
      </div>

      <div className="mt-5 flex items-center justify-between">
        <div className="flex items-center gap-2.5">
          <span className="text-xs text-muted-foreground">Speed</span>
          <ToggleGroup
            type="single"
            value={String(speed)}
            onValueChange={(v) => v && setSpeed(Number(v) as PlaybackSpeed)}
            variant="outline"
            size="sm"
            disabled={disabled}
          >
            {SPEED_VALUES.map((s) => (
              <ToggleGroupItem
                key={s}
                value={String(s)}
                className="h-7 px-2.5 text-xs"
              >
                {SPEED_LABEL[s]}
              </ToggleGroupItem>
            ))}
          </ToggleGroup>
        </div>
        <Button
          variant={heatmapOn ? "default" : "outline"}
          size="sm"
          className="h-7 gap-1 px-2 text-xs"
          onClick={toggleHeatmap}
        >
          <Layers className="size-3" />
          Heatmap
        </Button>
      </div>
    </div>
  );
}
