import {
  ArrowLeft,
  AlertTriangle,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  FileWarning,
  ShieldAlert,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useAuditReport } from "@/hooks/useAuditReport";


// ==========================================================
// Audit Status Styling
// ==========================================================

function statusClass(status: string) {
  switch (status) {
    case "Completed":
      return "bg-green-100 text-green-700 border-green-200";

    case "In Progress":
      return "bg-yellow-100 text-yellow-700 border-yellow-200";

    case "Planned":
      return "bg-blue-100 text-blue-700 border-blue-200";

    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
  }
}


// ==========================================================
// Finding Severity
// ==========================================================

function severityClass(severity: string) {
  switch (severity) {
    case "Critical":
      return "bg-red-100 text-red-700 border-red-200";

    case "High":
      return "bg-orange-100 text-orange-700 border-orange-200";

    case "Medium":
      return "bg-yellow-100 text-yellow-700 border-yellow-200";

    case "Low":
      return "bg-green-100 text-green-700 border-green-200";

    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
  }
}


// ==========================================================
// Date Formatting
// ==========================================================

function formatDate(date: string | null) {
  if (!date) {
    return "—";
  }

  return new Date(
    `${date}T00:00:00`
  ).toLocaleDateString("en-IE");
}


// ==========================================================
// Audit Report
// ==========================================================

