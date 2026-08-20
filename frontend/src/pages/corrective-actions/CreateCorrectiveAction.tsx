import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import CorrectiveActionForm from "@/components/corrective-actions/CorrectiveActionForm";

import { useCreateCorrectiveAction } from "@/hooks/useCreateCorrectiveAction";

import type {
  CreateCorrectiveActionRequest,
} from "@/api/correctiveActions";

export default function CreateCorrectiveAction() {
  const navigate = useNavigate();

  const createMutation =
    useCreateCorrectiveAction();

  async function handleSubmit(
    data: CreateCorrectiveActionRequest
  ) {
    try {
      await createMutation.mutateAsync(
        data
      );

      navigate("/corrective-actions");
    } catch {
      alert(
        "Failed to create corrective action."
      );
    }
  }

  return (
    <AppLayout>
      <div className="mx-auto max-w-3xl space-y-6">

        <div>
          <h1 className="text-3xl font-bold text-slate-900">
            Create Corrective Action
          </h1>

          <p className="mt-1 text-slate-500">
            Create a remediation action for an audit finding.
          </p>
        </div>

        <CorrectiveActionForm
          onSubmit={handleSubmit}
          onCancel={() =>
            navigate("/corrective-actions")
          }
          isSubmitting={
            createMutation.isPending
          }
          submitLabel="Create Action"
        />

      </div>
    </AppLayout>
  );
}