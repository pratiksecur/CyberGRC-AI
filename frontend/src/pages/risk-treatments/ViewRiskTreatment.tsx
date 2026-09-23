import {
  ArrowLeft,
  CalendarDays,
  CheckCircle2,
  ClipboardList,
  Pencil,
  ShieldCheck,
  Trash2,
} from "lucide-react";

import { useNavigate, useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import Can from "@/components/auth/Can";

import { Button } from "@/components/ui/button";

import {
  useRiskTreatment,
} from "@/hooks/useRiskTreatment";

import {
  useRisk,
} from "@/hooks/useRisk";

import {
  useDeleteRiskTreatment,
} from "@/hooks/useDeleteRiskTreatment";


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


export default function ViewRiskTreatment() {

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


  const deleteMutation =
    useDeleteRiskTreatment();


  async function handleDelete() {

    if (!treatment) {
      return;
    }


    const confirmed =
      window.confirm(
        "Delete this risk treatment?"
      );


    if (!confirmed) {
      return;
    }


    try {

      await deleteMutation.mutateAsync(
        treatment.id
      );

      navigate(
        `/risks/${treatment.risk_id}`
      );

    } catch {

      alert(
        "Failed to delete risk treatment."
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

        <div className="mx-auto max-w-4xl p-10">

          <div className="rounded-xl border border-red-200 bg-red-50 p-6">

            <h2 className="font-semibold text-red-700">
              Risk Treatment Not Found
            </h2>

            <p className="mt-1 text-sm text-red-600">
              The requested treatment could not be found within your access scope.
            </p>

            <Button
              className="mt-4"
              variant="outline"
              onClick={() =>
                navigate("/risks")
              }
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back to Risks
            </Button>

          </div>

        </div>

      </AppLayout>
    );
  }


  return (
    <AppLayout>

      <div className="mx-auto max-w-5xl space-y-6">

        {/* ================================================== */}
        {/* Header */}
        {/* ================================================== */}

        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">

          <div>

            <button
              type="button"
              onClick={() =>
                navigate(
                  `/risks/${treatment.risk_id}`
                )
              }
              className="mb-4 inline-flex items-center gap-2 text-sm text-slate-500 transition hover:text-slate-900"
            >
              <ArrowLeft className="h-4 w-4" />
              Back to Risk
            </button>


            <div className="flex items-center gap-3">

              <h1 className="text-3xl font-bold text-slate-900">
                Risk Treatment #{treatment.id}
              </h1>

            </div>


            {risk && (

              <p className="mt-2 text-slate-500">
                Risk{" "}
                <span className="font-medium text-slate-700">
                  #{risk.id} — {risk.title}
                </span>
              </p>

            )}

          </div>


          <div className="flex flex-wrap gap-2">

            <Can
              resource="risk_treatments"
              action="update"
            >
              <Button
                variant="outline"
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
                onClick={
                  handleDelete
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


        {/* ================================================== */}
        {/* Main */}
        {/* ================================================== */}

        <div className="rounded-2xl border bg-white p-8 shadow-sm">

          {/* Status */}

          <div className="mb-8 flex flex-wrap gap-2">

            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold ${strategyClass(
                treatment.strategy
              )}`}
            >
              {treatment.strategy}
            </span>


            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold ${statusClass(
                treatment.status
              )}`}
            >
              {treatment.status}
            </span>


            {treatment.strategy ===
              "Accept" && (

              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold ${acceptanceClass(
                  treatment.acceptance_status
                )}`}
              >
                Acceptance:{" "}
                {treatment.acceptance_status}
              </span>

            )}

          </div>


          {/* ================================================== */}
          {/* Details */}
          {/* ================================================== */}

          <div className="grid gap-5 md:grid-cols-2">

            <div className="rounded-xl bg-slate-50 p-5">

              <p className="text-sm text-slate-500">
                Treatment Owner
              </p>

              <p className="mt-1 font-semibold text-slate-900">
                User #{treatment.owner_id}
              </p>

            </div>


            <div className="rounded-xl bg-slate-50 p-5">

              <div className="flex items-center gap-2">

                <CalendarDays className="h-4 w-4 text-slate-400" />

                <p className="text-sm text-slate-500">
                  Target Date
                </p>

              </div>

              <p className="mt-1 font-semibold text-slate-900">
                {treatment.target_date
                  ? new Date(
                      treatment.target_date
                    ).toLocaleDateString()
                  : "No target date"}
              </p>

            </div>


            <div className="rounded-xl bg-slate-50 p-5">

              <p className="text-sm text-slate-500">
                Residual Likelihood
              </p>

              <p className="mt-1 font-semibold text-slate-900">
                {treatment.residual_likelihood ??
                  "Not assessed"}
              </p>

            </div>


            <div className="rounded-xl bg-slate-50 p-5">

              <p className="text-sm text-slate-500">
                Residual Impact
              </p>

              <p className="mt-1 font-semibold text-slate-900">
                {treatment.residual_impact ??
                  "Not assessed"}
              </p>

            </div>


            <div className="rounded-xl bg-slate-50 p-5 md:col-span-2">

              <p className="text-sm text-slate-500">
                Residual Risk Score
              </p>

              <p className="mt-1 text-2xl font-bold text-slate-900">
                {treatment.residual_risk_score ??
                  "Not assessed"}
              </p>

            </div>

          </div>


          {/* ================================================== */}
          {/* Treatment Plan */}
          {/* ================================================== */}

          <div className="mt-8 border-t pt-8">

            <div className="flex items-start gap-3">

              <ClipboardList className="mt-1 h-5 w-5 text-slate-400" />

              <div>

                <h2 className="font-semibold text-slate-900">
                  Treatment Plan
                </h2>

                <p className="mt-3 whitespace-pre-wrap leading-7 text-slate-600">
                  {treatment.treatment_plan}
                </p>

              </div>

            </div>

          </div>


          {/* ================================================== */}
          {/* Acceptance */}
          {/* ================================================== */}

          {treatment.strategy ===
            "Accept" && (

            <div className="mt-8 border-t pt-8">

              <div className="rounded-xl border border-amber-200 bg-amber-50 p-6">

                <div className="flex items-start gap-3">

                  <ShieldCheck className="mt-1 h-5 w-5 text-amber-700" />

                  <div className="min-w-0">

                    <h2 className="font-semibold text-amber-900">
                      Risk Acceptance
                    </h2>

                    <p className="mt-1 text-sm text-amber-800">
                      Acceptance is recorded separately from the underlying risk.
                    </p>


                    <div className="mt-5 grid gap-4 md:grid-cols-2">

                      <div>

                        <p className="text-xs font-medium text-amber-700">
                          Status
                        </p>

                        <p className="mt-1 font-semibold text-amber-900">
                          {
                            treatment.acceptance_status
                          }
                        </p>

                      </div>


                      <div>

                        <p className="text-xs font-medium text-amber-700">
                          Accepted / Rejected By
                        </p>

                        <p className="mt-1 font-semibold text-amber-900">
                          {treatment.accepted_by_id
                            ? `User #${treatment.accepted_by_id}`
                            : "Not yet decided"}
                        </p>

                      </div>

                    </div>


                    {treatment.acceptance_reason && (

                      <div className="mt-5 border-t border-amber-200 pt-5">

                        <p className="text-xs font-medium text-amber-700">
                          Reason
                        </p>

                        <p className="mt-2 whitespace-pre-wrap leading-6 text-amber-900">
                          {
                            treatment.acceptance_reason
                          }
                        </p>

                      </div>

                    )}


                    {treatment.accepted_at && (

                      <div className="mt-5 flex items-center gap-2 text-sm text-amber-800">

                        <CheckCircle2 className="h-4 w-4" />

                        Decision recorded{" "}
                        {new Date(
                          treatment.accepted_at
                        ).toLocaleString()}

                      </div>

                    )}

                  </div>

                </div>

              </div>

            </div>

          )}


          {/* ================================================== */}
          {/* Audit timestamps */}
          {/* ================================================== */}

          <div className="mt-8 border-t pt-8">

            <div className="grid gap-4 md:grid-cols-2">

              <div>

                <p className="text-xs font-medium text-slate-500">
                  Created
                </p>

                <p className="mt-1 text-sm text-slate-700">
                  {new Date(
                    treatment.created_at
                  ).toLocaleString()}
                </p>

              </div>


              <div>

                <p className="text-xs font-medium text-slate-500">
                  Updated
                </p>

                <p className="mt-1 text-sm text-slate-700">
                  {new Date(
                    treatment.updated_at
                  ).toLocaleString()}
                </p>

              </div>

            </div>

          </div>

        </div>

      </div>

    </AppLayout>
  );
}