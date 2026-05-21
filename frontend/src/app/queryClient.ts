import { QueryClient } from "@tanstack/react-query";

// Run data is immutable (same runId always yields the same result); project/setup are manually invalidated on mutation.
// Retry on network failure is capped at 1 — surface backend failures fast.
export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: 1,
      refetchOnWindowFocus: false,
      staleTime: 1000 * 60, // 1 minute
    },
    mutations: {
      retry: 0,
    },
  },
});
