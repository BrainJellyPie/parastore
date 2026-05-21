import { createRootRoute, Outlet } from "@tanstack/react-router";
import { Suspense } from "react";
import { AppHeader } from "@/app/AppHeader";
import { LoadingView } from "@/shared/components/LoadingView";
import { RouteErrorBoundary } from "@/app/providers/RouteErrorBoundary";

export const Route = createRootRoute({
  component: RootLayout,
});

function RootLayout() {
  return (
    <div className="flex h-screen w-screen flex-col bg-background">
      <AppHeader />
      <main className="flex flex-1 overflow-hidden">
        <RouteErrorBoundary>
          <Suspense fallback={<LoadingView />}>
            <Outlet />
          </Suspense>
        </RouteErrorBoundary>
      </main>
    </div>
  );
}
