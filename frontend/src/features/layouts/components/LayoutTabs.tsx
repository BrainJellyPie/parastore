// Layout switching/adding must work in every mode (ready/running/playback). Each
// layout has its own simulation history, so navigation cannot be gated on the
// current mode. `disabled` is reserved for ProjectShell.navigationDisabled and
// blocks both the tabs and the Add button together.

import { Plus } from "lucide-react";

import { Button } from "@/shared/components/ui/button";

import type { Layout } from "../hooks/useLayouts";

export interface LayoutTabsProps {
  layouts: Layout[];
  selectedId: string | undefined;
  onSelect: (id: string) => void;
  onAddNew: () => void;
  disabled?: boolean;
}

export function LayoutTabs({
  layouts,
  selectedId,
  onSelect,
  onAddNew,
  disabled = false,
}: LayoutTabsProps) {
  return (
    <div
      className="flex items-center gap-1.5"
      role="tablist"
      aria-label="Layouts"
    >
      {layouts.map((layout) => {
        const selected = layout.id === selectedId;
        return (
          <Button
            key={layout.id}
            type="button"
            role="tab"
            aria-selected={selected}
            variant={selected ? "default" : "outline"}
            size="sm"
            disabled={disabled}
            onClick={() => onSelect(layout.id)}
          >
            {layout.name}
          </Button>
        );
      })}
      <Button
        type="button"
        variant="outline"
        size="sm"
        disabled={disabled}
        onClick={onAddNew}
      >
        <Plus aria-hidden />
        Add new
      </Button>
    </div>
  );
}
