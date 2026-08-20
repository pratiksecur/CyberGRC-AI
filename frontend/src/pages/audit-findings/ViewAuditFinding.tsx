import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Calendar,
  FileText,
  Pencil,
  ShieldCheck,
} from "lucide-react";

import AppLayout from "@/layouts/AppLayout";

import { useAuditFinding } from "@/hooks/useAuditFinding";

function severityClass(
  severity: string
) {
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

function statusClass(
  status: string
) {
  switch (status) {
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

export default function ViewAuditFinding() {
  const { id } = useParams();

  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
  } = useAuditFinding(Number(id));

  if (isLoading) {
    return (
      <AppLayout>

        <div className="mx-auto max-w-4xl space-y-6">

          <div className="h-8 w-64 animate-pulse rounded bg-slate-200" />

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

            <h2 className="font-semibold text-red-700">
              Audit Finding Not Found
            </h2>

            <p className="mt-1 text-sm text-red-600">
              The requested audit finding could not be found.
            </p>

            <button
              onClick={() =>
                navigate("/audit-findings")
              }
              className="mt-4 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white hover:bg-red-700"
            >
              Back to Audit Findings
            </button>

          </div>

        </div>

      </AppLayout>
    );
  }

  return (
    <AppLayout>

      <div className="mx-auto max-w-4xl space-y-6">

        {/* Header */}
        <div className="flex items-start justify-between gap-4">

          <div>

            <button
              onClick={() =>
                navigate("/audit-findings")
              }
              className="mb-4 flex items-center gap-2 text-sm text-slate-500 transition hover:text-slate-800"
            >
              <ArrowLeft size={16} />
              Back to Audit Findings
            </button>

            <h1 className="text-3xl font-bold text-slate-900">
              {data.title}
            </h1>

            <p className="mt-1 text-slate-500">
              Audit Finding #{data.id}
            </p>

          </div>

          <button
            onClick={() =>
              navigate(
                `/audit-findings/${data.id}/edit`
              )
            }
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700"
          >
            <Pencil size={16} />
            Edit
          </button>

        </div>

        {/* Main Card */}
        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">

          {/* Summary */}
          <div className="border-b bg-slate-50 p-6">

            <div className="grid gap-5 md:grid-cols-2">

              <div className="flex gap-3">

                <div className="rounded-lg bg-indigo-100 p-2.5">
                  <FileText
                    size={20}
                    className="text-indigo-600"
                  />
                </div>

                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Audit
                  </p>

                  <p className="mt-1 font-semibold text-slate-800">
                    {data.audit_name}
                  </p>

                  <p className="text-xs text-slate-400">
                    Audit ID: {data.audit_id}
                  </p>
                </div>

              </div>

              <div className="flex gap-3">

                <div className="rounded-lg bg-blue-100 p-2.5">
                  <ShieldCheck
                    size={20}
                    className="text-blue-600"
                  />
                </div>

                <div>
                  <p className="text-xs font-medium uppercase tracking-wide text-slate-500">
                    Control
                  </p>

                  <p className="mt-1 font-semibold text-slate-800">
                    {data.control_name}
                  </p>

                  <p className="text-xs text-slate-400">
                    Control ID: {data.control_id}
                  </p>
                </div>

              </div>

            </div>

            <div className="mt-6 flex flex-wrap gap-3">

              <span
                className={`rounded-full border px-3 py-1.5 text-xs font-semibold ${severityClass(
                  data.severity
                )}`}
              >
                {data.severity} Severity
              </span>

              <span
                className={`rounded-full border px-3 py-1.5 text-xs font-semibold ${statusClass(
                  data.status
                )}`}
              >
                {data.status}
              </span>

            </div>

          </div>

          {/* Description */}
          <div className="p-6">

            <h2 className="text-lg font-semibold text-slate-900">
              Description
            </h2>

            <p className="mt-3 whitespace-pre-wrap leading-7 text-slate-600">
              {data.description}
            </p>

          </div>

          {/* Recommendation */}
          <div className="border-t p-6">

            <h2 className="text-lg font-semibold text-slate-900">
              Recommendation
            </h2>

            <div className="mt-3 rounded-lg border border-indigo-100 bg-indigo-50 p-4">

              <p className="whitespace-pre-wrap leading-7 text-slate-700">
                {data.recommendation}
              </p>

            </div>

          </div>

          {/* Metadata */}
          <div className="border-t bg-slate-50 p-6">

            <div className="flex items-center gap-2 text-sm text-slate-500">

              <Calendar size={16} />

              <span>
                Created{" "}
                {new Date(
                  data.created_at
                ).toLocaleString()}
              </span>

            </div>

            <div className="mt-2 text-sm text-slate-400">
              Last updated{" "}
              {new Date(
                data.updated_at
              ).toLocaleString()}
            </div>

          </div>

        </div>

      </div>

    </AppLayout>
  );
}