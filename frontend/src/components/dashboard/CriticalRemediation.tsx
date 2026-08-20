import {
  AlertTriangle,
  CalendarDays,
  CheckCircle2,
  User,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import type {
  CriticalRemediation as CriticalRemediationData,
} from "@/api/dashboard";

interface Props {
  data: CriticalRemediationData | null;
}

export default function CriticalRemediation({
  data,
}: Props) {
  const navigate = useNavigate();
  if (!data) {
    return (
      <div className="rounded-2xl border bg-white p-6">
        <div className="flex items-center gap-3">
          <div className="rounded-lg bg-emerald-50 p-2">
            <CheckCircle2 className="h-5 w-5 text-emerald-600" />
          </div>

          <div>
            <h2 className="font-semibold text-slate-900">
              Critical Remediation
            </h2>

            <p className="text-sm text-slate-500">
              No critical remediation items require attention.
            </p>
          </div>
        </div>
      </div>
    );
  }

  const formattedDueDate = data.dueDate
    ? new Date(
        `${data.dueDate}T00:00:00`
      ).toLocaleDateString("en-IE")
    : "Not specified";

  return (
    <div className="rounded-2xl border bg-white shadow-sm">

      {/* Header */}

      <div className="flex items-center gap-3 border-b p-6">

        <div className="rounded-lg bg-red-50 p-2">
          <AlertTriangle className="h-5 w-5 text-red-600" />
        </div>

        <div>
          <h2 className="font-semibold text-slate-900">
            Critical Remediation
          </h2>

          <p className="text-sm text-slate-500">
            Highest-priority finding requiring attention.
          </p>
        </div>

      </div>

      {/* Content */}

      <div className="space-y-6 p-6">

        {/* Finding */}

        <div>
          <p className="mb-1 text-xs font-medium uppercase tracking-wide text-slate-400">
            Critical Finding
          </p>

          <div className="flex items-start justify-between gap-4">

          <button
            type="button"
            onClick={() =>
              navigate(
                `/audit-findings/${data.findingId}`
              )
            }
            className="text-left font-semibold text-slate-900 transition hover:text-blue-600 hover:underline"
          >
            {data.findingTitle}
          </button>

            <span className="shrink-0 rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-700">
              {data.findingSeverity}
            </span>

          </div>
        </div>

        {/* Corrective Action */}

        <div className="rounded-xl bg-slate-50 p-4">

          <p className="mb-1 text-xs font-medium uppercase tracking-wide text-slate-400">
            Corrective Action
          </p>

          <button
            type="button"
            onClick={() =>
              navigate(
                `/corrective-actions/${data.actionId}`
              )
            }
            className="text-left font-medium text-slate-900 transition hover:text-blue-600 hover:underline"
          >
            {data.actionTitle}
          </button>

        </div>

        {/* Details */}

        <div className="grid gap-4 sm:grid-cols-3">

          {/* Assignee */}

          <div className="flex items-center gap-3">

            <div className="rounded-lg bg-blue-50 p-2">
              <User className="h-4 w-4 text-blue-600" />
            </div>

            <div>
              <p className="text-xs text-slate-400">
                Assigned To
              </p>

              <p className="text-sm font-medium text-slate-900">
                {data.assigneeName}
              </p>
            </div>

          </div>

          {/* Status */}

          <div>

            <p className="text-xs text-slate-400">
              Status
            </p>

            <span className="mt-1 inline-flex rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">
              {data.status}
            </span>

          </div>

          {/* Priority */}

          <div>

            <p className="text-xs text-slate-400">
              Priority
            </p>

            <span className="mt-1 inline-flex rounded-full bg-red-100 px-3 py-1 text-xs font-semibold text-red-700">
              {data.priority}
            </span>

          </div>

        </div>

        {/* Due Date */}

        <div className="flex items-center gap-3 border-t pt-4">

          <CalendarDays className="h-4 w-4 text-slate-500" />

          <div>

            <p className="text-xs text-slate-400">
              Due Date
            </p>

            <p className="text-sm font-medium text-slate-900">
              {formattedDueDate}
            </p>

          </div>

        </div>

      </div>

    </div>
  );
}