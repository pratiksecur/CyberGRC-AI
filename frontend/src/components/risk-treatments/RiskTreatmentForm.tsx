import {
  type FormEvent,
  useState,
} from "react";

import { Input } from "@/components/ui/input";

import { useVisibleUsers } from "@/hooks/useVisibleUsers";
import { useAuth } from "@/contexts/useAuth";

import type {
  RiskTreatment,
  CreateRiskTreatmentRequest,
} from "@/api/riskTreatments";


export type RiskTreatmentFormValues =
  CreateRiskTreatmentRequest;


interface Props {
  initialData?: RiskTreatment;

  onSubmit: (
    data: RiskTreatmentFormValues
  ) => void | Promise<void>;

  onCancel: () => void;

  isSubmitting: boolean;

  submitLabel: string;
}


const STRATEGIES = [
  "Mitigate",
  "Avoid",
  "Transfer",
  "Accept",
] as const;


const STATUSES = [
  "Planned",
  "In Progress",
  "Completed",
  "Cancelled",
] as const;


export default function RiskTreatmentForm({
  initialData,
  onSubmit,
  onCancel,
  isSubmitting,
  submitLabel,
}: Props) {
  const { user } = useAuth();

  const {
    data: visibleUsers,
    isLoading: usersLoading,
    isError: usersError,
  } = useVisibleUsers();


  const canApprove =
    user?.role === "Admin" ||
    user?.role === "GRC Manager";

  const hasFinalAcceptanceDecision =
    initialData?.strategy === "Accept" &&
    (initialData?.acceptance_status === "Approved" ||
      initialData?.acceptance_status === "Rejected");


  // ========================================================
  // FORM STATE
  // ========================================================

  const [strategy, setStrategy] =
    useState<
      RiskTreatmentFormValues["strategy"]
    >(
      initialData?.strategy ??
        "Mitigate"
    );


  const [status, setStatus] =
    useState<
      RiskTreatmentFormValues["status"]
    >(
      initialData?.status ??
        "Planned"
    );


  const [treatmentPlan, setTreatmentPlan] =
    useState(
      initialData?.treatment_plan ??
        ""
    );


  const [ownerId, setOwnerId] =
    useState<number | null>(
      initialData?.owner_id ??
        user?.id ??
        null
    );


  const [targetDate, setTargetDate] =
    useState(
      initialData?.target_date ??
        ""
    );


  const [residualEnabled, setResidualEnabled] =
    useState(
      initialData?.residual_likelihood != null &&
        initialData?.residual_impact != null &&
        initialData?.residual_risk_score != null
    );


  const [residualLikelihood, setResidualLikelihood] =
    useState<number | null>(
      initialData?.residual_likelihood ??
        null
    );


  const [residualImpact, setResidualImpact] =
    useState<number | null>(
      initialData?.residual_impact ??
        null
    );


  const [acceptanceStatus, setAcceptanceStatus] =
    useState<
      RiskTreatmentFormValues["acceptance_status"]
    >(
      initialData?.acceptance_status ??
        "Not Required"
    );


  const [acceptanceReason, setAcceptanceReason] =
    useState(
      initialData?.acceptance_reason ??
        ""
    );


  // ========================================================
  // EFFECTIVE OWNER
  // ========================================================
  //
  // We intentionally do not call setState from an effect.
  //
  // For a new treatment:
  //   current authenticated user is preferred.
  //
  // If the authenticated user is not present yet, the first
  // visible user is used as a fallback once users load.
  //
  // For an existing treatment:
  //   initialData.owner_id remains authoritative.
  //
  // ========================================================

  const effectiveOwnerId =
    ownerId ??
    user?.id ??
    visibleUsers?.[0]?.id ??
    null;


  // ========================================================
  // RESIDUAL RISK
  // ========================================================

  const residualRiskScore =
    residualEnabled &&
    residualLikelihood !== null &&
    residualImpact !== null
      ? residualLikelihood *
        residualImpact
      : null;


  // ========================================================
  // STRATEGY CHANGE
  // ========================================================

  function handleStrategyChange(
    nextStrategy:
      RiskTreatmentFormValues["strategy"]
  ) {
    setStrategy(
      nextStrategy
    );

    if (
      nextStrategy !== "Accept"
    ) {
      setAcceptanceStatus(
        "Not Required"
      );

      setAcceptanceReason(
        ""
      );

      return;
    }

    setAcceptanceStatus(
      "Pending"
    );
  }


  // ========================================================
  // SUBMIT
  // ========================================================

  async function handleSubmit(
    event: FormEvent<HTMLFormElement>
  ) {
    event.preventDefault();


    if (!effectiveOwnerId) {
      window.alert(
        "Please select a treatment owner."
      );

      return;
    }


    if (
      treatmentPlan.trim().length < 10
    ) {
      window.alert(
        "Treatment plan must contain at least 10 characters."
      );

      return;
    }


    if (
      residualEnabled &&
      (
        residualLikelihood === null ||
        residualImpact === null
      )
    ) {
      window.alert(
        "Please provide both residual likelihood and residual impact."
      );

      return;
    }


    const finalAcceptanceDecision =
      strategy === "Accept" &&
      (acceptanceStatus === "Approved" ||
        acceptanceStatus === "Rejected");

    if (
      finalAcceptanceDecision &&
      !acceptanceReason.trim()
    ) {
      window.alert(
        "A final risk acceptance decision requires an acceptance reason."
      );

      return;
    }


    if (
      hasFinalAcceptanceDecision &&
      strategy !== "Accept"
    ) {
      window.alert(
        "A finalized risk acceptance decision cannot change treatment strategy."
      );

      return;
    }


    const data:
      RiskTreatmentFormValues = {
      risk_id:
        initialData?.risk_id ??
        0,

      strategy,

      status,

      treatment_plan:
        treatmentPlan.trim(),

      owner_id:
        effectiveOwnerId,

      target_date:
        targetDate ||
        null,

      residual_likelihood:
        residualEnabled
          ? residualLikelihood
          : null,

      residual_impact:
        residualEnabled
          ? residualImpact
          : null,

      residual_risk_score:
        residualRiskScore,

      acceptance_status:
        strategy === "Accept"
          ? acceptanceStatus
          : "Not Required",

      acceptance_reason:
        strategy === "Accept" &&
        acceptanceReason.trim()
          ? acceptanceReason.trim()
          : null,
    };


    await onSubmit(
      data
    );
  }


  // ========================================================
  // RENDER
  // ========================================================

  return (
    <form
      onSubmit={
        handleSubmit
      }
      className="space-y-6 rounded-2xl border bg-white p-8 shadow-sm"
    >

      {/* ==================================================
          Strategy
      ================================================== */}

      <div>

        <label className="mb-2 block text-sm font-medium text-slate-700">
          Treatment Strategy
        </label>

        <select
          value={strategy}
          onChange={(event) =>
            handleStrategyChange(
              event.target.value as
                RiskTreatmentFormValues["strategy"]
            )
          }
          disabled={
            isSubmitting ||
            hasFinalAcceptanceDecision
          }
          className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 outline-none focus:border-blue-500"
        >

          {STRATEGIES.map(
            (item) => (
              <option
                key={item}
                value={item}
              >
                {item}
              </option>
            )
          )}

        </select>

      </div>


      {/* ==================================================
          Status
      ================================================== */}

      <div>

        <label className="mb-2 block text-sm font-medium text-slate-700">
          Treatment Status
        </label>

        <select
          value={status}
          onChange={(event) =>
            setStatus(
              event.target.value as
                RiskTreatmentFormValues["status"]
            )
          }
          disabled={isSubmitting}
          className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 outline-none focus:border-blue-500"
        >

          {STATUSES.map(
            (item) => (
              <option
                key={item}
                value={item}
              >
                {item}
              </option>
            )
          )}

        </select>

      </div>


      {/* ==================================================
          Treatment Plan
      ================================================== */}

      <div>

        <label className="mb-2 block text-sm font-medium text-slate-700">
          Treatment Plan
        </label>

        <textarea
          rows={6}
          value={treatmentPlan}
          onChange={(event) =>
            setTreatmentPlan(
              event.target.value
            )
          }
          disabled={isSubmitting}
          placeholder="Describe how the risk will be treated..."
          className="w-full rounded-lg border border-slate-300 p-3 outline-none focus:border-blue-500"
          required
        />

      </div>


      {/* ==================================================
          Owner
      ================================================== */}

      <div>

        <label className="mb-2 block text-sm font-medium text-slate-700">
          Treatment Owner
        </label>

        {usersLoading ? (

          <div className="rounded-lg border bg-slate-50 px-4 py-3 text-sm text-slate-500">
            Loading available users...
          </div>

        ) : usersError ? (

          <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
            Unable to load available treatment owners.
          </div>

        ) : (

          <select
            value={
              effectiveOwnerId ??
              ""
            }
            onChange={(event) =>
              setOwnerId(
                Number(
                  event.target.value
                )
              )
            }
            disabled={
              isSubmitting ||
              usersLoading
            }
            required
            className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 outline-none focus:border-blue-500"
          >

            <option
              value=""
              disabled
            >
              Select treatment owner
            </option>

            {visibleUsers?.map(
              (visibleUser) => (

                <option
                  key={visibleUser.id}
                  value={visibleUser.id}
                >
                  {visibleUser.full_name} —{" "}
                  {visibleUser.role}
                </option>

              )
            )}

          </select>

        )}

      </div>


      {/* ==================================================
          Target Date
      ================================================== */}

      <div>

        <label className="mb-2 block text-sm font-medium text-slate-700">
          Target Date
        </label>

        <Input
          type="date"
          value={targetDate}
          onChange={(event) =>
            setTargetDate(
              event.target.value
            )
          }
          disabled={isSubmitting}
        />

      </div>


      {/* ==================================================
          Residual Risk
      ================================================== */}

      <div className="rounded-xl border bg-slate-50 p-5">

        <div className="flex items-center justify-between gap-4">

          <div>

            <h3 className="font-semibold text-slate-900">
              Residual Risk Assessment
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Record the expected risk remaining after treatment.
            </p>

          </div>

          <label className="flex items-center gap-2 text-sm font-medium text-slate-700">

            <input
              type="checkbox"
              checked={
                residualEnabled
              }
              onChange={(event) => {

                const enabled =
                  event.target.checked;

                setResidualEnabled(
                  enabled
                );

                if (!enabled) {

                  setResidualLikelihood(
                    null
                  );

                  setResidualImpact(
                    null
                  );

                }

              }}
              disabled={isSubmitting}
              className="h-4 w-4"
            />

            Enable

          </label>

        </div>


        {residualEnabled && (

          <div className="mt-5 grid gap-5 md:grid-cols-3">

            <div>

              <label className="mb-2 block text-sm font-medium text-slate-700">
                Residual Likelihood
              </label>

              <Input
                type="number"
                min={1}
                max={5}
                value={
                  residualLikelihood ??
                  ""
                }
                onChange={(event) =>
                  setResidualLikelihood(
                    event.target.value
                      ? Number(
                          event.target.value
                        )
                      : null
                  )
                }
                disabled={
                  isSubmitting
                }
              />

            </div>


            <div>

              <label className="mb-2 block text-sm font-medium text-slate-700">
                Residual Impact
              </label>

              <Input
                type="number"
                min={1}
                max={5}
                value={
                  residualImpact ??
                  ""
                }
                onChange={(event) =>
                  setResidualImpact(
                    event.target.value
                      ? Number(
                          event.target.value
                        )
                      : null
                  )
                }
                disabled={
                  isSubmitting
                }
              />

            </div>


            <div>

              <label className="mb-2 block text-sm font-medium text-slate-700">
                Residual Risk Score
              </label>

              <Input
                value={
                  residualRiskScore ??
                  ""
                }
                readOnly
                disabled
              />

            </div>

          </div>

        )}

      </div>


      {/* ==================================================
          Acceptance
      ================================================== */}

      {strategy ===
        "Accept" && (

        <div className="rounded-xl border border-amber-200 bg-amber-50 p-5">

          <h3 className="font-semibold text-amber-900">
            Risk Acceptance
          </h3>

          <p className="mt-1 text-sm text-amber-800">
            Acceptance remains part of the audit trail and does not remove the underlying risk.
          </p>


          <div className="mt-5 space-y-5">

            <div>

              <label className="mb-2 block text-sm font-medium text-slate-700">
                Acceptance Status
              </label>

              {canApprove ? (

                <select
                  value={
                    acceptanceStatus
                  }
                  onChange={(event) =>
                    setAcceptanceStatus(
                      event.target.value as
                        RiskTreatmentFormValues["acceptance_status"]
                    )
                  }
                  disabled={
                    isSubmitting ||
                    hasFinalAcceptanceDecision
                  }
                  className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 outline-none focus:border-blue-500"
                >

                  <option value="Pending">
                    Pending
                  </option>

                  <option value="Approved">
                    Approved
                  </option>

                  <option value="Rejected">
                    Rejected
                  </option>

                </select>

              ) : (

                <div className="rounded-lg border bg-white px-4 py-3 font-medium text-slate-700">
                  {acceptanceStatus}
                </div>

              )}

            </div>


            <div>

              <label className="mb-2 block text-sm font-medium text-slate-700">
                Acceptance Reason
              </label>

              <textarea
                rows={4}
                value={
                  acceptanceReason
                }
                onChange={(event) =>
                  setAcceptanceReason(
                    event.target.value
                  )
                }
                disabled={
                  isSubmitting ||
                  hasFinalAcceptanceDecision
                }
                readOnly={
                  hasFinalAcceptanceDecision
                }
                placeholder="Document the rationale for the acceptance decision..."
                className="w-full rounded-lg border border-slate-300 bg-white p-3 outline-none focus:border-blue-500"
              />

            </div>

          </div>

        </div>

      )}


      {/* ==================================================
          Actions
      ================================================== */}

      <div className="flex justify-end gap-3 border-t pt-6">

        <button
          type="button"
          onClick={
            onCancel
          }
          disabled={
            isSubmitting
          }
          className="rounded-lg border border-slate-300 px-5 py-2.5 font-medium text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
        >
          Cancel
        </button>


        <button
          type="submit"
          disabled={
            isSubmitting ||
            effectiveOwnerId === null ||
            usersLoading
          }
          className="rounded-lg bg-blue-600 px-5 py-2.5 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting
            ? "Saving..."
            : submitLabel}
        </button>

      </div>

    </form>
  );
}