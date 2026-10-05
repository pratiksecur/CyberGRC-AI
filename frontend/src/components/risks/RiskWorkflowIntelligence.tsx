import {
  AlertTriangle,
  CheckCircle2,
  Clock3,
  GitBranch,
  ShieldAlert,
  Timer,
  UserCheck,
} from "lucide-react";

import type {
  RiskResponseWorkflowIntelligence,
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


function formatDuration(
  seconds: number | null
) {
  if (
    seconds === null ||
    !Number.isFinite(seconds)
  ) {
    return "—";
  }

  const totalMinutes =
    Math.floor(seconds / 60);

  if (totalMinutes < 1) {
    return "< 1 min";
  }

  const days =
    Math.floor(totalMinutes / 1440);

  const hours =
    Math.floor(
      (totalMinutes % 1440) / 60
    );

  const minutes =
    totalMinutes % 60;

  const parts: string[] = [];

  if (days > 0) {
    parts.push(`${days}d`);
  }

  if (hours > 0) {
    parts.push(`${hours}h`);
  }

  if (
    minutes > 0 &&
    parts.length < 2
  ) {
    parts.push(`${minutes}m`);
  }

  return parts.join(" ") || "< 1 min";
}


function healthClass(
  health: string
) {
  switch (health) {

    case "HEALTHY":
      return "border-emerald-200 bg-emerald-50 text-emerald-700";

    case "AGING":
      return "border-amber-200 bg-amber-50 text-amber-700";

    case "OVERDUE":
      return "border-red-200 bg-red-50 text-red-700";

    case "BLOCKED":
      return "border-red-300 bg-red-100 text-red-800";

    case "ESCALATED":
      return "border-orange-300 bg-orange-100 text-orange-800";

    case "COMPLETED":
      return "border-emerald-200 bg-emerald-50 text-emerald-700";

    case "CANCELLED":
      return "border-slate-200 bg-slate-100 text-slate-600";

    default:
      return "border-slate-200 bg-slate-50 text-slate-700";
  }
}


function priorityClass(
  value: string | null
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
      return "border-slate-200 bg-slate-100 text-slate-600";
  }
}


function escalationClass(
  value: string
) {
  switch (value) {

    case "ESCALATE":
      return "border-red-300 bg-red-100 text-red-800";

    case "REVIEW":
      return "border-orange-300 bg-orange-100 text-orange-800";

    case "NONE":
    default:
      return "border-emerald-200 bg-emerald-50 text-emerald-700";
  }
}


function dependencyClass(
  value: string
) {
  switch (value) {

    case "BLOCKING":
      return "border-red-300 bg-red-100 text-red-800";

    case "ATTENTION_REQUIRED":
      return "border-orange-300 bg-orange-100 text-orange-800";

    case "INCOMPLETE":
      return "border-yellow-300 bg-yellow-100 text-yellow-800";

    case "MISSING":
      return "border-red-200 bg-red-50 text-red-700";

    case "AVAILABLE":
      return "border-emerald-200 bg-emerald-50 text-emerald-700";

    case "NO_DEPENDENCY":
    default:
      return "border-slate-200 bg-slate-100 text-slate-600";
  }
}


function MetricCard({
  label,
  value,
  detail,
  icon: Icon,
}: {
  label: string;
  value: string;
  detail?: string;
  icon: typeof Clock3;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">

      <div className="flex items-center justify-between gap-3">

        <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          {label}
        </p>

        <Icon className="h-4 w-4 text-slate-400" />

      </div>

      <p className="mt-2 text-lg font-bold text-slate-900">
        {value}
      </p>

      {detail && (
        <p className="mt-1 text-xs text-slate-500">
          {detail}
        </p>
      )}

    </div>
  );
}


// ==========================================================
// Component
// ==========================================================

interface RiskWorkflowIntelligenceProps {
  intelligence:
    RiskResponseWorkflowIntelligence;
}

