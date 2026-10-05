import {
  AlertTriangle,
  Brain,
  CheckCircle2,
  RefreshCw,
  ShieldAlert,
} from "lucide-react";

import {
  type WorkflowIntelligenceExplanation,
} from "@/api/ai";

import {
  useRiskWorkflowExplanation,
} from "@/hooks/useRiskWorkflowExplanation";


// ==========================================================
// Helpers
// ==========================================================

function formatLabel(
  value: string | null | undefined
): string {
  if (!value) {
    return "—";
  }

  return value
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase()
    );
}


// ==========================================================
// Component
// ==========================================================

export default function RiskWorkflowAIExplanation({
  riskId,
  workflowId,
  explanation,
}: {
  riskId: number;
  workflowId: number;
  explanation: WorkflowIntelligenceExplanation | null;
}) {
  const {
    mutate: explainWorkflow,
    data,
    isPending,
    error,
  } = useRiskWorkflowExplanation();

  const result =
    data ?? explanation;

  return (
    <div className="mt-5 rounded-xl border border-purple-200 bg-purple-50/30">

      {/* Header */}
      <div className="border-b border-purple-100 p-5">

        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

          <div className="flex items-start gap-3">

            <div className="rounded-xl bg-purple-100 p-3">
              <Brain className="h-5 w-5 text-purple-700" />
            </div>

            <div>
              <h3 className="text-sm font-semibold text-slate-900">
                AI Workflow Explanation
              </h3>

              <p className="mt-1 text-xs leading-5 text-slate-500">
                AI explains the deterministic workflow intelligence.
                It does not change or execute the workflow.
              </p>
            </div>

          </div>

          <button
            type="button"
            onClick={() =>
              explainWorkflow({
                riskId,
                workflowId,
              })
            }
            disabled={isPending}
            className="inline-flex items-center justify-center rounded-lg border border-purple-200 bg-white px-3 py-2 text-xs font-semibold text-purple-700 transition hover:bg-purple-50 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isPending ? (
              <>
                <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                Generating...
              </>
            ) : (
              <>
                <Brain className="mr-2 h-4 w-4" />
                {result
                  ? "Regenerate Explanation"
                  : "Explain with AI"}
              </>
            )}
          </button>

        </div>

      </div>

      {/* Error */}
      {error && (
        <div className="p-5">
          <div className="rounded-xl border border-red-200 bg-red-50 p-4">
            <div className="flex items-start gap-3">
              <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-red-600" />

              <div>
                <p className="font-medium text-red-800">
                  AI explanation unavailable
                </p>

                <p className="mt-1 text-sm text-red-700">
                  {error.message}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Explanation */}
      {result && (
        <div className="space-y-5 p-5">

          {/* Authoritative snapshot */}
          <div>
            <div className="mb-3">
              <h4 className="text-sm font-semibold text-slate-900">
                Authoritative Workflow Snapshot
              </h4>

              <p className="mt-1 text-xs text-slate-500">
                These values come from the deterministic workflow
                intelligence layer, not from AI.
              </p>
            </div>

            <div className="grid gap-3 sm:grid-cols-2 lg:grid-cols-4">

              <div className="rounded-xl border bg-white p-4">
                <p className="text-xs uppercase tracking-wide text-slate-500">
                  Status
                </p>

                <p className="mt-2 text-sm font-semibold text-slate-900">
                  {formatLabel(result.status)}
                </p>
              </div>

              <div className="rounded-xl border bg-white p-4">
                <p className="text-xs uppercase tracking-wide text-slate-500">
                  Health
                </p>

                <p className="mt-2 text-sm font-semibold text-slate-900">
                  {formatLabel(result.health)}
                </p>
              </div>

              <div className="rounded-xl border bg-white p-4">
                <p className="text-xs uppercase tracking-wide text-slate-500">
                  Priority
                </p>

                <p className="mt-2 text-sm font-semibold text-slate-900">
                  {formatLabel(
                    result.decision_priority
                  )}
                </p>
              </div>

              <div className="rounded-xl border bg-white p-4">
                <p className="text-xs uppercase tracking-wide text-slate-500">
                  Dependency
                </p>

                <p className="mt-2 text-sm font-semibold text-slate-900">
                  {formatLabel(
                    result.dependency_state
                  )}
                </p>
              </div>

            </div>
          </div>

          {/* Explanation */}
          <div className="rounded-xl border border-purple-100 bg-white p-5">

            <div className="flex items-start gap-3">

              <Brain className="mt-0.5 h-5 w-5 shrink-0 text-purple-600" />

              <div>
                <h4 className="font-semibold text-slate-900">
                  Explanation
                </h4>

                <p className="mt-2 text-sm leading-7 text-slate-700">
                  {result.explanation}
                </p>
              </div>

            </div>

          </div>

          {/* Drivers / Review */}
          <div className="grid gap-5 md:grid-cols-2">

            <div className="rounded-xl border bg-white p-5">

              <div className="mb-4 flex items-center gap-2">
                <ShieldAlert className="h-5 w-5 text-orange-600" />

                <h4 className="font-semibold text-slate-900">
                  Key Drivers
                </h4>
              </div>

              <div className="space-y-2">

                {result.key_drivers.map(
                  (driver, index) => (
                    <div
                      key={`${driver}-${index}`}
                      className="rounded-lg bg-slate-50 p-3 text-sm leading-6 text-slate-700"
                    >
                      {driver}
                    </div>
                  )
                )}

              </div>

            </div>

            <div className="rounded-xl border bg-white p-5">

              <div className="mb-4 flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-600" />

                <h4 className="font-semibold text-slate-900">
                  Human Review Areas
                </h4>
              </div>

              <div className="space-y-2">

                {result.review_areas.map(
                  (area, index) => (
                    <div
                      key={`${area}-${index}`}
                      className="rounded-lg bg-slate-50 p-3 text-sm leading-6 text-slate-700"
                    >
                      {area}
                    </div>
                  )
                )}

              </div>

            </div>

          </div>

          {/* Governance */}
          <div className="rounded-xl border border-slate-200 bg-slate-50 p-4">

            <p className="text-xs font-semibold uppercase tracking-wide text-slate-500">
              AI Governance Boundary
            </p>

            <p className="mt-2 text-sm leading-6 text-slate-600">
              AI provides an explanatory interpretation of the
              deterministic workflow intelligence. The workflow
              status, priority, bottleneck, escalation recommendation,
              dependency state, approval requirements, and execution
              controls remain authoritative outside the AI layer.
            </p>

          </div>

        </div>
      )}

    </div>
  );
}