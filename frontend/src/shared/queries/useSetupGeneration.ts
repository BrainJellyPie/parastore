import { useEffect, useRef, useState } from "react";
import { useQueryClient } from "@tanstack/react-query";
import {
  getGenerationStatus,
  getSetupGenerations,
  regeneratePersona,
} from "@/shared/api/client";
import type { GenerationKind, GenerationStatus } from "@/shared/types/domain";
import { queryKeys } from "@/shared/queries/keys";

const POLL_INTERVAL_MS = 3000;

export type SetupGenerationPhase = "idle" | "layout" | "persona" | "completed" | "failed";

export interface SetupGenerationState {
  phase: SetupGenerationPhase;
  // Populated in every phase except "idle"; preserved when restoring a failed gen.
  kind: GenerationKind | null;
  currentGenId: string | null;
  error: string | null;          // only populated when phase === "failed"
  retry: () => void;             // persona retry only; throws if called on a failed layout gen
  retrying: boolean;
}

function phaseFromStatus(s: GenerationStatus): SetupGenerationPhase {
  if (s.status === "failed") return "failed";
  if (s.status === "completed") {
    if (s.kind === "persona") return "completed";
    // layout completed → caller advances to persona polling using next_gen_id
    return "layout";
  }
  return s.kind;
}

export function useSetupGeneration(
  projectId: string,
  setupId: string,
  initialGenId?: string | null,
): SetupGenerationState {
  const qc = useQueryClient();
  const [phase, setPhase] = useState<SetupGenerationPhase>("idle");
  const [kind, setKind] = useState<GenerationKind | null>(null);
  const [currentGenId, setCurrentGenId] = useState<string | null>(initialGenId ?? null);
  const [error, setError] = useState<string | null>(null);
  const [retrying, setRetrying] = useState(false);

  // On mount, query the latest generation with active_only=false so we can
  // restore failed gens. initialGenId from props takes precedence.
  const bootstrappedRef = useRef(false);

  useEffect(() => {
    bootstrappedRef.current = false;
  }, [projectId, setupId]);

  useEffect(() => {
    if (bootstrappedRef.current) return;
    if (initialGenId) {
      bootstrappedRef.current = true;
      setCurrentGenId(initialGenId);
      return;
    }
    let cancelled = false;
    void (async () => {
      try {
        const list = await getSetupGenerations(projectId, setupId, { active_only: false });
        if (cancelled) return;
        bootstrappedRef.current = true;
        const latest = list[0];
        if (!latest) {
          setPhase("idle");
          return;
        }
        setKind(latest.kind);
        setCurrentGenId(latest.gen_id);
        if (latest.status === "failed") {
          setPhase("failed");
          setError(latest.error ?? "Generation failed");
          return;
        }
        if (latest.status === "completed") {
          if (latest.kind === "layout" && latest.progress?.next_gen_id) {
            setCurrentGenId(latest.progress.next_gen_id);
            setKind("persona");
            setPhase("persona");
          } else if (latest.kind === "persona") {
            setPhase("completed");
            qc.invalidateQueries({ queryKey: queryKeys.project(projectId) });
            qc.invalidateQueries({ queryKey: queryKeys.setup(projectId, setupId) });
          } else {
            // layout completed but no next_gen — auto-chain was skipped, fall back to idle
            setPhase("idle");
          }
          return;
        }
        setPhase(latest.kind);
      } catch (e) {
        if (cancelled) return;
        setPhase("failed");
        setError(e instanceof Error ? e.message : String(e));
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [projectId, setupId, initialGenId, qc]);

  useEffect(() => {
    if (!currentGenId) return;
    if (phase !== "layout" && phase !== "persona") return;
    let cancelled = false;
    let timer: ReturnType<typeof setTimeout> | null = null;

    const tick = async () => {
      try {
        const s = await getGenerationStatus(projectId, setupId, currentGenId);
        if (cancelled) return;
        setKind(s.kind);
        if (s.status === "failed") {
          setPhase("failed");
          setError(s.error ?? "Generation failed");
          return;
        }
        if (s.status === "completed") {
          if (s.kind === "layout" && s.progress?.next_gen_id) {
            setCurrentGenId(s.progress.next_gen_id);
            setKind("persona");
            setPhase("persona");
            return;
          }
          if (s.kind === "persona") {
            setPhase("completed");
            qc.invalidateQueries({ queryKey: queryKeys.project(projectId) });
            qc.invalidateQueries({ queryKey: queryKeys.setup(projectId, setupId) });
            return;
          }
          // layout completed without next_gen (race or skipped chain): fall back
          // to idle so the readiness/race reconciliation effect can decide.
          setPhase("idle");
          return;
        }
        setPhase(phaseFromStatus(s));
        timer = setTimeout(() => void tick(), POLL_INTERVAL_MS);
      } catch (e) {
        if (cancelled) return;
        setPhase("failed");
        setError(e instanceof Error ? e.message : String(e));
      }
    };
    void tick();

    return () => {
      cancelled = true;
      if (timer) clearTimeout(timer);
    };
  }, [projectId, setupId, currentGenId, phase, qc]);

  const retry = () => {
    if (kind === "layout" && phase === "failed") {
      throw new Error("Layout regeneration is not supported — please create a new project");
    }
    setRetrying(true);
    setError(null);
    void (async () => {
      try {
        const { gen_id } = await regeneratePersona(projectId, setupId);
        setCurrentGenId(gen_id);
        setKind("persona");
        setPhase("persona");
      } catch (e) {
        setPhase("failed");
        setError(e instanceof Error ? e.message : String(e));
      } finally {
        setRetrying(false);
      }
    })();
  };

  return { phase, kind, currentGenId, error, retry, retrying };
}
