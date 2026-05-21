import { Loader2 } from "lucide-react";

interface Props {
  label?: string;
}

export function LoadingView({ label = "Loading…" }: Props) {
  return (
    <div className="flex h-full w-full flex-1 items-center justify-center gap-2">
      <Loader2 className="size-4 animate-spin text-muted-foreground" />
      <div className="text-xs text-muted-foreground">{label}</div>
    </div>
  );
}
