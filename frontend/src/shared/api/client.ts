// Response types mirror backend schemas.py 1:1 — keep in sync.

import type {
  Store,
  Persona,
  DaySchedule,
  CustomerResult,
  Readiness,
  GenerationStatus,
  GenerationListItem,
  SlotRow,
  BlockedFaceInfo,
  BlockedFaceDetail,
  ClearedSlotInfo,
  Issue,
} from "@/shared/types/domain";

export type { BlockedFaceDetail, Issue } from "@/shared/types/domain";

export const BASE = import.meta.env.VITE_API_URL ?? "http://localhost:8000";

async function fetchJson<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json" },
    ...init,
  });
  if (!res.ok) {
    const body = await res.text().catch(() => "");
    throw new Error(`${res.status} ${res.statusText}: ${body}`);
  }
  return res.json() as Promise<T>;
}

export interface ProjectListItem {
  project_id: string;
  name: string;
  description: string;
  store_type: string;
  grid_size: [number, number] | null;
  weekly_schedule: DaySchedule[];
  created_at: string;
  updated_at: string;
  status: string;
}

export interface ProjectMetadata {
  project_id: string;
  name: string;
  description: string;
  store_type: string;
  grid_size: [number, number] | null;
  weekly_schedule: DaySchedule[];
  address: string;
  customer_profile: string;
  supplemental_summary: string;
  created_at: string;
  updated_at: string;
}

export interface ProjectDetail {
  projectId: string;
  metadata: ProjectMetadata;
  personas: Persona[];
  state: { activeSetupId: string; runningSetups: string[] };
  setups: SetupSummary[];
  personasLocked: boolean;
}

export function getProjects(signal?: AbortSignal): Promise<ProjectListItem[]> {
  return fetchJson("/api/projects", { signal });
}

export function getProject(projectId: string, signal?: AbortSignal): Promise<ProjectDetail> {
  return fetchJson(`/api/projects/${projectId}`, { signal });
}

export function deleteProject(projectId: string, signal?: AbortSignal): Promise<{ status: string }> {
  return fetchJson(`/api/projects/${projectId}`, { method: "DELETE", signal });
}

export function updateProjectMetadata(
  projectId: string,
  patch: { name?: string; description?: string; address?: string; customer_profile?: string; supplemental_summary?: string },
  signal?: AbortSignal,
): Promise<{ status: "saved" }> {
  return fetchJson(`/api/projects/${projectId}/metadata`, {
    method: "PUT",
    body: JSON.stringify(patch),
    signal,
  });
}

export interface SetupSummaryShort {
  id: string;
  name: string;
  status: "draft" | "running" | "locked";
  parentId: string | null;
  runId: string | null;
  memo: string;
  readiness: Readiness | null;
  created_at: string;
  updated_at: string;
}

export interface CreateStoreMeta {
  name: string;
  description: string;
  address: string;
  store_type: string;
  customer_profile: string;
  weekly_schedule: ReadonlyArray<{
    day: number;
    is_open: boolean;
    open_hour: number;
    close_hour: number;
  }>;
}

export interface CreateStoreResponse {
  metadata: ProjectMetadata;
  setup: SetupSummaryShort;
  personaGenId: string;
}

export async function createStore(
  meta: CreateStoreMeta,
  supplemental: File | null,
): Promise<CreateStoreResponse> {
  const fd = new FormData();
  fd.append("meta", JSON.stringify(meta));
  if (supplemental) fd.append("supplemental", supplemental);

  // Direct base URL — Vite has no /api proxy, so a relative path would hit the dev server.
  const res = await fetch(`${BASE}/api/projects/create-store`, { method: "POST", body: fd });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(text || `Failed to create store (HTTP ${res.status})`);
  }
  return res.json() as Promise<CreateStoreResponse>;
}

export interface SetupSummary {
  id: string;
  name: string;
  status: string;
  parentId: string | null;
  runId: string | null;
  memo: string;
  readiness: Readiness | null;
  created_at: string;
  updated_at: string;
}

export interface SetupDetail extends SetupSummary {
  store: Store | null;
  blocked_faces?: BlockedFaceDetail[];
}

export function getSetups(projectId: string, signal?: AbortSignal): Promise<SetupSummary[]> {
  return fetchJson(`/api/projects/${projectId}/setups`, { signal });
}

export function getSetup(
  projectId: string,
  setupId: string,
  signal?: AbortSignal,
): Promise<SetupDetail> {
  return fetchJson(`/api/projects/${projectId}/setups/${setupId}`, { signal });
}

export interface SaveSetupResponse {
  setup: SetupSummary;
  cleared: ClearedSlotInfo[];
  blocked_faces: BlockedFaceDetail[];
  issues: Issue[];
}

export function saveSetup(
  projectId: string,
  setupId: string,
  data: { store?: Store; name?: string; memo?: string },
  signal?: AbortSignal,
): Promise<SaveSetupResponse> {
  // backend expects nested { setup: ... } body
  return fetchJson(`/api/projects/${projectId}/setups/${setupId}`, {
    method: "PUT",
    body: JSON.stringify({ setup: data }),
    signal,
  });
}

