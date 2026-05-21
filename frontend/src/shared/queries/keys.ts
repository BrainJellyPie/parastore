// Array-shaped keys so invalidateQueries can match by prefix
// (e.g. invalidating queryKeys.project(pid) invalidates everything under that project).
export const queryKeys = {
  projects: () => ["projects"] as const,
  project: (projectId: string) => ["projects", projectId] as const,
  setups: (projectId: string) => ["projects", projectId, "setups"] as const,
  setup: (projectId: string, setupId: string) =>
    ["projects", projectId, "setups", setupId] as const,
  runs: (projectId: string, setupId: string) =>
    ["projects", projectId, "setups", setupId, "runs"] as const,
  run: (projectId: string, runId: string) =>
    ["projects", projectId, "runs", runId] as const,
  runStatus: (projectId: string, runId: string) =>
    ["projects", projectId, "runs", runId, "status"] as const,
};
