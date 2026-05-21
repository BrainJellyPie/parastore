import { startTransition, useCallback } from "react";
import { useSimulationStore } from "@/stores/simulationStore";

// Layout switching is pure local UI state — no server call. Wrap in startTransition
// so a useSetup(useSuspenseQuery) cache miss does not fall through to the root
// Suspense fallback; the previous UI stays visible. Avoids a "page refresh" flash
// that otherwise appears on the first switch.
export function useSwitchLayout() {
  const setSelectedSetupId = useSimulationStore((s) => s.setSelectedSetupId);
  return useCallback(
    (id: string) => {
      startTransition(() => {
        setSelectedSetupId(id);
      });
    },
    [setSelectedSetupId],
  );
}
