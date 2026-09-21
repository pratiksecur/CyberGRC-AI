import {
  ArrowLeft,
  AlertTriangle,
  CheckCircle2,
  FileCheck2,
  FileText,
  ShieldCheck,
  ClipboardCheck,
  BarChart3,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useComplianceReport } from "@/hooks/useComplianceReport";


// ==========================================================
// Effectiveness Styling
// ==========================================================

function effectivenessClass(value: number) {
  if (value >= 80) {
    return "bg-green-100 text-green-700 border-green-200";
  }

  if (value >= 60) {
    return "bg-yellow-100 text-yellow-700 border-yellow-200";
  }

  if (value >= 40) {
    return "bg-orange-100 text-orange-700 border-orange-200";
  }

  return "bg-red-100 text-red-700 border-red-200";
}


// ==========================================================
// Compliance Report
// ==========================================================

export default function ComplianceReport() {

  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useComplianceReport();


  // ========================================================
  // Loading
  // ========================================================

  if (isLoading) {
    return (
      <AppLayout>

        <div className="mx-auto max-w-7xl space-y-6">

          <div className="h-8 w-80 animate-pulse rounded bg-slate-200" />

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
                  Compliance Report Unavailable
                </h2>

                <p className="mt-1 text-sm text-red-600">
                  The compliance report could not be loaded.
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
    frameworks,
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

            <div className="rounded-xl bg-green-50 p-3">

              <FileCheck2 className="h-6 w-6 text-green-600" />

            </div>

            <div>

              <h1 className="text-3xl font-bold text-slate-900">
                Compliance Report
              </h1>

              <p className="mt-1 text-slate-500">
                Live overview of framework coverage, controls,
                effectiveness, evidence, and findings.
              </p>

            </div>

          </div>

        </div>


        {/* ==================================================
            Primary Summary
        ================================================== */}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">


          {/* Frameworks */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                Total Frameworks
              </p>

              <FileCheck2 className="h-5 w-5 text-slate-400" />

            </div>

            <p className="mt-3 text-3xl font-bold text-slate-900">
              {summary.total_frameworks}
            </p>

          </div>


          {/* Controls */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                Total Controls
              </p>

              <ShieldCheck className="h-5 w-5 text-blue-500" />

            </div>

            <p className="mt-3 text-3xl font-bold text-blue-600">
              {summary.total_controls}
            </p>

          </div>


          {/* Active Controls */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                Active Controls
              </p>

              <ClipboardCheck className="h-5 w-5 text-green-500" />

            </div>

            <p className="mt-3 text-3xl font-bold text-green-600">
              {summary.active_controls}
            </p>

          </div>


          {/* Effectiveness */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                Control Effectiveness
              </p>

              <BarChart3 className="h-5 w-5 text-indigo-500" />

            </div>

            <p className="mt-3 text-3xl font-bold text-indigo-600">
              {summary.average_control_effectiveness}%
            </p>

          </div>

        </div>


        {/* ==================================================
            Secondary Summary
        ================================================== */}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">


          {/* Evidence */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                Evidence
              </p>

              <FileText className="h-4 w-4 text-slate-400" />

            </div>

            <p className="mt-2 text-2xl font-bold text-slate-900">
              {summary.total_evidence}
            </p>

          </div>


          {/* Findings */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Total Findings
            </p>

            <p className="mt-2 text-2xl font-bold text-slate-900">
              {summary.total_findings}
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


          {/* Critical */}

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Critical Findings
            </p>

            <p className="mt-2 text-2xl font-bold text-red-600">
              {summary.critical_findings}
            </p>

          </div>

        </div>


        {/* ==================================================
            Framework Register
        ================================================== */}

        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">

          <div className="border-b bg-slate-50 px-6 py-5">

            <div className="flex items-center gap-3">

              <div className="rounded-lg bg-green-50 p-2">

                <ShieldCheck className="h-5 w-5 text-green-600" />

              </div>

              <div>

                <h2 className="font-semibold text-slate-900">
                  Framework Compliance
                </h2>

                <p className="text-sm text-slate-500">
                  Framework coverage, control effectiveness,
                  evidence, and findings.
                </p>

              </div>

            </div>

          </div>


          {frameworks.length === 0 ? (

            <div className="p-12 text-center">

              <CheckCircle2 className="mx-auto h-10 w-10 text-green-500" />

              <h3 className="mt-4 font-semibold text-slate-900">
                No frameworks
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                There are currently no compliance
                frameworks in the system.
              </p>

            </div>

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full min-w-[1200px] text-left">

                <thead className="border-b bg-white">

                  <tr>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Framework
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Controls
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Active
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Effectiveness
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Evidence
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

                  {frameworks.map((framework) => (

                    <tr
                      key={framework.id}
                      role="button"
                      tabIndex={0}
                      onClick={() =>
                        navigate(`/frameworks/${framework.id}`)
                      }
                      onKeyDown={(event) => {
                        if (
                          event.key === "Enter" ||
                          event.key === " "
                        ) {
                          event.preventDefault();

                          navigate(
                            `/frameworks/${framework.id}`
                          );
                        }
                      }}
                      className="cursor-pointer transition hover:bg-slate-50"
                    >

                      {/* Framework */}

                      <td className="px-6 py-5">

                        <div>

                          <p className="font-semibold text-indigo-600">
                            {framework.name}
                          </p>

                          <p className="mt-1 text-xs text-slate-500">
                            Version {framework.version}
                          </p>

                          <p className="mt-1 text-xs text-slate-400">
                            Framework #{framework.id}
                          </p>

                        </div>

                      </td>


                      {/* Controls */}

                      <td className="px-6 py-5">

                        <span className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-700">
                          {framework.control_count}
                        </span>

                      </td>


                      {/* Active */}

                      <td className="px-6 py-5">

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${
                            framework.active_control_count > 0
                              ? "bg-green-100 text-green-700 border-green-200"
                              : "bg-slate-50 text-slate-600 border-slate-200"
                          }`}
                        >
                          {framework.active_control_count}
                        </span>

                      </td>


                      {/* Effectiveness */}

                      <td className="px-6 py-5">

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${effectivenessClass(
                            framework.average_effectiveness
                          )}`}
                        >
                          {framework.average_effectiveness}%
                        </span>

                      </td>


                      {/* Evidence */}

                      <td className="px-6 py-5">

                        <span className="inline-flex items-center gap-1.5 text-sm font-medium text-slate-700">

                          <FileText className="h-4 w-4 text-slate-400" />

                          {framework.evidence_count}

                        </span>

                      </td>


                      {/* Findings */}

                      <td className="px-6 py-5">

                        <span className="inline-flex rounded-full border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-semibold text-slate-700">
                          {framework.finding_count}
                        </span>

                      </td>


                      {/* Critical */}

                      <td className="px-6 py-5">

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${
                            framework.critical_finding_count > 0
                              ? "bg-red-100 text-red-700 border-red-200"
                              : "bg-slate-50 text-slate-600 border-slate-200"
                          }`}
                        >
                          {framework.critical_finding_count}
                        </span>

                      </td>


                      {/* Open */}

                      <td className="px-6 py-5">

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${
                            framework.open_finding_count > 0
                              ? "bg-blue-100 text-blue-700 border-blue-200"
                              : "bg-green-100 text-green-700 border-green-200"
                          }`}
                        >
                          {framework.open_finding_count}
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