export default function AuditReport() {

  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useAuditReport();


  // ========================================================
  // Loading
  // ========================================================

  if (isLoading) {
    return (
      <AppLayout>

        <div className="mx-auto max-w-7xl space-y-6">

          <div className="h-8 w-72 animate-pulse rounded bg-slate-200" />

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

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

            {Array.from({ length: 4 }).map(
              (_, index) => (
                <div
                  key={index}
                  className="h-24 animate-pulse rounded-xl bg-slate-100"
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

          <div className="rounded-xl border border-red-200 bg-red-50 p-6">

            <div className="flex items-start gap-3">

              <AlertTriangle className="mt-0.5 h-5 w-5 text-red-600" />

              <div>

                <h2 className="font-semibold text-red-700">
                  Audit Report Unavailable
                </h2>

                <p className="mt-1 text-sm text-red-600">
                  The audit report could not be loaded.
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
    audits,
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

            <div className="rounded-xl bg-blue-50 p-3">

              <ClipboardCheck className="h-6 w-6 text-blue-600" />

            </div>

            <div>

              <h1 className="text-3xl font-bold text-slate-900">
                Audit Report
              </h1>

              <p className="mt-1 text-slate-500">
                Live overview of audits, findings, severity,
                status, and audit performance.
              </p>

            </div>

          </div>

        </div>


        {/* ==================================================
            Primary Summary
        ================================================== */}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">


          {/* Total Audits */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                Total Audits
              </p>

              <ClipboardCheck className="h-5 w-5 text-slate-400" />

            </div>

            <p className="mt-3 text-3xl font-bold text-slate-900">
              {summary.total_audits}
            </p>

          </div>


          {/* Planned */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                Planned Audits
              </p>

              <Clock3 className="h-5 w-5 text-blue-500" />

            </div>

            <p className="mt-3 text-3xl font-bold text-blue-600">
              {summary.planned_audits}
            </p>

          </div>


          {/* In Progress */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                In Progress
              </p>

              <ClipboardCheck className="h-5 w-5 text-yellow-500" />

            </div>

            <p className="mt-3 text-3xl font-bold text-yellow-600">
              {summary.in_progress_audits}
            </p>

          </div>


          {/* Completed */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                Completed Audits
              </p>

              <CheckCircle2 className="h-5 w-5 text-green-500" />

            </div>

            <p className="mt-3 text-3xl font-bold text-green-600">
              {summary.completed_audits}
            </p>

          </div>

        </div>


        {/* ==================================================
            Findings Summary
        ================================================== */}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">


          {/* Total Findings */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Total Findings
            </p>

            <p className="mt-2 text-2xl font-bold text-slate-900">
              {summary.total_findings}
            </p>

          </div>


          {/* Critical */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Critical Findings
            </p>

            <p className="mt-2 text-2xl font-bold text-red-600">
              {summary.critical_findings}
            </p>

          </div>


          {/* Open */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Open Findings
            </p>

            <p className="mt-2 text-2xl font-bold text-blue-600">
              {summary.open_findings}
            </p>

          </div>


          {/* Closed */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Closed Findings
            </p>

            <p className="mt-2 text-2xl font-bold text-green-600">
              {summary.closed_findings}
            </p>

          </div>

        </div>


        {/* ==================================================
            Severity Breakdown
        ================================================== */}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Critical
            </p>

            <p className="mt-2 text-2xl font-bold text-red-600">
              {summary.critical_findings}
            </p>

          </div>


          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              High
            </p>

            <p className="mt-2 text-2xl font-bold text-orange-600">
              {summary.high_findings}
            </p>

          </div>


          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Medium
            </p>

            <p className="mt-2 text-2xl font-bold text-yellow-600">
              {summary.medium_findings}
            </p>

          </div>


          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Low
            </p>

            <p className="mt-2 text-2xl font-bold text-green-600">
              {summary.low_findings}
            </p>

          </div>

        </div>


        {/* ==================================================
            Audit Register
        ================================================== */}

        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">

          <div className="border-b bg-slate-50 px-6 py-5">

            <div className="flex items-center gap-3">

              <div className="rounded-lg bg-blue-50 p-2">

                <FileWarning className="h-5 w-5 text-blue-600" />

              </div>

              <div>

                <h2 className="font-semibold text-slate-900">
                  Audit Register
                </h2>

                <p className="text-sm text-slate-500">
                  Detailed audit register and finding overview.
                </p>

              </div>

            </div>

          </div>


          {audits.length === 0 ? (

            <div className="p-12 text-center">

              <CheckCircle2 className="mx-auto h-10 w-10 text-green-500" />

              <h3 className="mt-4 font-semibold text-slate-900">
                No audits
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                There are currently no audits
                in the system.
              </p>

            </div>

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full min-w-[1250px] text-left">

                <thead className="border-b bg-white">

                  <tr>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Audit
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Framework
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Auditor
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Status
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Dates
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Findings
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Critical
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Open
                    </th>

                  </tr>

                </thead>


                <tbody className="divide-y">

                  {audits.map((audit) => (

                    <tr
                      key={audit.id}
                      className="transition hover:bg-slate-50"
                    >

                      {/* Audit */}

                      <td className="px-6 py-5">

                        <div>

                          <p className="font-semibold text-slate-900">
                            {audit.name}
                          </p>

                          <p className="mt-1 max-w-sm text-xs leading-5 text-slate-500">
                            {audit.scope}
                          </p>

                          <p className="mt-1 text-xs text-slate-400">
                            Audit #{audit.id}
                          </p>

                        </div>

                      </td>


                      {/* Framework */}

                      <td className="px-6 py-5">

                        <p className="text-sm font-medium text-slate-800">
                          {audit.framework_name}
                        </p>

                        <p className="mt-1 text-xs text-slate-400">
                          Framework #{audit.framework_id}
                        </p>

                      </td>


                      {/* Auditor */}

                      <td className="px-6 py-5">

                        <p className="text-sm font-medium text-slate-800">
                          {audit.auditor_name}
                        </p>

                      </td>


                      {/* Status */}

                      <td className="px-6 py-5">

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${statusClass(
                            audit.status
                          )}`}
                        >
                          {audit.status}
                        </span>

                      </td>


                      {/* Dates */}

                      <td className="px-6 py-5">

                        <div className="text-sm">

                          <p className="text-slate-700">
                            {formatDate(
                              audit.start_date
                            )}
                          </p>

                          <p className="mt-1 text-xs text-slate-400">
                            to {formatDate(
                              audit.end_date
                            )}
                          </p>

                        </div>

                      </td>


                      {/* Findings */}

                      <td className="px-6 py-5">

                        <span className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-700">
                          {audit.finding_count}
                        </span>

                      </td>


                      {/* Critical */}

                      <td className="px-6 py-5">

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${
                            audit.critical_finding_count > 0
                              ? severityClass("Critical")
                              : "bg-slate-50 text-slate-600 border-slate-200"
                          }`}
                        >
                          {audit.critical_finding_count}
                        </span>

                      </td>


                      {/* Open */}

                      <td className="px-6 py-5">

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${
                            audit.open_finding_count > 0
                              ? "bg-blue-100 text-blue-700 border-blue-200"
                              : "bg-green-100 text-green-700 border-green-200"
                          }`}
                        >
                          {audit.open_finding_count}
                        </span>

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