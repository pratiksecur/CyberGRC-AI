import {
  ArrowLeft,
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
  ShieldCheck,
  Activity,
  BarChart3,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useRiskReport } from "@/hooks/useRiskReport";


// ==========================================================
// Risk Score Styling
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


// ==========================================================
// Status Styling
// ==========================================================

function statusClass(status: string) {
  switch (status) {
    case "Closed":
      return "bg-green-100 text-green-700 border-green-200";

    case "Open":
      return "bg-blue-100 text-blue-700 border-blue-200";

    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
  }
}


// ==========================================================
// Severity Styling
// ==========================================================

function severityClass(score: number) {
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


// ==========================================================
// Date Formatting
// ==========================================================

function formatDate(date: string) {
  if (!date) {
    return "—";
  }

  return new Date(date).toLocaleDateString("en-IE");
}


// ==========================================================
// Risk Report
// ==========================================================

export default function RiskReport() {

  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useRiskReport();


  // ========================================================
  // Loading
  // ========================================================

  if (isLoading) {
    return (
      <AppLayout>

        <div className="mx-auto max-w-7xl space-y-6">

          <div className="h-8 w-64 animate-pulse rounded bg-slate-200" />

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

            {Array.from({ length: 4 }).map(
              (_, index) => (
                <div
                  key={index}
                  className="h-28 animate-pulse rounded-xl bg-slate-100"
                />
              )
            )}

          </div>

          <div className="h-28 animate-pulse rounded-xl bg-slate-100" />

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

          <div className="rounded-xl border border-red-200 bg-red-50 p-6">

            <div className="flex items-start gap-3">

              <AlertTriangle className="mt-0.5 h-5 w-5 text-red-600" />

              <div>

                <h2 className="font-semibold text-red-700">
                  Risk Report Unavailable
                </h2>

                <p className="mt-1 text-sm text-red-600">
                  The risk report could not be loaded.
                  Please try again.
                </p>

                <div className="mt-4 flex gap-3">

                  <button
                    type="button"
                    onClick={() => refetch()}
                    className="rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
                  >
                    Try Again
                  </button>

                  <button
                    type="button"
                    onClick={() =>
                      navigate("/reports")
                    }
                    className="rounded-lg border border-red-200 bg-white px-4 py-2 text-sm font-medium text-red-700 transition hover:bg-red-50"
                  >
                    Back to Reports
                  </button>

                </div>

              </div>

            </div>

          </div>

        </div>

      </AppLayout>
    );
  }


  const {
    summary,
    risks,
  } = data;


  // ========================================================
  // Page
  // ========================================================

  return (
    <AppLayout>

      <div className="mx-auto max-w-7xl space-y-6">

        {/* ==================================================
            Header
        ================================================== */}

        <div>

          <button
            type="button"
            onClick={() =>
              navigate("/reports")
            }
            className="mb-4 flex items-center gap-2 text-sm text-slate-500 transition hover:text-slate-900"
          >

            <ArrowLeft size={16} />

            Back to Reports

          </button>


          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-red-50 p-3">

              <ShieldAlert className="h-6 w-6 text-red-600" />

            </div>

            <div>

              <h1 className="text-3xl font-bold text-slate-900">
                Risk Report
              </h1>

              <p className="mt-1 text-slate-500">
                Live overview of organizational risks,
                severity, risk scores, and ownership.
              </p>

            </div>

          </div>

        </div>


        {/* ==================================================
            Primary Summary
        ================================================== */}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">


          {/* Total */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                Total Risks
              </p>

              <ShieldAlert className="h-5 w-5 text-slate-400" />

            </div>

            <p className="mt-3 text-3xl font-bold text-slate-900">
              {summary.total_risks}
            </p>

          </div>


          {/* Critical */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                Critical Risks
              </p>

              <AlertTriangle className="h-5 w-5 text-red-500" />

            </div>

            <p className="mt-3 text-3xl font-bold text-red-600">
              {summary.critical_risks}
            </p>

          </div>


          {/* High */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                High Risks
              </p>

              <Activity className="h-5 w-5 text-orange-500" />

            </div>

            <p className="mt-3 text-3xl font-bold text-orange-600">
              {summary.high_risks}
            </p>

          </div>


          {/* Average Score */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                Average Risk Score
              </p>

              <BarChart3 className="h-5 w-5 text-indigo-500" />

            </div>

            <p className="mt-3 text-3xl font-bold text-indigo-600">
              {summary.average_risk_score}
            </p>

          </div>

        </div>


        {/* ==================================================
            Secondary Summary
        ================================================== */}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">


          {/* Medium */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Medium Risks
            </p>

            <p className="mt-2 text-2xl font-bold text-yellow-600">
              {summary.medium_risks}
            </p>

          </div>


          {/* Low */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Low Risks
            </p>

            <p className="mt-2 text-2xl font-bold text-green-600">
              {summary.low_risks}
            </p>

          </div>


          {/* Open */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Open Risks
            </p>

            <p className="mt-2 text-2xl font-bold text-blue-600">
              {summary.open_risks}
            </p>

          </div>


          {/* Closed */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Closed Risks
            </p>

            <p className="mt-2 text-2xl font-bold text-slate-600">
              {summary.closed_risks}
            </p>

          </div>

        </div>


        {/* ==================================================
            Risk Register
        ================================================== */}

        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">

          <div className="border-b bg-slate-50 px-6 py-5">

            <div className="flex items-center gap-3">

              <div className="rounded-lg bg-red-50 p-2">

                <ShieldCheck className="h-5 w-5 text-red-600" />

              </div>

              <div>

                <h2 className="font-semibold text-slate-900">
                  Risk Register
                </h2>

                <p className="text-sm text-slate-500">
                  Detailed organizational risk register.
                </p>

              </div>

            </div>

          </div>


          {risks.length === 0 ? (

            <div className="p-12 text-center">

              <CheckCircle2 className="mx-auto h-10 w-10 text-green-500" />

              <h3 className="mt-4 font-semibold text-slate-900">
                No risks
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                There are currently no risks
                in the system.
              </p>

            </div>

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full min-w-[1200px] text-left">

                <thead className="border-b bg-white">

                  <tr>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Risk
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Owner
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Likelihood
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Impact
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Risk Score
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Status
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Created
                    </th>

                  </tr>

                </thead>


                <tbody className="divide-y">

                  {risks.map((risk) => (

                    <tr
                      key={risk.id}
                      className="transition hover:bg-slate-50"
                    >

                      {/* Risk */}

                      <td className="px-6 py-5">

                        <div>

                          <p className="font-semibold text-slate-900">
                            {risk.title}
                          </p>

                          <p className="mt-1 max-w-sm text-xs leading-5 text-slate-500">
                            {risk.description}
                          </p>

                          <p className="mt-1 text-xs text-slate-400">
                            Risk #{risk.id}
                          </p>

                        </div>

                      </td>


                      {/* Owner */}

                      <td className="px-6 py-5">

                        <p className="text-sm font-medium text-slate-800">
                          {risk.owner_name}
                        </p>

                      </td>


                      {/* Likelihood */}

                      <td className="px-6 py-5">

                        <span className="inline-flex min-w-8 justify-center rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-sm font-semibold text-slate-700">
                          {risk.likelihood}
                        </span>

                      </td>


                      {/* Impact */}

                      <td className="px-6 py-5">

                        <span className="inline-flex min-w-8 justify-center rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-sm font-semibold text-slate-700">
                          {risk.impact}
                        </span>

                      </td>


                      {/* Risk Score */}

                      <td className="px-6 py-5">

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${riskScoreClass(
                            risk.risk_score
                          )}`}
                        >
                          {risk.risk_score}
                        </span>

                      </td>


                      {/* Status */}

                      <td className="px-6 py-5">

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${statusClass(
                            risk.status
                          )}`}
                        >
                          {risk.status}
                        </span>

                      </td>


                      {/* Created */}

                      <td className="px-6 py-5">

                        <p className="text-sm text-slate-600">
                          {formatDate(
                            risk.created_at
                          )}
                        </p>

                      </td>

                    </tr>

                  ))}

                </tbody>

              </table>

            </div>

          )}

        </div>

      </div>

    </AppLayout>
  );
}