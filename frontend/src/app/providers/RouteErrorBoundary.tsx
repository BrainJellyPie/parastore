import type { ReactNode } from "react";
import { ErrorBoundary, type FallbackProps } from "react-error-boundary";
import { useQueryErrorResetBoundary } from "@tanstack/react-query";
import { useNavigate } from "@tanstack/react-router";
import { Button } from "@/shared/components/ui/button";

function Fallback({ error, resetErrorBoundary }: FallbackProps) {
  const navigate = useNavigate();
  return (
    <div className="flex h-full flex-1 items-center justify-center">
      <div className="max-w-md space-y-3 text-center">
        <div className="text-sm font-medium text-destructive">Something went wrong</div>
        <div className="text-xs text-muted-foreground">
          {error instanceof Error ? error.message : String(error)}
        </div>
        <div className="flex justify-center gap-2">
          <Button
            variant="outline"
            size="sm"
            onClick={() => {
              // navigate alone does not clear the ErrorBoundary's hasError, so the Fallback keeps showing.
              // resetErrorBoundary must be called too so the next route's children tree mounts.
              resetErrorBoundary();
              void navigate({ to: "/" });
            }}
          >
            Back to list
          </Button>
          <Button variant="outline" size="sm" onClick={resetErrorBoundary}>
            Retry
          </Button>
        </div>
      </div>
    </div>
  );
}

export function RouteErrorBoundary({ children }: { children: ReactNode }) {
  const { reset } = useQueryErrorResetBoundary();
  return (
    <ErrorBoundary FallbackComponent={Fallback} onReset={reset}>
      {children}
    </ErrorBoundary>
  );
}
