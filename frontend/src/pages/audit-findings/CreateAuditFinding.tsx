import { useNavigate } from "react-router-dom";
import { AxiosError } from "axios";

import AppLayout from "@/layouts/AppLayout";

import AuditFindingForm from "@/components/audit-findings/AuditFindingForm";

import { useCreateAuditFinding } from "@/hooks/useCreateAuditFinding";

import type {
  CreateAuditFindingRequest,
} from "@/api/auditFindings";

export default function CreateAuditFinding() {

  const navigate = useNavigate();

  const createMutation =
    useCreateAuditFinding();


  async function handleSubmit(
    data: CreateAuditFindingRequest
  ) {

    try {

      await createMutation.mutateAsync(
        data
      );

      navigate("/audit-findings");

    } catch (error: unknown) {

      const axiosError =
        error instanceof AxiosError
          ? error
          : null;

      const detail =
        axiosError?.response?.data?.detail;

      const message =
        typeof detail === "string"
          ? detail
          : "Failed to create audit finding.";

      alert(message);

    }

  }


  return (

    <AppLayout>

      <div className="mx-auto max-w-3xl">

        <div className="mb-8">

          <h1 className="text-3xl font-bold">
            Create Audit Finding
          </h1>

          <p className="mt-1 text-slate-500">
            Create a new finding from an audit.
          </p>

        </div>


        <AuditFindingForm
          mode="create"
          onSubmit={handleSubmit}
          isSubmitting={
            createMutation.isPending
          }
          onCancel={() =>
            navigate(
              "/audit-findings"
            )
          }
        />

      </div>

    </AppLayout>

  );

}