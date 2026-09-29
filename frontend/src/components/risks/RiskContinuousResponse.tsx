import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  Eye,
  GitBranch,
  ShieldAlert,
  UserCheck,
} from "lucide-react";

import type {
  RiskContinuousResponse,
  RiskResponseDecision,
  RiskResponseReason,
} from "@/api/risks";


// ==========================================================
// Helpers
// ==========================================================

function formatLabel(
  value: string
) {
  return value
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase()
    );
}


function stateClass(
  value: string
) {
  switch (value) {

    case "CURRENT":
      return "border-emerald-200 bg-emerald-50 text-emerald-700";

    case "DEGRADED":
      return "border-amber-200 bg-amber-50 text-amber-700";

    case "STALE":
      return "border-amber-200 bg-amber-50 text-amber-700";

    case "REASSESSMENT_REQUIRED":
    case "REQUIRES_REASSESSMENT":
      return "border-red-200 bg-red-50 text-red-700";

    default:
      return "border-slate-200 bg-slate-50 text-slate-700";
  }
}


function priorityClass(
  value: string
) {
  switch (value) {

    case "CRITICAL":
      return "border-red-300 bg-red-100 text-red-800";

    case "HIGH":
      return "border-orange-300 bg-orange-100 text-orange-800";

    case "MEDIUM":
      return "border-yellow-300 bg-yellow-100 text-yellow-800";

    case "LOW":
      return "border-emerald-300 bg-emerald-100 text-emerald-800";

    default:
      return "border-slate-200 bg-slate-100 text-slate-700";
  }
}


function decisionIcon(
  decision: string
) {
  switch (decision) {

    case "MONITOR":
      return Eye;

    case "REVIEW":
      return Clock3;

    case "REASSESS_RISK":
      return ShieldAlert;

    case "UPDATE_TREATMENT":
      return GitBranch;

    case "CONTROL_REVIEW":
      return ShieldAlert;

    case "EVIDENCE_REVIEW":
      return CheckCircle2;

    case "CORRECTIVE_ACTION_REVIEW":
      return AlertTriangle;

    case "ESCALATE":
      return UserCheck;

    default:
      return AlertTriangle;
  }
}


// ==========================================================
// Decision
// ==========================================================

interface DecisionCardProps {
  decision: RiskResponseDecision;
}

function DecisionCard({
  decision,
}: DecisionCardProps) {

  const Icon =
    decisionIcon(
      decision.decision
    );

  return (
    <div className="rounded-xl border border-slate-200 bg-white p-5">

      <div className="flex items-start justify-between gap-4">

        <div className="flex min-w-0 items-start gap-3">

          <div className="rounded-lg bg-slate-100 p-2">

            <Icon className="h-5 w-5 text-slate-700" />

          </div>

          <div className="min-w-0">

            <p className="font-semibold text-slate-900">
              {formatLabel(
                decision.decision
              )}
            </p>

            <p className="mt-1 text-sm text-slate-500">
              Recommended response
            </p>

          </div>

        </div>


        <span
          className={`shrink-0 rounded-full border px-2.5 py-1 text-xs font-semibold uppercase ${priorityClass(
            decision.priority
          )}`}
        >
          {decision.priority}
        </span>

      </div>


      {decision.reason_codes.length > 0 && (

        <div className="mt-4">

          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            Drivers
          </p>

          <div className="mt-2 flex flex-wrap gap-2">

            {decision.reason_codes.map(
              (code) => (
                <span
                  key={code}
                  className="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600"
                >
                  {formatLabel(code)}
                </span>
              )
            )}

          </div>

        </div>

      )}


      {decision.human_approval_required && (

        <div className="mt-4 flex items-start gap-2 rounded-lg border border-orange-200 bg-orange-50 p-3">

          <UserCheck className="mt-0.5 h-4 w-4 shrink-0 text-orange-600" />

          <div>

            <p className="text-sm font-semibold text-orange-800">
              Human approval required
            </p>

            <p className="mt-1 text-xs leading-5 text-orange-700">
              This response is advisory and must not be
              executed automatically.
            </p>

          </div>

        </div>

      )}

    </div>
  );
}


// ==========================================================
// Reason
// ==========================================================

interface ReasonListProps {
  reasons: RiskResponseReason[];
}

