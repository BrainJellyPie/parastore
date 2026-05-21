import { createFileRoute, useNavigate } from "@tanstack/react-router";

import { CreateStoreWizard } from "@/features/setup/components/CreateStoreWizard";

export const Route = createFileRoute("/projects/new")({
  component: NewProjectPage,
});

function NewProjectPage() {
  const navigate = useNavigate();
  return (
    <CreateStoreWizard
      onCreated={(pid) =>
        navigate({ to: "/projects/$pid", params: { pid }, replace: true })
      }
    />
  );
}
