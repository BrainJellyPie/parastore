import { Package, Users, Loader2, DoorOpen, DoorClosed, ScanLine, type LucideIcon } from "lucide-react";
import type { Readiness, ReadinessReason } from "@/shared/types/domain";

export interface Availability {
  canSimulate: boolean;
  reasons: ReadinessReason[];
}

export function computeSimulationAvailability(readiness: Readiness | null): Availability {
  if (!readiness) return { canSimulate: false, reasons: [] };
  return { canSimulate: readiness.ready, reasons: readiness.reasons };
}

export function reasonLabel(reason: ReadinessReason): string {
  switch (reason) {
    case "no_personas": return "Personas have not been generated yet";
    case "no_items": return "No products placed on shelves";
    case "no_layout": return "Store layout is not set up yet";
    case "layout_pending": return "Layout analysis is in progress";
    case "personas_pending": return "Persona generation is in progress";
    case "no_entrance": return "Place at least one entrance";
    case "no_exit": return "Place at least one exit";
    case "no_counter": return "Place at least one checkout counter";
  }
}

export function reasonIcon(reason: ReadinessReason): LucideIcon {
  switch (reason) {
    case "no_personas":
    case "personas_pending":
      return Users;
    case "no_items":
      return Package;
    case "no_layout":
    case "layout_pending":
      return Loader2;
    case "no_entrance":
      return DoorOpen;
    case "no_exit":
      return DoorClosed;
    case "no_counter":
      return ScanLine;
  }
}
