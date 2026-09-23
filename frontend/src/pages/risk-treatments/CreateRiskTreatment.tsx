import { useNavigate, useSearchParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import RiskTreatmentForm from "@/components/risk-treatments/RiskTreatmentForm";

import {
  useCreateRiskTreatment,
} from "@/hooks/useCreateRiskTreatment";

import {
  useRisk,
} from "@/hooks/useRisk";

import type {
  RiskTreatmentFormValues,
} from "@/components/risk-treatments/RiskTreatmentForm";

import type {
  CreateRiskTreatmentRequest,
} from "@/api/riskTreatments";


export default function CreateRiskTreatment() {

  const navigate =
    useNavigate();

  const [
    searchParams,
  ] = useSearchParams();


  const riskId = Number(
    searchParams.get("risk_id")
  );


  const {
    data: risk,
    isLoading: riskLoading,
    error: riskError,
  } = useRisk(riskId);


  const createMutation =
    useCreateRiskTreatment();


  async function handleSubmit(
    formData: RiskTreatmentFormValues
  ) {

    if (!riskId || !risk) {
      return;
    }


    const payload:
      CreateRiskTreatmentRequest = {
      ...formData,

      risk_id:
        riskId,

      acceptance_status:
        formData.strategy === "Accept"
          ? formData.acceptance_status
          : "Not Required",

      acceptance_reason:
        formData.strategy === "Accept"
          ? formData.acceptance_reason
          : null,
    };


    try {

      await createMutation.mutateAsync(
        payload
      );

      navigate(
        `/risks/${riskId}`
      );

    } catch (
      error
    ) {

      console.error(
        error
      );

      alert(
        "Failed to create risk treatment."
      );

    }
  }


  if (!riskId) {
    return (
      <AppLayout>

        <div className="mx-auto max-w-3xl p-10">

          <h1 className="text-2xl font-bold text-slate-900">
            Risk Treatment
          </h1>

          <p className="mt-2 text-red-600">
            A valid risk must be selected.
          </p>

        </div>

      </AppLayout>
    );
  }


  if (riskLoading) {
    return (
      <AppLayout>

        <div className="p-10">
          Loading Risk...
        </div>

      </AppLayout>
    );
  }


  if (riskError || !risk) {
    return (
      <AppLayout>

        <div className="p-10 text-red-600">
          Risk not found within your access scope.
        </div>

      </AppLayout>
    );
  }


  return (
    <AppLayout>

      <div className="mx-auto max-w-4xl space-y-6">

        <div>

          <h1 className="text-3xl font-bold text-slate-900">
            Create Risk Treatment
          </h1>

          <p className="mt-1 text-slate-500">
            Define how risk{" "}
            <span className="font-medium text-slate-700">
              #{risk.id} — {risk.title}
            </span>{" "}
            will be treated.
          </p>

        </div>


        <RiskTreatmentForm
          onSubmit={
            handleSubmit
          }
          onCancel={() =>
            navigate(
              `/risks/${riskId}`
            )
          }
          isSubmitting={
            createMutation.isPending
          }
          submitLabel="Create Treatment"
        />

      </div>

    </AppLayout>
  );
}