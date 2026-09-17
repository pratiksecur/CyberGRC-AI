import { useNavigate, useParams } from "react-router-dom";

import { AxiosError } from "axios";

import AppLayout from "@/layouts/AppLayout";

import AuditFindingForm from "@/components/audit-findings/AuditFindingForm";

import { useAuditFinding } from "@/hooks/useAuditFinding";

import { useUpdateAuditFinding } from "@/hooks/useUpdateAuditFinding";

import type {
  CreateAuditFindingRequest,
} from "@/api/auditFindings";

export default function EditAuditFinding() {

  const { id } =
    useParams();


  const navigate =
    useNavigate();


  const findingId =
    Number(id);


  const {
    data,
    isLoading,
    error,
  } =
    useAuditFinding(
      findingId
    );


  const updateMutation =
    useUpdateAuditFinding();


  async function handleSubmit(
    formData: CreateAuditFindingRequest
  ) {

    try {

      await updateMutation.mutateAsync({

        id: findingId,

        data: formData,

      });


      navigate(
        "/audit-findings"
      );

    } catch (error: unknown) {

      console.error(
        "Failed to update audit finding:",
        error
      );

      const axiosError =
        error instanceof AxiosError
          ? error
          : null;

      const detail =
        axiosError?.response?.data?.detail;

      const message =
        typeof detail === "string"
          ? detail
          : "Failed to update audit finding.";

      alert(message);

    }

  }


  if (isLoading) {

    return (

      <AppLayout>

        <div className="p-10">

          Loading Audit Finding...

        </div>

      </AppLayout>

    );

  }


  if (
    error ||
    !data
  ) {

    return (

      <AppLayout>

        <div className="p-10 text-red-500">

          Audit Finding not found.

        </div>

      </AppLayout>

    );

  }


  return (

    <AppLayout>

      <div className="mx-auto max-w-3xl">

        <div className="mb-8">

          <h1 className="text-3xl font-bold">

            Edit Audit Finding

          </h1>


          <p className="mt-1 text-slate-500">

            Update the audit finding details.

          </p>

        </div>


        <AuditFindingForm

          mode="edit"

          finding={data}

          onSubmit={handleSubmit}

          isSubmitting={
            updateMutation.isPending
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