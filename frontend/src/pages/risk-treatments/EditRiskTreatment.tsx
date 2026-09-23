import { useNavigate, useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import RiskTreatmentForm from "@/components/risk-treatments/RiskTreatmentForm";

import {
  useRiskTreatment,
} from "@/hooks/useRiskTreatment";

import {
  useRisk,
} from "@/hooks/useRisk";

import {
  useUpdateRiskTreatment,
} from "@/hooks/useUpdateRiskTreatment";

import type {
  RiskTreatmentFormValues,
} from "@/components/risk-treatments/RiskTreatmentForm";

import type {
  UpdateRiskTreatmentRequest,
} from "@/api/riskTreatments";


export default function EditRiskTreatment() {

  const {
    id,
  } = useParams();

  const navigate =
    useNavigate();


  const treatmentId =
    Number(id);


  const {
    data: treatment,
    isLoading,
    error,
  } = useRiskTreatment(
    treatmentId
  );


  const {
    data: risk,
  } = useRisk(
    treatment?.risk_id ?? 0
  );


  const updateMutation =
    useUpdateRiskTreatment();


  async function handleSubmit(
    formData: RiskTreatmentFormValues
  ) {

    if (!treatment) {
      return;
    }


    const payload:
      UpdateRiskTreatmentRequest = {

      strategy:
        formData.strategy,

      status:
        formData.status,

      treatment_plan:
        formData.treatment_plan,

      owner_id:
        formData.owner_id,

      target_date:
        formData.target_date,

      residual_likelihood:
        formData.residual_likelihood,

      residual_impact:
        formData.residual_impact,

      residual_risk_score:
        formData.residual_risk_score,
    };


    /*
     * Acceptance changes are sent only when the acceptance
     * status or acceptance reason actually changes.
     *
     * This prevents a normal treatment edit from accidentally
     * re-submitting an already-approved acceptance decision.
     */

    if (
      treatment.strategy !==
      formData.strategy
    ) {

      if (
        formData.strategy ===
        "Accept"
      ) {

        payload.acceptance_status =
          formData.acceptance_status;

        payload.acceptance_reason =
          formData.acceptance_reason;

      } else {

        payload.acceptance_status =
          "Not Required";

      }

    } else if (
      treatment.strategy ===
      "Accept"
    ) {

      if (
        treatment.acceptance_status !==
        formData.acceptance_status
      ) {

        payload.acceptance_status =
          formData.acceptance_status;

      }

      if (
        (
          treatment.acceptance_reason ??
          ""
        ) !==
        (
          formData.acceptance_reason ??
          ""
        )
      ) {

        payload.acceptance_reason =
          formData.acceptance_reason;

      }

    }


    try {

      const updated =
        await updateMutation.mutateAsync({
          id: treatment.id,
          data: payload,
        });


      navigate(
        `/risk-treatments/${updated.id}`
      );

    } catch (
      error
    ) {

      console.error(
        error
      );

      alert(
        "Failed to update risk treatment."
      );

    }
  }


  if (isLoading) {
    return (
      <AppLayout>

        <div className="p-10">
          Loading Risk Treatment...
        </div>

      </AppLayout>
    );
  }


  if (error || !treatment) {
    return (
      <AppLayout>

        <div className="p-10 text-red-600">
          Risk treatment not found within your access scope.
        </div>

      </AppLayout>
    );
  }


  return (
    <AppLayout>

      <div className="mx-auto max-w-4xl space-y-6">

        <div>

          <h1 className="text-3xl font-bold text-slate-900">
            Edit Risk Treatment
          </h1>

          <p className="mt-1 text-slate-500">
            Update the treatment plan, ownership, residual risk, or acceptance workflow.
          </p>

          {risk && (

            <p className="mt-2 text-sm text-slate-500">
              Risk:{" "}
              <span className="font-medium text-slate-700">
                #{risk.id} — {risk.title}
              </span>
            </p>

          )}

        </div>


        <RiskTreatmentForm
          initialData={
            treatment
          }
          onSubmit={
            handleSubmit
          }
          onCancel={() =>
            navigate(
              `/risk-treatments/${treatment.id}`
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