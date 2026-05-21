import { create } from "zustand";

export type DashboardTab = "dashboard" | "settings";

interface SimulationState {
  highlightId: string | null;
  heatmapOn: boolean;
  activeTab: DashboardTab;
  // Currently selected setup (layout) id. Backend has no "active layout" concept —
  // this is purely local UI state and is not persisted across sessions.
  selectedSetupId: string | null;

  hoveredRackId: string | null;
  selectedRackId: string | null;

  setHighlightId: (id: string | null) => void;
  toggleHeatmap: () => void;
  setActiveTab: (tab: DashboardTab) => void;
  setSelectedSetupId: (id: string | null) => void;
  setHoveredRackId: (id: string | null) => void;
  setSelectedRackId: (id: string | null) => void;
  reset: () => void;
}

export const useSimulationStore = create<SimulationState>((set) => ({
  highlightId: null,
  heatmapOn: false,
  activeTab: "dashboard",
  selectedSetupId: null,
  hoveredRackId: null,
  selectedRackId: null,

  setHighlightId: (id) => set({ highlightId: id }),
  toggleHeatmap: () => set((s) => ({ heatmapOn: !s.heatmapOn })),
  setActiveTab: (tab) => set({ activeTab: tab }),
  setSelectedSetupId: (id) => set({ selectedSetupId: id }),
  setHoveredRackId: (id) => set({ hoveredRackId: id }),
  setSelectedRackId: (id) => set({ selectedRackId: id }),
  reset: () =>
    set({
      highlightId: null,
      heatmapOn: false,
      activeTab: "dashboard" as const,
      selectedSetupId: null,
      hoveredRackId: null,
      selectedRackId: null,
    }),
}));
