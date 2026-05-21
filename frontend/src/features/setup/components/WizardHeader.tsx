import { cn } from "@/shared/utils/cn";

interface WizardHeaderProps {
  title: string;
  steps: ReadonlyArray<{ index: number; label: string }>;
  activeIndex: number;
}

export function WizardHeader({ title, steps, activeIndex }: WizardHeaderProps) {
  return (
    <div className="space-y-6">
      <h1 className="text-2xl font-semibold">{title}</h1>
      <div className="flex border-b">
        {steps.map((s) => {
          const active = s.index === activeIndex;
          return (
            <div
              key={s.index}
              className={cn(
                "flex-1 pb-3 text-base",
                active ? "border-b-2 border-foreground font-semibold" : "text-muted-foreground",
              )}
            >
              {s.index}. {s.label}
            </div>
          );
        })}
      </div>
    </div>
  );
}
