import { abortableDelay } from "@/shared/utils/abortableDelay";

export type JobStatus = "pending" | "running" | "completed" | "failed";

export interface JobStatusResponse<TResult> {
  status: JobStatus;
  result?: TResult;
}

const JOB_POLL_INTERVAL = 2000;

export async function pollJob<TResult>(
  getStatus: (signal?: AbortSignal) => Promise<JobStatusResponse<TResult>>,
  signal?: AbortSignal,
): Promise<TResult> {
  while (!signal?.aborted) {
    const res = await getStatus(signal);
    if (signal?.aborted) break;
    if (res.status === "completed" && res.result !== undefined) return res.result;
    if (res.status === "failed") throw new Error("Job failed");
    await abortableDelay(JOB_POLL_INTERVAL, signal);
  }
  throw new Error("Job was aborted");
}
