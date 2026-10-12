import React from "react";

import {
  AlertTriangle,
  ArrowUpRight,
  CheckCircle2,
  Clock3,
  GitBranch,
  Loader2,
  ShieldAlert,
  Workflow,
  XCircle,
} from "lucide-react";

import type {
  RiskResponseWorkflow,
} from "@/api/risks";

import {
  useRiskWorkflowIntelligence,
} from "@/hooks/useRiskWorkflowIntelligence";


// ==========================================================
// Helpers
// ==========================================================

function formatLabel(value: string | null | undefined): string {
  if (!value) {
    return "—";
  }

  return value
    .toLowerCase()
    .replace(/_/g, " ")
    .replace(/\b\w/g, (char) =>
      char.toUpperCase()
    );
}


function formatDate(
  value: string | null | undefined
): string {
  if (!value) {
    return "—";
  }

  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}


function formatDuration(
  seconds: number | null | undefined
): string {
  if (
    seconds === null ||
    seconds === undefined ||
    Number.isNaN(seconds)
  ) {
    return "—";
  }

  const totalSeconds = Math.max(
    0,
    Math.round(seconds)
  );

  const days = Math.floor(
    totalSeconds / 86400
  );

  const hours = Math.floor(
    (totalSeconds % 86400) / 3600
  );

  const minutes = Math.floor(
    (totalSeconds % 3600) / 60
  );

  if (days > 0) {
    return `${days}d ${hours}h`;
  }

  if (hours > 0) {
    return `${hours}h ${minutes}m`;
  }

  if (minutes > 0) {
    return `${minutes}m`;
  }

  return `${totalSeconds}s`;
}


function statusClass(
  status: string
): string {
  switch (status) {
    case "COMPLETED":
      return "bg-emerald-50 text-emerald-700 border-emerald-200";

    case "CANCELLED":
      return "bg-slate-100 text-slate-600 border-slate-200";

    case "IN_PROGRESS":
      return "bg-blue-50 text-blue-700 border-blue-200";

    case "OPEN":
    default:
      return "bg-amber-50 text-amber-700 border-amber-200";
  }
}


function healthClass(
  health: string
): string {
  switch (health) {
    case "HEALTHY":
      return "text-emerald-700";

    case "AGING":
      return "text-amber-700";

    case "OVERDUE":
      return "text-orange-700";

    case "BLOCKED":
    case "ESCALATED":
      return "text-red-700";

    case "COMPLETED":
      return "text-emerald-700";

    case "CANCELLED":
      return "text-slate-500";

    default:
      return "text-slate-700";
  }
}


function priorityClass(
  priority: string | null
): string {
  switch (priority) {
    case "CRITICAL":
      return "bg-red-50 text-red-700 border-red-200";

    case "HIGH":
      return "bg-orange-50 text-orange-700 border-orange-200";

    case "MEDIUM":
      return "bg-amber-50 text-amber-700 border-amber-200";

    case "LOW":
      return "bg-slate-100 text-slate-600 border-slate-200";

    default:
      return "bg-slate-100 text-slate-500 border-slate-200";
  }
}


function escalationClass(
  recommendation: string
): string {
  switch (recommendation) {
    case "ESCALATE":
      return "bg-red-50 text-red-700 border-red-200";

    case "REVIEW":
      return "bg-amber-50 text-amber-700 border-amber-200";

    default:
      return "bg-emerald-50 text-emerald-700 border-emerald-200";
  }
}


function dependencyClass(
  state: string
): string {
  switch (state) {
    case "BLOCKING":
    case "ATTENTION_REQUIRED":
    case "MISSING":
      return "text-red-700";

    case "INCOMPLETE":
      return "text-amber-700";

    case "AVAILABLE":
      return "text-emerald-700";

    default:
      return "text-slate-500";
  }
}


// ==========================================================
// Metric Card
// ==========================================================

function MetricCard({
  label,
  value,
  icon,
}: {
  label: string;
  value: string;
  icon: React.ReactNode;
}) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4">
      <div className="flex items-center gap-2 text-xs font-medium uppercase tracking-wide text-slate-500">
        {icon}
        <span>{label}</span>
      </div>

      <div className="mt-2 text-sm font-semibold text-slate-900">
        {value}
      </div>
    </div>
  );
}