function ReasonList({
  reasons,
}: ReasonListProps) {

  if (reasons.length === 0) {

    return (
      <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">

        <div className="flex items-start gap-3">

          <CheckCircle2 className="mt-0.5 h-5 w-5 shrink-0 text-emerald-600" />

          <div>

            <p className="font-semibold text-emerald-700">
              No active response drivers
            </p>

            <p className="mt-1 text-sm leading-6 text-emerald-600">
              No monitored condition currently requires
              a response beyond normal observation.
            </p>

          </div>

        </div>

      </div>
    );
  }


  return (
    <div className="space-y-3">

      {reasons.map(
        (reason, index) => (

          <div
            key={`${reason.code}-${reason.resource_type}-${reason.resource_id}-${index}`}
            className="rounded-xl border border-slate-200 bg-white p-4"
          >

            <div className="flex items-start gap-3">

              <AlertTriangle
                className={`mt-0.5 h-5 w-5 shrink-0 ${
                  reason.severity === "CRITICAL"
                    ? "text-red-600"
                    : reason.severity === "HIGH"
                      ? "text-orange-600"
                      : "text-amber-600"
                }`}
              />

              <div className="min-w-0">

                <div className="flex flex-wrap items-center gap-2">

                  <span className="font-semibold text-slate-900">
                    {formatLabel(reason.code)}
                  </span>

                  <span className="rounded-full border border-slate-200 bg-slate-50 px-2 py-0.5 text-[10px] font-semibold uppercase tracking-wide text-slate-500">
                    {reason.severity}
                  </span>

                </div>

                <p className="mt-1 text-sm leading-6 text-slate-600">
                  {reason.message}
                </p>

              </div>

            </div>

          </div>

        )
      )}

    </div>
  );
}


// ==========================================================
// Main Component
// ==========================================================

interface RiskContinuousResponseProps {
  response: RiskContinuousResponse;
}

export default function RiskContinuousResponse({
  response,
}: RiskContinuousResponseProps) {

  return (
    <section className="rounded-2xl border bg-white shadow-sm">

      {/* ==================================================
          Header
      ================================================== */}

      <div className="border-b p-6">

        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">

          <div className="flex items-start gap-3">

            <div className="rounded-lg bg-indigo-50 p-2">

              <ShieldAlert className="h-5 w-5 text-indigo-600" />

            </div>

            <div>

              <h2 className="text-lg font-semibold text-slate-900">
                Continuous Risk Response
              </h2>

              <p className="mt-1 text-sm leading-6 text-slate-500">
                Deterministic response recommendations derived from
                the current risk state, treatment state, and connected
                GRC conditions.
              </p>

            </div>

          </div>


          <span
            className={`w-fit rounded-full border px-3 py-1.5 text-xs font-semibold uppercase ${priorityClass(
              response.priority
            )}`}
          >
            {response.priority} Priority
          </span>

        </div>

      </div>


      {/* ==================================================
          State Summary
      ================================================== */}

      <div className="grid gap-4 border-b p-6 md:grid-cols-2 lg:grid-cols-4">

        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">

          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            Risk State
          </p>

          <span
            className={`mt-2 inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold uppercase ${stateClass(
              response.risk_state
            )}`}
          >
            {formatLabel(response.risk_state)}
          </span>

        </div>


        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">

          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            Treatment State
          </p>

          <span
            className={`mt-2 inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold uppercase ${stateClass(
              response.treatment_state
            )}`}
          >
            {formatLabel(response.treatment_state)}
          </span>

        </div>


        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">

          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            Response Required
          </p>

          <p className="mt-2 text-lg font-bold text-slate-900">
            {response.response_required
              ? "Yes"
              : "No"}
          </p>

        </div>


        <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">

          <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
            Human Approval
          </p>

          <p className="mt-2 text-lg font-bold text-slate-900">
            {response.human_approval_required
              ? "Required"
              : "Not Required"}
          </p>

        </div>

      </div>


      {/* ==================================================
          Decisions
      ================================================== */}

      <div className="p-6">

        <div className="mb-4">

          <h3 className="font-semibold text-slate-900">
            Recommended Response
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            These decisions are derived from deterministic GRC
            rules. They do not execute automatically.
          </p>

        </div>


        {response.decisions.length === 0 ? (

          <div className="rounded-xl border border-slate-200 bg-slate-50 p-5">

            <div className="flex items-start gap-3">

              <Eye className="mt-0.5 h-5 w-5 text-slate-500" />

              <p className="text-sm leading-6 text-slate-600">
                No response decision has been generated for the
                current risk state.
              </p>

            </div>

          </div>

        ) : (

          <div className="space-y-3">

            {response.decisions.map(
              (decision, index) => (

                <DecisionCard
                  key={`${decision.decision}-${index}`}
                  decision={decision}
                />

              )
            )}

          </div>

        )}

      </div>


      {/* ==================================================
          Drivers
      ================================================== */}

      <div className="border-t p-6">

        <div className="mb-4">

          <h3 className="font-semibold text-slate-900">
            Response Drivers
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Conditions currently contributing to the response
            decision.
          </p>

        </div>

        <ReasonList
          reasons={response.reasons}
        />

      </div>


      {/* ==================================================
          Governance Boundary
      ================================================== */}

      <div className="border-t p-6">

        <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-4">

          <div className="flex items-start gap-3">

            <UserCheck className="mt-0.5 h-5 w-5 shrink-0 text-indigo-600" />

            <div>

              <p className="text-sm font-semibold text-indigo-900">
                Governance boundary
              </p>

              <p className="mt-1 text-xs leading-5 text-indigo-800">
                Continuous response recommendations are advisory.
                High-impact decisions such as risk reassessment and
                escalation require human approval and are not executed
                automatically by the platform.
              </p>

            </div>

          </div>

        </div>

      </div>

    </section>
  );
}