import {
  ClipboardCheck,
  Loader2,
  Sparkles,
} from "lucide-react";

import Can from "@/components/auth/Can";

import { Button } from "@/components/ui/button";

import { useAuditAISummary } from "@/hooks/useAuditAISummary";


interface AuditAIInsightsProps {
  auditId: number;
}


export default function AuditAIInsights({
  auditId,
}: AuditAIInsightsProps) {
  const {
    mutate: summarizeAudit,
    data: summary,
    isPending,
    error,
    reset,
  } = useAuditAISummary();


  const handleGenerate = () => {
    reset();

    summarizeAudit(auditId);
  };


  return (
    <Can
      resource="ai"
      action="use"
    >
      <section className="overflow-hidden rounded-2xl border bg-white shadow-sm">

        {/* Header */}
        <div className="border-b bg-slate-50 p-6">

          <div className="flex items-start gap-3">

            <div className="rounded-xl bg-purple-100 p-3">
              <ClipboardCheck
                size={20}
                className="text-purple-600"
              />
            </div>

            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                AI Audit Intelligence
              </h2>

              <p className="mt-1 text-sm leading-6 text-slate-500">
                Generate an AI-assisted assessment of this audit,
                including findings and remediation activity.
              </p>

              <p className="mt-2 text-xs text-slate-400">
                AI output is advisory and does not automatically change
                audit records.
              </p>
            </div>

          </div>

        </div>


        <div className="p-6">

          {/* Generate */}
          <Button
            type="button"
            onClick={handleGenerate}
            disabled={isPending}
          >
            {isPending ? (
              <Loader2
                className="mr-2 h-4 w-4 animate-spin"
              />
            ) : (
              <Sparkles
                className="mr-2 h-4 w-4"
              />
            )}

            {isPending
              ? "Generating AI Summary..."
              : "Generate AI Audit Summary"}
          </Button>


          {/* Loading */}
          {isPending && (
            <div className="mt-6 rounded-xl border border-purple-200 bg-purple-50 p-5">

              <div className="flex items-center gap-3">

                <Sparkles className="h-5 w-5 animate-pulse text-purple-600" />

                <div>
                  <p className="font-medium text-purple-700">
                    AI is reviewing this audit...
                  </p>

                  <p className="mt-1 text-sm text-purple-600">
                    Reviewing findings and corrective actions.
                  </p>
                </div>

              </div>

            </div>
          )}


          {/* Error */}
          {error && !isPending && (
            <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-5">

              <div className="flex items-start gap-3">

                <div>
                  <p className="font-medium text-red-700">
                    Audit AI summary failed.
                  </p>

                  <p className="mt-1 text-sm text-red-600">
                    The AI service could not generate the summary.
                    Please try again.
                  </p>

                  <button
                    type="button"
                    onClick={handleGenerate}
                    className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
                  >
                    Retry Summary
                  </button>
                </div>

              </div>

            </div>
          )}


          {/* Result */}
          {summary && !isPending && (
            <div className="mt-6 space-y-5">

              {/* Overall Assessment */}
              <div className="rounded-xl border bg-slate-50 p-5">

                <div className="flex items-center gap-2">

                  <Sparkles
                    size={18}
                    className="text-purple-600"
                  />

                  <h3 className="font-semibold text-slate-900">
                    AI Audit Assessment
                  </h3>

                </div>

                <p className="mt-2 leading-7 text-slate-600">
                  {summary.overall_assessment}
                </p>

              </div>


              {/* Authoritative Metrics */}
              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

                <div className="rounded-xl border bg-white p-4">

                  <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Critical Findings
                  </p>

                  <p className="mt-1 text-2xl font-bold text-red-600">
                    {summary.critical_findings}
                  </p>

                  <p className="mt-1 text-xs text-slate-400">
                    Database-derived
                  </p>

                </div>


                <div className="rounded-xl border bg-white p-4">

                  <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Open Findings
                  </p>

                  <p className="mt-1 text-2xl font-bold text-orange-600">
                    {summary.open_findings}
                  </p>

                  <p className="mt-1 text-xs text-slate-400">
                    Database-derived
                  </p>

                </div>


                <div className="rounded-xl border bg-white p-4">

                  <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Completed Actions
                  </p>

                  <p className="mt-1 text-2xl font-bold text-emerald-600">
                    {summary.completed_actions}
                  </p>

                  <p className="mt-1 text-xs text-slate-400">
                    Database-derived
                  </p>

                </div>


                <div className="rounded-xl border bg-white p-4">

                  <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                    Pending Actions
                  </p>

                  <p className="mt-1 text-2xl font-bold text-blue-600">
                    {summary.pending_actions}
                  </p>

                  <p className="mt-1 text-xs text-slate-400">
                    Database-derived
                  </p>

                </div>

              </div>


              {/* Executive Summary */}
              <div className="rounded-xl border bg-white p-5">

                <h3 className="font-semibold text-slate-900">
                  Executive Summary
                </h3>

                <p className="mt-2 whitespace-pre-wrap leading-7 text-slate-600">
                  {summary.executive_summary}
                </p>

              </div>


              {/* Priority Recommendations */}
              {summary.priority_recommendations.length > 0 && (
                <div className="rounded-xl border bg-white p-5">

                  <h3 className="mb-3 font-semibold text-slate-900">
                    Priority Recommendations
                  </h3>

                  <div className="space-y-2">

                    {summary.priority_recommendations.map(
                      (recommendation, index) => (
                        <div
                          key={`${recommendation}-${index}`}
                          className="flex gap-3 rounded-lg border bg-slate-50 p-3"
                        >

                          <span className="shrink-0 font-semibold text-purple-600">
                            {index + 1}.
                          </span>

                          <span className="text-sm leading-6 text-slate-600">
                            {recommendation}
                          </span>

                        </div>
                      )
                    )}

                  </div>

                </div>
              )}

            </div>
          )}

        </div>

      </section>
    </Can>
  );
}