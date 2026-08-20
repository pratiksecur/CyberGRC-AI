import { useNavigate, useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import CorrectiveActionForm from "@/components/corrective-actions/CorrectiveActionForm";

import { useCorrectiveAction } from "@/hooks/useCorrectiveAction";
import { useUpdateCorrectiveAction } from "@/hooks/useUpdateCorrectiveAction";

import type {
  CreateCorrectiveActionRequest,
} from "@/api/correctiveActions";

export default function EditCorrectiveAction() {
  const { id } = useParams();

  const navigate = useNavigate();

  const actionId = Number(id);

  const {
    data,
    isLoading,
    error,
  } = useCorrectiveAction(
    actionId
  );

  const updateMutation =
    useUpdateCorrectiveAction();

  async function handleSubmit(
    formData: CreateCorrectiveActionRequest
  ) {
    try {
      await updateMutation.mutateAsync({
        id: actionId,
        data: formData,
      });

      navigate(
        `/corrective-actions/${actionId}`
      );
    } catch {
      alert(
        "Failed to update corrective action."
      );
    }
  }

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading Corrective Action...
        </div>
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="p-10 text-center text-red-500">
          Corrective action not found.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="mx-auto max-w-3xl space-y-6">

        <div>
          <h1 className="text-3xl font-bold text-slate-900">
            Edit Corrective Action
          </h1>

          <p className="mt-1 text-slate-500">
            Update the remediation activity and its current status.
          </p>
        </div>

        <CorrectiveActionForm
          initialData={data}
          onSubmit={handleSubmit}
          onCancel={() =>
            navigate(
              `/corrective-actions/${actionId}`
            )
          }
          isSubmitting={
            updateMutation.isPending
          }
          submitLabel="Save Changes"
        />

      </div>
    </AppLayout>
  );
}