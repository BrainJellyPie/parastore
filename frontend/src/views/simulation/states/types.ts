import type { Layout } from "@/features/layouts/hooks/useLayouts";
import type { SetupDetail } from "@/shared/api/client";
import type { Persona, Store } from "@/shared/types/domain";

export interface LayoutTabProps {
  layouts: Layout[];
  selectedSetupId: string;
  onLayoutSelect: (id: string) => void;
  onAddLayout: () => void;
}

export interface ViewCommon {
  pid: string;
  setup: SetupDetail & { store: Store };
  personas: Persona[];
  location: string;
}
