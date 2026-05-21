import { useMemo } from "react";
import type { Persona } from "@/shared/types/domain";

export function usePersonaData(personas: Persona[]): {
  personaNames: Map<string, string>;
  personaGenders: Map<string, string>;
} {
  const personaNames = useMemo(() => {
    const map = new Map<string, string>();
    for (const p of personas) map.set(p.id, p.identity);
    return map;
  }, [personas]);

  const personaGenders = useMemo(() => {
    const map = new Map<string, string>();
    for (const p of personas) map.set(p.id, p.gender);
    return map;
  }, [personas]);

  return { personaNames, personaGenders };
}