// ==========================================================
// Workflow Intelligence
// ==========================================================

function WorkflowIntelligence({
  riskId,
  workflowId,
}: {
  riskId: number;
  workflowId: number;
}) {
  const {
    data: intelligence,
    isLoading,
    isError,
  } = useRiskWorkflowIntelligence(
    riskId,
    workflowId
  );

  if (isLoading) {
    return (
      <div className="mt-4 rounded-xl border border-slate-200 bg-slate-50 p-5">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Loader2
            className="h-4 w-4 animate-spin"
          />
          Loading workflow intelligence...
        </div>
      </div>
    );
  }

  if (isError || !intelligence) {
    return (
      <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4">
        <div className="flex items-center gap-2 text-sm text-red-700">
          <AlertTriangle className="h-4 w-4" />
          Workflow intelligence could not be loaded.
        </div>
      </div>
    );
  }

  return (
    <div className="mt-4 space-y-4">

      {/* Lifecycle */}
      <div>
        <div className="mb-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
          Workflow Intelligence
        </div>

        <div className="grid grid-cols-1 gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <MetricCard
            label="Age"
            value={`${intelligence.age_days.toFixed(1)} days`}
            icon={
              <Clock3 className="h-4 w-4" />
            }
          />

          <MetricCard
            label="Time to Start"
            value={formatDuration(
              intelligence.time_to_start_seconds
            )}
            icon={
              <Clock3 className="h-4 w-4" />
            }
          />

          <MetricCard
            label="Time In Progress"
            value={formatDuration(
              intelligence.time_in_progress_seconds
            )}
            icon={
              <Workflow className="h-4 w-4" />
            }
          />

          <MetricCard
            label="Lifecycle Duration"
            value={formatDuration(
              intelligence.lifecycle_duration_seconds
            )}
            icon={
              <CheckCircle2 className="h-4 w-4" />
            }
          />
        </div>
      </div>

      {/* Priority / Health */}
      <div className="grid grid-cols-1 gap-4 lg:grid-cols-2">

        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="mb-3 flex items-center gap-2">
            <ShieldAlert className="h-4 w-4 text-slate-500" />

            <span className="text-sm font-semibold text-slate-900">
              Priority & Health
            </span>
          </div>

          <div className="flex flex-wrap gap-2">

            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold ${priorityClass(
                intelligence.decision_priority
              )}`}
            >
              {formatLabel(
                intelligence.decision_priority
              )}
            </span>

            <span
              className={`rounded-full border px-3 py-1 text-xs font-semibold ${statusClass(
                intelligence.status
              )}`}
            >
              {formatLabel(
                intelligence.status
              )}
            </span>

            <span
              className={`px-1 py-1 text-xs font-semibold ${healthClass(
                intelligence.health
              )}`}
            >
              {formatLabel(
                intelligence.health
              )}
            </span>
          </div>

          {intelligence.reason_codes.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {intelligence.reason_codes.map(
                (reason) => (
                  <span
                    key={reason}
                    className="rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-600"
                  >
                    {formatLabel(reason)}
                  </span>
                )
              )}
            </div>
          )}
        </div>

        {/* Bottleneck */}
        <div className="rounded-xl border border-slate-200 bg-white p-4">
          <div className="mb-3 flex items-center gap-2">
            <AlertTriangle className="h-4 w-4 text-slate-500" />

            <span className="text-sm font-semibold text-slate-900">
              Bottleneck
            </span>
          </div>

          <div className="flex items-center gap-2">
            {intelligence.bottlenecked ? (
              <>
                <AlertTriangle className="h-4 w-4 text-orange-600" />

                <span className="text-sm font-semibold text-orange-700">
                  Attention required
                </span>
              </>
            ) : (
              <>
                <CheckCircle2 className="h-4 w-4 text-emerald-600" />

                <span className="text-sm font-semibold text-emerald-700">
                  No bottleneck detected
                </span>
              </>
            )}
          </div>

          {intelligence.bottleneck_reason_codes.length > 0 && (
            <div className="mt-3 flex flex-wrap gap-2">
              {intelligence.bottleneck_reason_codes.map(
                (reason) => (
                  <span
                    key={reason}
                    className="rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-600"
                  >
                    {formatLabel(reason)}
                  </span>
                )
              )}
            </div>
          )}
        </div>
      </div>

      {/* Escalation */}
      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <div className="mb-3 flex items-center gap-2">
          <ArrowUpRight className="h-4 w-4 text-slate-500" />

          <span className="text-sm font-semibold text-slate-900">
            Escalation Recommendation
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-2">
          <span
            className={`rounded-full border px-3 py-1 text-xs font-semibold ${escalationClass(
              intelligence.escalation_recommendation
            )}`}
          >
            {formatLabel(
              intelligence.escalation_recommendation
            )}
          </span>

          {intelligence.escalation_requires_human_review && (
            <span className="rounded-full border border-red-200 bg-red-50 px-3 py-1 text-xs font-semibold text-red-700">
              Human review required
            </span>
          )}
        </div>

        {intelligence.escalation_reason_codes.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {intelligence.escalation_reason_codes.map(
              (reason) => (
                <span
                  key={reason}
                  className="rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-600"
                >
                  {formatLabel(reason)}
                </span>
              )
            )}
          </div>
        )}
      </div>

      {/* Dependency */}
      <div className="rounded-xl border border-slate-200 bg-white p-4">
        <div className="mb-3 flex items-center gap-2">
          <GitBranch className="h-4 w-4 text-slate-500" />

          <span className="text-sm font-semibold text-slate-900">
            Dependency
          </span>
        </div>

        <div className="flex flex-wrap items-center gap-3">

          <span
            className={`text-sm font-semibold ${dependencyClass(
              intelligence.dependency_state
            )}`}
          >
            {formatLabel(
              intelligence.dependency_state
            )}
          </span>

          {intelligence.dependency_target_type && (
            <span className="text-sm text-slate-600">
              Target:{" "}
              <span className="font-medium text-slate-900">
                {formatLabel(
                  intelligence.dependency_target_type
                )}
              </span>
              {intelligence.dependency_target_id !== null &&
                ` #${intelligence.dependency_target_id}`}
            </span>
          )}
        </div>

        {intelligence.dependency_reason_codes.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            {intelligence.dependency_reason_codes.map(
              (reason) => (
                <span
                  key={reason}
                  className="rounded-md bg-slate-100 px-2 py-1 text-xs text-slate-600"
                >
                  {formatLabel(reason)}
                </span>
              )
            )}
          </div>
        )}
      </div>

      {/* Governance */}
      <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">
        <div className="text-xs font-semibold uppercase tracking-wide text-slate-500">
          Governance Boundary
        </div>

        <p className="mt-2 text-sm leading-6 text-slate-600">
          Workflow intelligence is read-only. It describes
          lifecycle state, priority, bottlenecks, escalation
          recommendations, and dependencies. It does not execute
          or mutate the underlying GRC resource.
        </p>

        {intelligence.governance_level && (
          <div className="mt-3 text-xs text-slate-500">
            Governance level:{" "}
            <span className="font-semibold text-slate-700">
              {formatLabel(
                intelligence.governance_level
              )}
            </span>
          </div>
        )}
      </div>
    </div>
  );
}