export function createSetup(
  projectId: string,
  body: {
    mode: "racks_and_items" | "racks" | "empty";
    source_setup_id: string | null;
    name?: string;
    memo?: string;
  },
  signal?: AbortSignal,
): Promise<SetupSummaryShort> {
  return fetchJson(`/api/projects/${projectId}/setups`, {
    method: "POST",
    body: JSON.stringify(body),
    signal,
  });
}

export function deleteSetup(
  projectId: string,
  setupId: string,
  signal?: AbortSignal,
): Promise<{ status: string; deleted: string[] }> {
  return fetchJson(`/api/projects/${projectId}/setups/${setupId}`, {
    method: "DELETE",
    signal,
  });
}

export interface ReplaceSlotsResponse {
  count: number;
  cleared: ClearedSlotInfo[];
}

export function replaceSlots(
  projectId: string,
  setupId: string,
  slots: SlotRow[],
  signal?: AbortSignal,
): Promise<ReplaceSlotsResponse> {
  return fetchJson(`/api/projects/${projectId}/setups/${setupId}/slots`, {
    method: "PUT",
    body: JSON.stringify({ slots }),
    signal,
  });
}

export function getSetupGenerations(
  projectId: string,
  setupId: string,
  opts?: { active_only?: boolean },
  signal?: AbortSignal,
): Promise<GenerationListItem[]> {
  const query = opts?.active_only ? "?active_only=true" : "";
  return fetchJson(
    `/api/projects/${projectId}/setups/${setupId}/generations${query}`,
    { signal },
  );
}

export function getGenerationStatus(
  projectId: string,
  setupId: string,
  genId: string,
  signal?: AbortSignal,
): Promise<GenerationStatus> {
  return fetchJson(
    `/api/projects/${projectId}/setups/${setupId}/generations/${genId}/status`,
    { signal },
  );
}

export function regeneratePersona(
  projectId: string,
  setupId: string,
  signal?: AbortSignal,
): Promise<{ gen_id: string }> {
  return fetchJson(
    `/api/projects/${projectId}/setups/${setupId}/regenerate-persona`,
    { method: "POST", signal },
  );
}

export function getBlockedFaces(store: Store, signal?: AbortSignal): Promise<BlockedFaceInfo[]> {
  return fetchJson(`/api/util/blocked-faces`, {
    method: "POST",
    body: JSON.stringify({ store }),
    signal,
  });
}

export function savePersonas(
  projectId: string,
  personas: Persona[],
  signal?: AbortSignal,
): Promise<{ status: string }> {
  return fetchJson(`/api/projects/${projectId}/personas`, {
    method: "PUT",
    body: JSON.stringify({ personas }),
    signal,
  });
}

export interface RunListItem {
  run_id: string;
  project_id: string;
  setup_id: string;
  status: string;
  created_at: string;
  total_customers: number;
}

export function getRuns(
  projectId: string,
  setupId?: string,
  signal?: AbortSignal,
): Promise<RunListItem[]> {
  const query = setupId ? `?setup_id=${setupId}` : "";
  return fetchJson(`/api/projects/${projectId}/runs${query}`, { signal });
}

export function startRun(
  projectId: string,
  setupId: string,
  signal?: AbortSignal,
): Promise<{ project_id: string; run_id: string; setup_id: string }> {
  return fetchJson(`/api/projects/${projectId}/runs`, {
    method: "POST",
    body: JSON.stringify({ setup_id: setupId }),
    signal,
  });
}

export function getRunStatus(
  projectId: string,
  runId: string,
  signal?: AbortSignal,
): Promise<{ status: string; error: string; total_customers: number }> {
  return fetchJson(`/api/projects/${projectId}/runs/${runId}/status`, { signal });
}

export function getRunTimeline(
  projectId: string,
  runId: string,
  signal?: AbortSignal,
): Promise<CustomerResult[]> {
  return fetchJson(`/api/projects/${projectId}/runs/${runId}/timeline`, { signal });
}

export interface RunSummary {
  total_customers: number;
  total_revenue: number;
  top_products: string[];
  by_purpose: Record<string, number>;
  by_identity: Record<string, number>;
  by_age: Record<string, number>;
  by_gender: Record<string, number>;
}

export function getRunSummary(
  projectId: string,
  runId: string,
  signal?: AbortSignal,
): Promise<{
  summary: RunSummary;
  personas: Record<string, Persona>;
}> {
  return fetchJson(`/api/projects/${projectId}/runs/${runId}/summary`, { signal });
}

export function getRunHeatmap(
  projectId: string,
  runId: string,
  signal?: AbortSignal,
): Promise<{
  pathcalc_heatmap: number[][];
  persona_heatmap: number[][];
}> {
  return fetchJson(`/api/projects/${projectId}/runs/${runId}/heatmap`, { signal });
}

export function getRunStore(
  projectId: string,
  runId: string,
  signal?: AbortSignal,
): Promise<Store> {
  return fetchJson(`/api/projects/${projectId}/runs/${runId}/store`, { signal });
}
