import { Loader2, AlertCircle, RefreshCw } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import type { SetupGenerationState } from "@/shared/queries/useSetupGeneration";

interface Props {
  generation: SetupGenerationState;
  contextKind: "layout" | "persona";
  // Invoked on layout failure. Caller is responsible for deleting the project
  // and navigating to /projects/new.
  onAbandonProject: () => void;
}

export function PreparingView({ generation, contextKind, onAbandonProject }: Props) {
  const { phase, kind, error, retry, retrying } = generation;

  const isLayoutFailed =
    phase === "failed" && (kind === "layout" || contextKind === "layout");
  if (isLayoutFailed) {
    return (
      <div className="flex flex-1 items-center justify-center p-8">
        <div className="max-w-md space-y-4 rounded-lg border border-destructive/40 bg-destructive/5 p-6 text-center">
          <AlertCircle className="mx-auto size-8 text-destructive" />
          <div className="space-y-1">
            <h2 className="text-lg font-semibold text-destructive">Layout analysis failed</h2>
            <p className="text-sm text-muted-foreground">
              {error || "An error occurred during layout analysis."}
            </p>
            <p className="text-xs text-muted-foreground">
              Layout regeneration is not supported — please create a new project.
            </p>
          </div>
          <Button variant="outline" onClick={onAbandonProject}>
            Start over
          </Button>
        </div>
      </div>
    );
  }

  if (phase === "failed") {
    return (
      <div className="flex flex-1 items-center justify-center p-8">
        <div className="max-w-md space-y-4 rounded-lg border border-destructive/40 bg-destructive/5 p-6 text-center">
          <AlertCircle className="mx-auto size-8 text-destructive" />
          <div className="space-y-1">
            <h2 className="text-lg font-semibold text-destructive">Persona generation failed</h2>
            <p className="text-sm text-muted-foreground">
              {error || "An error occurred during persona generation."}
            </p>
          </div>
          <Button onClick={retry} disabled={retrying}>
            <RefreshCw className={retrying ? "mr-2 size-4 animate-spin" : "mr-2 size-4"} />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  // Edge case: idle + persona context (no_personas, no generation history — e.g.
  // server hard-stop). Per spec table #5, show a generic "retry" button with no error message.
  if (phase === "idle" && contextKind === "persona") {
    return (
      <div className="flex flex-1 items-center justify-center p-8">
        <div className="max-w-md space-y-4 rounded-lg border bg-muted/40 p-6 text-center">
          <div className="space-y-1">
            <h2 className="text-base font-semibold">Personas have not been generated yet</h2>
            <p className="text-xs text-muted-foreground">
              Click "Retry" to generate personas.
            </p>
          </div>
          <Button onClick={retry} disabled={retrying}>
            <RefreshCw className={retrying ? "mr-2 size-4 animate-spin" : "mr-2 size-4"} />
            Retry
          </Button>
        </div>
      </div>
    );
  }

  const isPersonaPhase = phase === "persona";
  const label =
    phase === "layout" ? "Analyzing layout…"
    : phase === "persona" ? "Generating personas…"
    : contextKind === "layout" ? "Preparing layout analysis…"
    : "Preparing persona generation…";

  return (
    <div className="flex flex-1 items-center justify-center p-8">
      <div className="flex flex-col items-center gap-3 text-muted-foreground">
        <Loader2 className={isPersonaPhase ? "size-20 animate-spin" : "size-8 animate-spin"} />
        {isPersonaPhase && (
          <p className="text-base font-medium text-foreground">Generating synthetic consumers…</p>
        )}
        <p className="text-sm">{label}</p>
      </div>
    </div>
  );
}
