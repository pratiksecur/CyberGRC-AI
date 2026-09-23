import {
  CalendarDays,
  CheckCircle2,
  ClipboardList,
  Eye,
  Pencil,
  ShieldCheck,
  Trash2,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import Can from "@/components/auth/Can";
import { Button } from "@/components/ui/button";

import {
  useRiskTreatmentsForRisk,
} from "@/hooks/useRiskTreatmentsForRisk";

import {
  useDeleteRiskTreatment,
} from "@/hooks/useDeleteRiskTreatment";


interface Props {
  riskId: number;
}


function statusClass(
  status: string
) {

  switch (status) {

    case "Completed":
      return "bg-green-100 text-green-700";

    case "In Progress":
      return "bg-yellow-100 text-yellow-700";

    case "Cancelled":
      return "bg-slate-100 text-slate-600";

    default:
      return "bg-blue-100 text-blue-700";
  }
}


function strategyClass(
  strategy: string
) {

  switch (strategy) {

    case "Accept":
      return "bg-amber-100 text-amber-700";

    case "Avoid":
      return "bg-red-100 text-red-700";

    case "Transfer":
      return "bg-purple-100 text-purple-700";

    default:
      return "bg-indigo-100 text-indigo-700";
  }
}


function acceptanceClass(
  status: string
) {

  switch (status) {

    case "Approved":
      return "bg-green-100 text-green-700";

    case "Rejected":
      return "bg-red-100 text-red-700";

    case "Pending":
      return "bg-amber-100 text-amber-700";

    default:
      return "bg-slate-100 text-slate-600";
  }
}


export default function RiskTreatmentSection({
  riskId,
}: Props) {

  const navigate =
    useNavigate();

  const {
    data: treatments,
    isLoading,
    error,
  } =
    useRiskTreatmentsForRisk(
      riskId
    );

  const deleteMutation =
    useDeleteRiskTreatment();


  async function handleDelete(
    treatmentId: number
  ) {

    const confirmed =
      window.confirm(
        "Delete this risk treatment?"
      );

    if (!confirmed) {
      return;
    }

    try {

      await deleteMutation.mutateAsync(
        treatmentId
      );

    } catch {

      alert(
        "Failed to delete risk treatment."
      );

    }
  }


  return (
    <section className="rounded-2xl border bg-white shadow-sm">

      {/* ================================================== */}
      {/* Header */}
      {/* ================================================== */}

      <div className="flex flex-col justify-between gap-4 border-b p-6 sm:flex-row sm:items-center">

        <div className="flex items-start gap-3">

          <div className="rounded-xl bg-indigo-50 p-3">

            <ClipboardList className="h-6 w-6 text-indigo-600" />

          </div>

          <div>

            <h2 className="text-lg font-semibold text-slate-900">
              Risk Treatment
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Treatment strategy, residual risk, ownership, and acceptance status.
            </p>

          </div>

        </div>


        <Can
          resource="risk_treatments"
          action="create"
        >
          <Button
            onClick={() =>
              navigate(
                `/risk-treatments/new?risk_id=${riskId}`
              )
            }
          >
            Create Treatment
          </Button>
        </Can>

      </div>


      {/* ================================================== */}
      {/* Body */}
      {/* ================================================== */}

      <div className="p-6">

        {isLoading && (

          <div className="space-y-4">

            {Array.from({
              length: 2,
            }).map(
              (_, index) => (
                <div
                  key={index}
                  className="h-40 animate-pulse rounded-xl bg-slate-100"
                />
              )
            )}

          </div>

        )}


        {!isLoading && error && (

          <div className="rounded-xl border border-red-200 bg-red-50 p-5">

            <h3 className="font-semibold text-red-700">
              Risk treatments unavailable
            </h3>

            <p className="mt-1 text-sm text-red-600">
              The treatment records could not be loaded.
            </p>

          </div>

        )}


        {!isLoading &&
          !error &&
          (!treatments ||
            treatments.length === 0) && (

            <div className="rounded-xl border border-dashed p-8 text-center">

              <ClipboardList className="mx-auto h-8 w-8 text-slate-400" />

              <h3 className="mt-3 font-semibold text-slate-900">
                No risk treatment recorded
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                Create a treatment plan to document how this risk will be handled.
              </p>

              <Can
                resource="risk_treatments"
                action="create"
              >
                <Button
                  className="mt-4"
                  variant="outline"
                  onClick={() =>
                    navigate(
                      `/risk-treatments/new?risk_id=${riskId}`
                    )
                  }
                >
                  Add Treatment
                </Button>
              </Can>

            </div>

          )}


        {!isLoading &&
          !error &&
          treatments &&
          treatments.length > 0 && (

            <div className="space-y-4">

              {treatments.map(
                (treatment) => (

                  <div
                    key={treatment.id}
                    className="rounded-xl border p-5"
                  >

                    <div className="flex flex-col justify-between gap-4 lg:flex-row lg:items-start">

                      <div className="min-w-0">

                        <div className="flex flex-wrap items-center gap-2">

                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-semibold ${strategyClass(
                              treatment.strategy
                            )}`}
                          >
                            {treatment.strategy}
                          </span>

                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-semibold ${statusClass(
                              treatment.status
                            )}`}
                          >
                            {treatment.status}
                          </span>

                          {treatment.strategy ===
                            "Accept" && (

                            <span
                              className={`rounded-full px-2.5 py-1 text-xs font-semibold ${acceptanceClass(
                                treatment.acceptance_status
                              )}`}
                            >
                              Acceptance:{" "}
                              {
                                treatment.acceptance_status
                              }
                            </span>

                          )}

                        </div>


                        <p className="mt-3 whitespace-pre-wrap leading-6 text-slate-700">
                          {treatment.treatment_plan}
                        </p>


                        <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">

                          <div className="rounded-lg bg-slate-50 p-3">

                            <p className="text-xs text-slate-500">
                              Owner
                            </p>

                            <p className="mt-1 font-medium text-slate-900">
                              User #{treatment.owner_id}
                            </p>

                          </div>


                          <div className="rounded-lg bg-slate-50 p-3">

                            <p className="text-xs text-slate-500">
                              Residual Risk
                            </p>

                            <p className="mt-1 font-medium text-slate-900">
                              {treatment.residual_risk_score ??
                                "Not assessed"}
                            </p>

                          </div>


                          <div className="rounded-lg bg-slate-50 p-3">

                            <p className="text-xs text-slate-500">
                              Target Date
                            </p>

                            <div className="mt-1 flex items-center gap-2 font-medium text-slate-900">

                              <CalendarDays className="h-4 w-4 text-slate-400" />

                              {treatment.target_date
                                ? new Date(
                                    treatment.target_date
                                  ).toLocaleDateString()
                                : "No target date"}

                            </div>

                          </div>


                          <div className="rounded-lg bg-slate-50 p-3">

                            <p className="text-xs text-slate-500">
                              Created
                            </p>

                            <div className="mt-1 flex items-center gap-2 font-medium text-slate-900">

                              <CheckCircle2 className="h-4 w-4 text-slate-400" />

                              {new Date(
                                treatment.created_at
                              ).toLocaleDateString()}

                            </div>

                          </div>

                        </div>


                        {treatment.strategy ===
                          "Accept" &&
                          treatment.acceptance_reason && (

                            <div className="mt-4 rounded-lg border border-amber-200 bg-amber-50 p-4">

                              <div className="flex items-start gap-2">

                                <ShieldCheck className="mt-0.5 h-4 w-4 text-amber-700" />

                                <div>

                                  <p className="text-sm font-semibold text-amber-900">
                                    Acceptance Reason
                                  </p>

                                  <p className="mt-1 whitespace-pre-wrap text-sm leading-6 text-amber-800">
                                    {
                                      treatment.acceptance_reason
                                    }
                                  </p>

                                </div>

                              </div>

                            </div>

                          )}

                      </div>


                      {/* Actions */}

                      <div className="flex shrink-0 items-center gap-2 lg:justify-end">

                        <Button
                          variant="outline"
                          size="sm"
                          onClick={() =>
                            navigate(
                              `/risk-treatments/${treatment.id}`
                            )
                          }
                        >
                          <Eye className="mr-2 h-4 w-4" />
                          View
                        </Button>


                        <Can
                          resource="risk_treatments"
                          action="update"
                        >
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() =>
                              navigate(
                                `/risk-treatments/${treatment.id}/edit`
                              )
                            }
                          >
                            <Pencil className="mr-2 h-4 w-4" />
                            Edit
                          </Button>
                        </Can>


                        <Can
                          resource="risk_treatments"
                          action="delete"
                        >
                          <Button
                            variant="outline"
                            size="sm"
                            onClick={() =>
                              handleDelete(
                                treatment.id
                              )
                            }
                            disabled={
                              deleteMutation.isPending
                            }
                          >
                            <Trash2 className="mr-2 h-4 w-4" />
                            Delete
                          </Button>
                        </Can>

                      </div>

                    </div>

                  </div>

                )
              )}

            </div>

          )}

      </div>

    </section>
  );
}