// ==========================================================
// Workflow Card
// ==========================================================

function WorkflowCard({
  riskId,
  workflow,
  selected,
  onSelect,
}: {
  riskId: number;
  workflow: RiskResponseWorkflow;
  selected: boolean;
  onSelect: () => void;
}) {
  return (
    <div
      className={`rounded-xl border bg-white transition ${
        selected
          ? "border-slate-400 shadow-sm"
          : "border-slate-200"
      }`}
    >
      <button
        type="button"
        onClick={onSelect}
        className="w-full text-left"
      >
        <div className="p-4">

          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">

            <div className="min-w-0">
              <div className="flex items-center gap-2">
                <Workflow className="h-4 w-4 shrink-0 text-slate-500" />

                <h4 className="truncate text-sm font-semibold text-slate-900">
                  {workflow.title}
                </h4>
              </div>

              <p className="mt-1 text-xs text-slate-500">
                {formatLabel(
                  workflow.workflow_type
                )}
              </p>
            </div>

            <span
              className={`w-fit rounded-full border px-3 py-1 text-xs font-semibold ${statusClass(
                workflow.status
              )}`}
            >
              {formatLabel(
                workflow.status
              )}
            </span>
          </div>

          <p className="mt-3 text-sm leading-6 text-slate-600">
            {workflow.description}
          </p>

          <div className="mt-4 grid grid-cols-1 gap-3 sm:grid-cols-3">

            <div>
              <div className="text-[11px] font-medium uppercase tracking-wide text-slate-400">
                Target
              </div>

              <div className="mt-1 text-xs font-medium text-slate-700">
                {formatLabel(
                  workflow.target_type
                )}

                {workflow.target_id !== null &&
                  ` #${workflow.target_id}`}
              </div>
            </div>

            <div>
              <div className="text-[11px] font-medium uppercase tracking-wide text-slate-400">
                Created
              </div>

              <div className="mt-1 text-xs text-slate-700">
                {formatDate(
                  workflow.created_at
                )}
              </div>
            </div>

            <div>
              <div className="text-[11px] font-medium uppercase tracking-wide text-slate-400">
                Updated
              </div>

              <div className="mt-1 text-xs text-slate-700">
                {formatDate(
                  workflow.updated_at
                )}
              </div>
            </div>

          </div>
        </div>
      </button>

      {selected && (
        <div className="border-t border-slate-200 px-4 pb-4">
          <WorkflowIntelligence
            riskId={riskId}
            workflowId={workflow.id}
          />
        </div>
      )}
    </div>
  );
}


