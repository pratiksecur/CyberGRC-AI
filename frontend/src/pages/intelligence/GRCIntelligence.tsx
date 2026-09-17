import {
  Activity,
  AlertTriangle,
  ArrowRight,
  Brain,
  CheckCircle2,
  ClipboardCheck,
  FileCheck2,
  RefreshCw,
  ShieldAlert,
  Target,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useGRCIntelligence } from "@/hooks/useGRCIntelligence";


// ==========================================================
// Helpers
// ==========================================================

function riskScoreClass(score: number) {
  if (score >= 20) {
    return "bg-red-100 text-red-700 border-red-200";
  }

  if (score >= 15) {
    return "bg-orange-100 text-orange-700 border-orange-200";
  }

  if (score >= 8) {
    return "bg-yellow-100 text-yellow-700 border-yellow-200";
  }

  return "bg-green-100 text-green-700 border-green-200";
}


function formatPercent(value: number) {
  return `${value.toFixed(1)}%`;
}


// ==========================================================
// Page
// ==========================================================

export default function GRCIntelligence() {
  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
    refetch,
    isFetching,
  } = useGRCIntelligence();


  // ========================================================
  // Loading
  // ========================================================

  if (isLoading) {
    return (
      <AppLayout>
        <div className="mx-auto max-w-7xl space-y-6">

          <div className="h-10 w-80 animate-pulse rounded-lg bg-slate-200" />

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 8 }).map(
              (_, index) => (
                <div
                  key={index}
                  className="h-28 animate-pulse rounded-xl bg-slate-100"
                />
              )
            )}
          </div>

          <div className="h-96 animate-pulse rounded-xl bg-slate-100" />

        </div>
      </AppLayout>
    );
  }


  // ========================================================
  // Error
  // ========================================================

  if (error || !data) {
    return (
      <AppLayout>
        <div className="mx-auto max-w-4xl">

          <div className="rounded-2xl border border-red-200 bg-red-50 p-6">

            <div className="flex items-start gap-3">

              <AlertTriangle className="mt-0.5 h-6 w-6 text-red-600" />

              <div className="flex-1">

                <h2 className="font-semibold text-red-700">
                  GRC Intelligence Unavailable
                </h2>

                <p className="mt-1 text-sm leading-6 text-red-600">
                  The intelligence overview could not be loaded.
                  Please try again.
                </p>

                <button
                  type="button"
                  onClick={() => refetch()}
                  className="mt-4 inline-flex items-center rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Try Again
                </button>

              </div>

            </div>

          </div>

        </div>
      </AppLayout>
    );
  }


  const metrics = data.metrics;


  return (
    <AppLayout>

      <div className="mx-auto max-w-7xl space-y-8">

        {/* ==================================================
            Header
        ================================================== */}

        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-indigo-50 p-3">
              <Brain className="h-7 w-7 text-indigo-600" />
            </div>

            <div>

              <h1 className="text-3xl font-bold text-slate-900">
                GRC Intelligence
              </h1>

              <p className="mt-1 text-slate-500">
                Connected risk, control, evidence, finding, and remediation intelligence.
              </p>

            </div>

          </div>

          <button
            type="button"
            onClick={() => refetch()}
            disabled={isFetching}
            className="inline-flex items-center justify-center rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-50"
          >
            <RefreshCw
              className={`mr-2 h-4 w-4 ${
                isFetching
                  ? "animate-spin"
                  : ""
              }`}
            />
            Refresh
          </button>

        </div>


        {/* ==================================================
            Metrics
        ================================================== */}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <MetricCard
            title="Total Risks"
            value={metrics.total_risks}
            icon={ShieldAlert}
          />

          <MetricCard
            title="Critical Risks"
            value={metrics.critical_risks}
            icon={AlertTriangle}
            emphasis="critical"
          />

          <MetricCard
            title="Risks With Controls"
            value={metrics.risks_with_controls}
            icon={Target}
          />

          <MetricCard
            title="Risks With Evidence"
            value={metrics.risks_with_evidence}
            icon={FileCheck2}
          />

          <MetricCard
            title="Total Findings"
            value={metrics.total_findings}
            icon={ClipboardCheck}
          />

          <MetricCard
            title="Open Findings"
            value={metrics.open_findings}
            icon={Activity}
          />

          <MetricCard
            title="Open Actions"
            value={metrics.open_actions}
            icon={ArrowRight}
          />

          <MetricCard
            title="Remediation Complete"
            value={formatPercent(
              metrics.remediation_completion_percent
            )}
            icon={CheckCircle2}
          />

        </div>


        {/* ==================================================
            Intelligence explanation
        ================================================== */}

        <div className="rounded-2xl border border-slate-700 bg-slate-900 p-6">
            <div className="flex items-start gap-3">
                <div className="rounded-lg bg-slate-950 p-2 shadow-sm">
                <Brain className="h-5 w-5 text-indigo-500" />
                </div>

                <div>
                <h2 className="text-sm font-semibold text-white">
                    Risk-to-Remediation Intelligence
                </h2>

                <p className="mt-1 max-w-4xl text-sm leading-6 text-slate-300">
                    CyberGRC AI connects risks with their controls,
                    evidence, frameworks, audit findings, and corrective
                    actions. The intelligence view is generated from the
                    current database state and respects your existing
                    resource visibility.
                </p>
                </div>
            </div>
        </div>


        {/* ==================================================
            Risk Intelligence
        ================================================== */}

        <div className="rounded-2xl border bg-white shadow-sm">

          <div className="border-b p-6">

            <div className="flex items-center justify-between">

              <div>

                <h2 className="text-lg font-semibold text-slate-900">
                  Risk Intelligence
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Connected GRC intelligence for visible risks.
                </p>

              </div>

              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                {data.risks.length} risks
              </span>

            </div>

          </div>


          <div className="overflow-x-auto">

            {data.risks.length === 0 ? (

              <div className="p-10 text-center text-sm text-slate-500">
                No visible risks are available for intelligence analysis.
              </div>

            ) : (

              <table className="w-full min-w-[900px]">

                <thead className="border-b bg-slate-50">

                  <tr>

                    <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Risk
                    </th>

                    <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Score
                    </th>

                    <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Controls
                    </th>

                    <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Evidence
                    </th>

                    <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Findings
                    </th>

                    <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Actions
                    </th>

                    <th className="px-6 py-4" />

                  </tr>

                </thead>


                <tbody className="divide-y">

                  {data.risks.map((risk) => (

                    <tr
                      key={risk.risk_id}
                      className="transition hover:bg-slate-50"
                    >

                      <td className="px-6 py-5">

                        <div>

                          <p className="font-semibold text-slate-900">
                            {risk.risk_title}
                          </p>

                          <p className="mt-1 text-xs text-slate-400">
                            Risk #{risk.risk_id}
                          </p>

                        </div>

                      </td>


                      <td className="px-6 py-5">

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${riskScoreClass(
                            risk.risk_score
                          )}`}
                        >
                          {risk.risk_score}
                        </span>

                      </td>


                      <td className="px-6 py-5">

                        <span className="text-sm font-medium text-slate-700">
                          {risk.metrics.control_count}
                        </span>

                      </td>


                      <td className="px-6 py-5">

                        <div>

                          <p className="text-sm font-medium text-slate-700">
                            {risk.metrics.controls_with_evidence}
                          </p>

                          <p className="text-xs text-slate-400">
                            {formatPercent(
                              risk.metrics.evidence_coverage_percent
                            )}
                          </p>

                        </div>

                      </td>


                      <td className="px-6 py-5">

                        <div>

                          <p className="text-sm font-medium text-slate-700">
                            {risk.metrics.finding_count}
                          </p>

                          <p className="text-xs text-slate-400">
                            {risk.metrics.open_findings} open
                          </p>

                        </div>

                      </td>


                      <td className="px-6 py-5">

                        <div>

                          <p className="text-sm font-medium text-slate-700">
                            {risk.metrics.action_count}
                          </p>

                          <p className="text-xs text-slate-400">
                            {risk.metrics.overdue_actions} overdue
                          </p>

                        </div>

                      </td>


                      <td className="px-6 py-5 text-right">

                        <button
                          type="button"
                          onClick={() =>
                            navigate(
                              `/risks/${risk.risk_id}`
                            )
                          }
                          className="inline-flex items-center rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-700 transition hover:bg-slate-50"
                        >
                          View Risk
                          <ArrowRight className="ml-2 h-4 w-4" />
                        </button>

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            )}

          </div>

        </div>

      </div>

    </AppLayout>
  );
}


// ==========================================================
// Metric Card
// ==========================================================

interface MetricCardProps {
  title: string;
  value: number | string;
  icon: React.ComponentType<{
    className?: string;
  }>;
  emphasis?: "critical";
}


function MetricCard({
  title,
  value,
  icon: Icon,
  emphasis,
}: MetricCardProps) {

  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">

      <div className="flex items-start justify-between">

        <div>

          <p className="text-sm font-medium text-slate-500">
            {title}
          </p>

          <p
            className={`mt-2 text-2xl font-bold ${
              emphasis === "critical"
                ? "text-red-600"
                : "text-slate-900"
            }`}
          >
            {value}
          </p>

        </div>

        <div className="rounded-lg bg-slate-100 p-2">
          <Icon className="h-5 w-5 text-slate-600" />
        </div>

      </div>

    </div>
  );
}