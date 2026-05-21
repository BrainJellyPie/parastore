import type { ReactNode } from "react";

import { LayoutTabs } from "@/features/layouts/components/LayoutTabs";
import type { Layout } from "@/features/layouts/hooks/useLayouts";

export interface ProjectShellProps {
  layouts: Layout[];
  selectedLayoutId: string | null;
  onLayoutSelect: (id: string) => void;
  onAddLayout: () => void;
  centerSlot: ReactNode;
  sidePanelSlot: ReactNode;
  navigationDisabled?: boolean;
}

export function ProjectShell({
  layouts,
  selectedLayoutId,
  onLayoutSelect,
  onAddLayout,
  centerSlot,
  sidePanelSlot,
  navigationDisabled = false,
}: ProjectShellProps) {
  return (
    <>
      <div className="relative flex-1">
        {layouts.length > 0 && (
          <div className="pointer-events-auto absolute left-3 top-3 z-10">
            <LayoutTabs
              layouts={layouts}
              selectedId={selectedLayoutId ?? undefined}
              onSelect={onLayoutSelect}
              onAddNew={onAddLayout}
              disabled={navigationDisabled}
            />
          </div>
        )}
        {centerSlot}
      </div>
      {sidePanelSlot}
    </>
  );
}
