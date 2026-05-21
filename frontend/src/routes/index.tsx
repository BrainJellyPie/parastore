import { createFileRoute, useNavigate } from "@tanstack/react-router";
import { Plus, MapPin, LayoutGrid, CalendarDays } from "lucide-react";
import { Button } from "@/shared/components/ui/button";
import { Skeleton } from "@/shared/components/ui/skeleton";
import { useProjects } from "@/shared/queries/useProjects";
import type { ProjectListItem } from "@/shared/api/client";

export const Route = createFileRoute("/")({
  component: ProjectListPage,
});

const BADGE_COLORS: Record<string, string> = {
  "Setting up": "bg-yellow-100 text-yellow-800",
  "Ready": "bg-blue-100 text-blue-800",
  "Simulated": "bg-green-100 text-green-800",
};

const STORE_TYPE_LABELS: Record<string, string> = {
  convenience: "Convenience store",
  cafe: "Café",
  bakery: "Bakery",
  supermarket: "Supermarket",
  cosmetics: "Cosmetics",
  clothing: "Clothing",
  electronics: "Electronics",
  pharmacy: "Pharmacy",
};

function ProjectCard({ project, onClick }: { project: ProjectListItem; onClick: () => void }) {
  const badgeClass = BADGE_COLORS[project.status] ?? "bg-muted text-muted-foreground";
  const typeLabel = STORE_TYPE_LABELS[project.store_type] ?? project.store_type;
  const simDays = project.weekly_schedule?.filter((d) => d.is_open).length ?? 0;

  return (
    <button
      type="button"
      onClick={onClick}
      className="flex flex-col gap-2 rounded-lg border bg-background p-5 text-left transition-shadow hover:shadow-md"
    >
      <div className="flex items-start justify-between gap-2">
        <h3 className="text-sm font-semibold">{project.name || "Untitled"}</h3>
        <span className={`shrink-0 rounded-full px-2 py-0.5 text-[10px] font-medium ${badgeClass}`}>
          {project.status}
        </span>
      </div>
      {project.description && (
        <p className="line-clamp-2 text-xs text-muted-foreground">{project.description}</p>
      )}
      <div className="mt-auto flex items-center gap-3 text-xs text-muted-foreground">
        <span className="flex items-center gap-1">
          <MapPin className="size-3" />
          {typeLabel}
        </span>
        {project.grid_size && (
          <span className="flex items-center gap-1">
            <LayoutGrid className="size-3" />
            {project.grid_size[0]}x{project.grid_size[1]}
          </span>
        )}
        {simDays > 0 && (
          <span className="flex items-center gap-1">
            <CalendarDays className="size-3" />
            {simDays}d
          </span>
        )}
      </div>
    </button>
  );
}

function SkeletonCard() {
  return (
    <div className="flex flex-col gap-3 rounded-lg border bg-background p-5">
      <Skeleton className="h-4 w-3/4" />
      <Skeleton className="h-3 w-full" />
      <Skeleton className="h-3 w-1/2" />
      <div className="mt-auto flex gap-3">
        <Skeleton className="h-3 w-16" />
        <Skeleton className="h-3 w-20" />
      </div>
    </div>
  );
}

function ProjectListPage() {
  const navigate = useNavigate();
  const { data: projects, isLoading, error, refetch } = useProjects();

  return (
    <div className="flex-1 overflow-y-auto bg-muted/30 p-8">
      <div className="mx-auto max-w-4xl">
        <div className="mb-6 flex items-center justify-between">
          <div>
            <h1 className="text-lg font-semibold">Projects</h1>
            <p className="text-xs text-muted-foreground">Store simulation projects</p>
          </div>
          <Button
            size="sm"
            className="gap-1"
            onClick={() => navigate({ to: "/projects/new" })}
          >
            <Plus className="size-3.5" />
            New project
          </Button>
        </div>

        {error && (
          <div className="mb-4 rounded-md border border-destructive/50 bg-destructive/10 p-4 text-sm text-destructive">
            {error instanceof Error ? error.message : "Could not load projects"}
            <button type="button" onClick={() => refetch()} className="ml-2 underline">
              Retry
            </button>
          </div>
        )}

        {isLoading ? (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {Array.from({ length: 6 }).map((_, i) => <SkeletonCard key={i} />)}
          </div>
        ) : !projects || projects.length === 0 ? (
          <div className="flex flex-col items-center justify-center gap-3 rounded-lg border border-dashed py-16">
            <p className="text-sm text-muted-foreground">No projects yet</p>
            <Button
              size="sm"
              variant="outline"
              className="gap-1"
              onClick={() => navigate({ to: "/projects/new" })}
            >
              <Plus className="size-3.5" />
              Create your first project
            </Button>
          </div>
        ) : (
          <div className="grid grid-cols-1 gap-4 sm:grid-cols-2 lg:grid-cols-3">
            {projects.map((p) => (
              <ProjectCard
                key={p.project_id}
                project={p}
                onClick={() => navigate({ to: "/projects/$pid", params: { pid: p.project_id } })}
              />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
