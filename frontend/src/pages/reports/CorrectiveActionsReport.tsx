import {
  ArrowLeft,
  AlertTriangle,
  CheckCircle2,
  Clock3,
  ListChecks,
  ShieldAlert,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useCorrectiveActionReport } from "@/hooks/useCorrectiveActionReport";

function priorityClass(priority: string) {
  switch (priority) {
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

function statusClass(status: string) {
  switch (status) {
    case "Completed":
    case "Closed":
      return "bg-green-100 text-green-700 border-green-200";

    case "In Progress":
      return "bg-yellow-100 text-yellow-700 border-yellow-200";

    case "Open":
      return "bg-blue-100 text-blue-700 border-blue-200";

    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
  }
}

function formatDate(date: string | null) {
  if (!date) {
    return "—";
  }

  return new Date(
    `${date}T00:00:00`
  ).toLocaleDateString("en-IE");
}

export default function CorrectiveActionsReport() {
  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
    refetch,
  } = useCorrectiveActionReport();

  if (isLoading) {
    return (
      <AppLayout>
        <div className="mx-auto max-w-7xl space-y-6">

          <div className="h-8 w-72 animate-pulse rounded bg-slate-200" />

          <div className="grid gap-4 md:grid-cols-4">

            {Array.from({ length: 4 }).map(
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

  if (error || !data) {
    return (
      <AppLayout>
        <div className="mx-auto max-w-4xl">

          <div className="rounded-xl border border-red-200 bg-red-50 p-6">

            <div className="flex items-start gap-3">

              <AlertTriangle className="mt-0.5 h-5 w-5 text-red-600" />

              <div>

                <h2 className="font-semibold text-red-700">
                  Corrective Actions Report Unavailable
                </h2>

                <p className="mt-1 text-sm text-red-600">
                  The corrective actions report could not
                  be loaded.
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
    actions,
  } = data;

  return (
    <AppLayout>

      <div className="mx-auto max-w-7xl space-y-6">

        {/* Header */}

        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">

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

              <div className="rounded-xl bg-orange-50 p-3">

                <ListChecks className="h-6 w-6 text-orange-600" />

              </div>

              <div>

                <h1 className="text-3xl font-bold text-slate-900">
                  Corrective Actions Report
                </h1>

                <p className="mt-1 text-slate-500">
                  Live overview of remediation actions,
                  priorities, ownership, and deadlines.
                </p>

              </div>

            </div>

          </div>

        </div>

        {/* Summary */}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                Total Actions
              </p>

              <ListChecks className="h-5 w-5 text-slate-400" />

            </div>

            <p className="mt-3 text-3xl font-bold text-slate-900">
              {summary.total_actions}
            </p>

          </div>

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                Open Actions
              </p>

              <Clock3 className="h-5 w-5 text-blue-500" />

            </div>

            <p className="mt-3 text-3xl font-bold text-blue-600">
              {summary.open_actions}
            </p>

          </div>

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                Critical Actions
              </p>

              <ShieldAlert className="h-5 w-5 text-red-500" />

            </div>

            <p className="mt-3 text-3xl font-bold text-red-600">
              {summary.critical_actions}
            </p>

          </div>

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <div className="flex items-center justify-between">

              <p className="text-sm font-medium text-slate-500">
                Overdue Actions
              </p>

              <AlertTriangle className="h-5 w-5 text-orange-500" />

            </div>

            <p
              className={`mt-3 text-3xl font-bold ${
                summary.overdue_actions > 0
                  ? "text-red-600"
                  : "text-green-600"
              }`}
            >
              {summary.overdue_actions}
            </p>

          </div>

        </div>

        {/* Secondary Summary */}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              In Progress
            </p>

            <p className="mt-2 text-2xl font-bold text-yellow-600">
              {summary.in_progress_actions}
            </p>

          </div>

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Completed
            </p>

            <p className="mt-2 text-2xl font-bold text-green-600">
              {summary.completed_actions}
            </p>

          </div>

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              Closed
            </p>

            <p className="mt-2 text-2xl font-bold text-slate-600">
              {summary.closed_actions}
            </p>

          </div>

          <div className="rounded-xl border bg-white p-5 shadow-sm">

            <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
              High Priority
            </p>

            <p className="mt-2 text-2xl font-bold text-orange-600">
              {summary.high_actions}
            </p>

          </div>

        </div>

        {/* Report Table */}

        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">

          <div className="border-b bg-slate-50 px-6 py-5">

            <div className="flex items-center gap-3">

              <div className="rounded-lg bg-indigo-50 p-2">

                <CheckCircle2 className="h-5 w-5 text-indigo-600" />

              </div>

              <div>

                <h2 className="font-semibold text-slate-900">
                  Corrective Actions
                </h2>

                <p className="text-sm text-slate-500">
                  Detailed remediation action register.
                </p>

              </div>

            </div>

          </div>

          {actions.length === 0 ? (

            <div className="p-12 text-center">

              <CheckCircle2 className="mx-auto h-10 w-10 text-green-500" />

              <h3 className="mt-4 font-semibold text-slate-900">
                No corrective actions
              </h3>

              <p className="mt-1 text-sm text-slate-500">
                There are currently no corrective actions
                in the system.
              </p>

            </div>

          ) : (

            <div className="overflow-x-auto">

              <table className="w-full min-w-[1100px] text-left">

                <thead className="border-b bg-white">

                  <tr>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Action
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Finding
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Assignee
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Priority
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Status
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Due Date
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Completion
                    </th>

                    <th className="px-6 py-4 text-xs font-semibold uppercase tracking-wide text-slate-500">
                      Overdue
                    </th>

                  </tr>

                </thead>

                <tbody className="divide-y">

                  {actions.map((action) => (

                    <tr
                      key={action.id}
                      className={`transition hover:bg-slate-50 ${
                        action.overdue
                          ? "bg-red-50/40"
                          : ""
                      }`}
                    >

                      {/* Action */}

                      <td className="px-6 py-5">

                        <div>

                          <p className="font-semibold text-slate-900">
                            {action.title}
                          </p>

                          <p className="mt-1 max-w-xs text-xs leading-5 text-slate-500">
                            {action.description}
                          </p>

                        </div>

                      </td>

                      {/* Finding */}

                      <td className="px-6 py-5">

                        <p className="max-w-xs text-sm font-medium text-slate-700">
                          {action.finding_title}
                        </p>

                        <p className="mt-1 text-xs text-slate-400">
                          Finding #{action.finding_id}
                        </p>

                      </td>

                      {/* Assignee */}

                      <td className="px-6 py-5">

                        <p className="text-sm font-medium text-slate-800">
                          {action.assignee_name}
                        </p>

                      </td>

                      {/* Priority */}

                      <td className="px-6 py-5">

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${priorityClass(
                            action.priority
                          )}`}
                        >
                          {action.priority}
                        </span>

                      </td>

                      {/* Status */}

                      <td className="px-6 py-5">

                        <span
                          className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${statusClass(
                            action.status
                          )}`}
                        >
                          {action.status}
                        </span>

                      </td>

                      {/* Due Date */}

                      <td className="px-6 py-5">

                        <p
                          className={`text-sm font-medium ${
                            action.overdue
                              ? "text-red-700"
                              : "text-slate-700"
                          }`}
                        >
                          {formatDate(
                            action.due_date
                          )}
                        </p>

                      </td>

                      {/* Completion */}

                      <td className="px-6 py-5">

                        <p className="text-sm text-slate-600">
                          {formatDate(
                            action.completed_at
                          )}
                        </p>

                      </td>

                      {/* Overdue */}

                      <td className="px-6 py-5">

                        {action.overdue ? (

                          <span className="inline-flex items-center gap-1.5 rounded-full border border-red-200 bg-red-100 px-3 py-1 text-xs font-semibold text-red-700">

                            <AlertTriangle className="h-3.5 w-3.5" />

                            Overdue

                          </span>

                        ) : (

                          <span className="inline-flex items-center gap-1.5 rounded-full border border-green-200 bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">

                            <CheckCircle2 className="h-3.5 w-3.5" />

                            On Track

                          </span>

                        )}

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