export default function RiskWorkflowIntelligence({
  intelligence,
}: RiskWorkflowIntelligenceProps) {

  return (
    <section className="rounded-2xl border border-indigo-200 bg-white shadow-sm">

      {/* ==================================================
          Header
      ================================================== */}

      <div className="border-b border-indigo-100 bg-indigo-50/40 p-6">

        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">

          <div className="flex items-start gap-3">

            <div className="rounded-xl bg-indigo-100 p-3">

              <GitBranch className="h-5 w-5 text-indigo-600" />

            </div>

            <div>

              <h3 className="text-lg font-semibold text-slate-900">
                Workflow Intelligence
              </h3>

              <p className="mt-1 text-sm leading-6 text-slate-500">
                Deterministic intelligence describing workflow health,
                ageing, priority, bottlenecks, escalation, and
                target-resource dependency.
              </p>

            </div>

          </div>


          <span
            className={`w-fit rounded-full border px-3 py-1.5 text-xs font-semibold uppercase ${healthClass(
              intelligence.health
            )}`}
          >
            {formatLabel(
              intelligence.health
            )}
          </span>

        </div>

      </div>


      {/* ==================================================
          Lifecycle
      ================================================== */}

      <div className="border-b p-6">

        <div className="mb-4">

          <h4 className="font-semibold text-slate-900">
            Lifecycle
          </h4>

          <p className="mt-1 text-sm text-slate-500">
            Current timing and lifecycle position of this workflow.
          </p>

        </div>


        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <MetricCard
            label="Age"
            value={`${intelligence.age_days.toFixed(1)} days`}
            detail={`${formatDuration(
              intelligence.age_seconds
            )} elapsed`}
            icon={Clock3}
          />

          <MetricCard
            label="Time to Start"
            value={formatDuration(
              intelligence.time_to_start_seconds
            )}
            detail={
              intelligence.started
                ? "Workflow started"
                : "Awaiting start"
            }
            icon={Timer}
          />

          <MetricCard
            label="Time in Progress"
            value={formatDuration(
              intelligence.time_in_progress_seconds
            )}
            detail={
              intelligence.started
                ? "Since workflow start"
                : "Not started"
            }
            icon={Clock3}
          />

          <MetricCard
            label="Lifecycle Duration"
            value={formatDuration(
              intelligence.lifecycle_duration_seconds
            )}
            detail={
              intelligence.terminal
                ? "Completed lifecycle"
                : "Lifecycle still active"
            }
            icon={CheckCircle2}
          />

        </div>

      </div>


      {/* ==================================================
          Priority + Bottleneck
      ================================================== */}

      <div className="border-b p-6">

        <div className="grid gap-6 md:grid-cols-2">

          {/* Priority */}

          <div className="rounded-xl border border-slate-200 p-5">

            <div className="flex items-start gap-3">

              <ShieldAlert className="mt-0.5 h-5 w-5 text-orange-600" />

              <div className="min-w-0">

                <h4 className="font-semibold text-slate-900">
                  Workflow Priority
                </h4>

                <p className="mt-1 text-sm text-slate-500">
                  Priority inherited from the governed response decision.
                </p>

              </div>

            </div>


            <div className="mt-4 flex flex-wrap items-center gap-3">

              <span
                className={`rounded-full border px-3 py-1.5 text-xs font-semibold uppercase ${priorityClass(
                  intelligence.decision_priority
                )}`}
              >
                {intelligence.decision_priority
                  ? formatLabel(
                      intelligence.decision_priority
                    )
                  : "Not Available"}
              </span>

              {intelligence.priority_rank !== null && (
                <span className="text-xs font-medium text-slate-500">
                  Rank {intelligence.priority_rank}
                </span>
              )}

            </div>


            {intelligence.governance_level && (
              <p className="mt-3 text-xs text-slate-500">
                Governance:{" "}
                <span className="font-medium text-slate-700">
                  {formatLabel(
                    intelligence.governance_level
                  )}
                </span>
              </p>
            )}


            {intelligence.priority_reason_codes.length > 0 && (

              <div className="mt-4 flex flex-wrap gap-2">

                {intelligence.priority_reason_codes.map(
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

            )}

          </div>


          {/* Bottleneck */}

          <div className="rounded-xl border border-slate-200 p-5">

            <div className="flex items-start gap-3">

              <AlertTriangle
                className={`mt-0.5 h-5 w-5 ${
                  intelligence.bottlenecked
                    ? "text-red-600"
                    : "text-emerald-600"
                }`}
              />

              <div>

                <h4 className="font-semibold text-slate-900">
                  Bottleneck
                </h4>

                <p className="mt-1 text-sm text-slate-500">
                  Deterministic workflow ageing and lifecycle analysis.
                </p>

              </div>

            </div>


            <div className="mt-4">

              <span
                className={`rounded-full border px-3 py-1.5 text-xs font-semibold uppercase ${
                  intelligence.bottlenecked
                    ? "border-red-300 bg-red-100 text-red-800"
                    : "border-emerald-200 bg-emerald-50 text-emerald-700"
                }`}
              >
                {intelligence.bottlenecked
                  ? "Attention Required"
                  : "No Bottleneck"}
              </span>

            </div>


            {intelligence.bottleneck_reason_codes.length > 0 && (

              <div className="mt-4 flex flex-wrap gap-2">

                {intelligence.bottleneck_reason_codes.map(
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

            )}

          </div>

        </div>

      </div>


      {/* ==================================================
          Escalation
      ================================================== */}

      <div className="border-b p-6">

        <div className="rounded-xl border border-slate-200 p-5">

          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">

            <div className="flex items-start gap-3">

              <UserCheck
                className={`mt-0.5 h-5 w-5 ${
                  intelligence.escalation_recommendation === "ESCALATE"
                    ? "text-red-600"
                    : intelligence.escalation_recommendation === "REVIEW"
                      ? "text-orange-600"
                      : "text-emerald-600"
                }`}
              />

              <div>

                <h4 className="font-semibold text-slate-900">
                  Escalation Recommendation
                </h4>

                <p className="mt-1 text-sm leading-6 text-slate-500">
                  This is a deterministic recommendation. It does not
                  execute escalation automatically.
                </p>

              </div>

            </div>


            <span
              className={`w-fit rounded-full border px-3 py-1.5 text-xs font-semibold uppercase ${escalationClass(
                intelligence.escalation_recommendation
              )}`}
            >
              {formatLabel(
                intelligence.escalation_recommendation
              )}
            </span>

          </div>


          {intelligence.escalation_reason_codes.length > 0 && (

            <div className="mt-4 flex flex-wrap gap-2">

              {intelligence.escalation_reason_codes.map(
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

          )}


          {intelligence.escalation_requires_human_review && (

            <div className="mt-4 flex items-start gap-2 rounded-lg border border-orange-200 bg-orange-50 p-3">

              <UserCheck className="mt-0.5 h-4 w-4 shrink-0 text-orange-600" />

              <div>

                <p className="text-sm font-semibold text-orange-800">
                  Human review required
                </p>

                <p className="mt-1 text-xs leading-5 text-orange-700">
                  The intelligence layer cannot approve or execute
                  this escalation. A governed human decision remains
                  required.
                </p>

              </div>

            </div>

          )}

        </div>

      </div>


      {/* ==================================================
          Dependency
      ================================================== */}

      <div className="p-6">

        <div className="rounded-xl border border-slate-200 p-5">

          <div className="flex flex-col justify-between gap-4 md:flex-row md:items-start">

            <div className="flex items-start gap-3">

              <GitBranch
                className={`mt-0.5 h-5 w-5 ${
                  dependencyClass(
                    intelligence.dependency_state
                  ).includes("red")
                    ? "text-red-600"
                    : "text-indigo-600"
                }`}
              />

              <div>

                <h4 className="font-semibold text-slate-900">
                  Target Dependency
                </h4>

                <p className="mt-1 text-sm leading-6 text-slate-500">
                  Dependency information identifies the resource
                  targeted by the governed workflow.
                </p>

              </div>

            </div>


            <span
              className={`w-fit rounded-full border px-3 py-1.5 text-xs font-semibold uppercase ${dependencyClass(
                intelligence.dependency_state
              )}`}
            >
              {formatLabel(
                intelligence.dependency_state
              )}
            </span>

          </div>


          {intelligence.dependency_target_type && (

            <div className="mt-4 grid gap-4 sm:grid-cols-2">

              <div className="rounded-lg bg-slate-50 p-3">

                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Target Type
                </p>

                <p className="mt-1 text-sm font-semibold text-slate-800">
                  {formatLabel(
                    intelligence.dependency_target_type
                  )}
                </p>

              </div>


              <div className="rounded-lg bg-slate-50 p-3">

                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                  Target ID
                </p>

                <p className="mt-1 text-sm font-semibold text-slate-800">
                  {intelligence.dependency_target_id !== null
                    ? `#${intelligence.dependency_target_id}`
                    : "—"}
                </p>

              </div>

            </div>

          )}


          {intelligence.dependency_reason_codes.length > 0 && (

            <div className="mt-4 flex flex-wrap gap-2">

              {intelligence.dependency_reason_codes.map(
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

          )}

        </div>

      </div>


      {/* ==================================================
          Governance Boundary
      ================================================== */}

      <div className="border-t p-6">

        <div className="rounded-xl border border-indigo-200 bg-indigo-50 p-4">

          <div className="flex items-start gap-3">

            <ShieldAlert className="mt-0.5 h-5 w-5 shrink-0 text-indigo-600" />

            <div>

              <p className="text-sm font-semibold text-indigo-900">
                Intelligence governance boundary
              </p>

              <p className="mt-1 text-xs leading-5 text-indigo-800">
                Workflow intelligence is read-only. It describes the
                current governed workflow and provides deterministic
                recommendations. It does not change the workflow,
                approve actions, or mutate the underlying GRC resource.
              </p>

            </div>

          </div>

        </div>

      </div>

    </section>
  );
}