// ==========================================================
// Main Component
// ==========================================================

export default function RiskResponseWorkflows({
  riskId,
  workflows,
  isLoading,
  isError,
}: {
  riskId: number;
  workflows: RiskResponseWorkflow[];
  isLoading: boolean;
  isError: boolean;
}) {
  const [selectedWorkflowId, setSelectedWorkflowId] =
    React.useState<number | null>(
      workflows[0]?.id ?? null
    );

  const activeWorkflowId =
    workflows.some(
      (workflow) =>
        workflow.id === selectedWorkflowId
    )
      ? selectedWorkflowId
      : (workflows[0]?.id ?? null);

  if (isLoading) {
    return (
      <section className="rounded-2xl border border-slate-200 bg-white p-6">
        <div className="flex items-center gap-2 text-sm text-slate-500">
          <Loader2
            className="h-4 w-4 animate-spin"
          />
          Loading governed response workflows...
        </div>
      </section>
    );
  }

  if (isError) {
    return (
      <section className="rounded-2xl border border-red-200 bg-red-50 p-6">
        <div className="flex items-center gap-2 text-sm text-red-700">
          <AlertTriangle className="h-4 w-4" />
          Governed response workflows could not be loaded.
        </div>
      </section>
    );
  }

  return (
    <section className="rounded-2xl border border-slate-200 bg-white p-6">

      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">

        <div>
          <div className="flex items-center gap-2">
            <Workflow className="h-5 w-5 text-slate-600" />

            <h2 className="text-lg font-semibold text-slate-900">
              Governed Response Workflows
            </h2>
          </div>

          <p className="mt-1 text-sm text-slate-500">
            Read-only visibility into governed response
            workflows and their current intelligence.
          </p>
        </div>

        <div className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-600">
          {workflows.length}{" "}
          {workflows.length === 1
            ? "workflow"
            : "workflows"}
        </div>
      </div>

      {workflows.length === 0 ? (
        <div className="mt-6 rounded-xl border border-dashed border-slate-300 bg-slate-50 p-8 text-center">
          <XCircle className="mx-auto h-8 w-8 text-slate-400" />

          <p className="mt-3 text-sm font-medium text-slate-700">
            No governed response workflows
          </p>

          <p className="mt-1 text-xs text-slate-500">
            No governed workflow has been created for this risk.
          </p>
        </div>
      ) : (
        <div className="mt-6 space-y-4">
          {workflows.map((workflow) => (
            <WorkflowCard
              key={workflow.id}
              riskId={riskId}
              workflow={workflow}
              selected={
                activeWorkflowId ===
                workflow.id
              }
              onSelect={() =>
                setSelectedWorkflowId(
                  workflow.id
                )
              }
            />
          ))}
        </div>
      )}
    </section>
  );
}