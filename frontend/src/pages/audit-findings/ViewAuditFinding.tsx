import { useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  Calendar,
  ClipboardCheck,
  Eye,
  FileText,
  Pencil,
  ShieldCheck,
} from "lucide-react";

import AppLayout from "@/layouts/AppLayout";

import { useAuditFinding } from "@/hooks/useAuditFinding";
import { useCorrectiveActions } from "@/hooks/useCorrectiveActions";
import { useEvidence } from "@/hooks/useEvidence";

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

function statusClass(status: string) {
  switch (status) {
    case "Closed":
    case "Completed":
      return "bg-green-100 text-green-700 border-green-200";

    case "In Progress":
      return "bg-yellow-100 text-yellow-700 border-yellow-200";

    case "Open":
    case "Pending":
      return "bg-blue-100 text-blue-700 border-blue-200";

    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
  }
}

function priorityClass(priority: string) {
  switch (priority) {
    case "Critical":
      return "bg-red-100 text-red-700";

    case "High":
      return "bg-orange-100 text-orange-700";

    case "Medium":
      return "bg-yellow-100 text-yellow-700";

    case "Low":
      return "bg-green-100 text-green-700";

    default:
      return "bg-slate-100 text-slate-700";
  }
}

export default function ViewAuditFinding() {
  const { id } = useParams();
  const navigate = useNavigate();

  const findingId = Number(id);

  const {
    data,
    isLoading,
    error,
  } = useAuditFinding(findingId);

  const {
    data: correctiveActions,
    isLoading: actionsLoading,
    error: actionsError,
  } = useCorrectiveActions();

  const {
    data: evidence,
    isLoading: evidenceLoading,
    error: evidenceError,
  } = useEvidence();

  const relatedActions = useMemo(() => {
    if (!correctiveActions) {
      return [];
    }

    return correctiveActions.filter(
      (action) => action.finding_id === findingId
    );
  }, [correctiveActions, findingId]);

  const controlEvidence = useMemo(() => {
    if (!data || !evidence) {
      return [];
    }

    return evidence.filter(
      (item) => item.control_id === data.control_id
    );
  }, [data, evidence]);

  if (isLoading) {
    return (
      <AppLayout>
        <div className="mx-auto max-w-5xl space-y-6">
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
              The requested audit finding could not be found within your access scope.
            </p>

            <button
              type="button"
              onClick={() =>
                navigate("/audit-findings")
              }
              className="mt-4 flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
            >
              <ArrowLeft size={16} />
              Back to Audit Findings
            </button>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="mx-auto max-w-5xl space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <button
              type="button"
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
            type="button"
            onClick={() =>
              navigate(
                `/audit-findings/${data.id}/edit`
              )
            }
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700"
          >
            <Pencil size={16} />
            Edit Finding
          </button>
        </div>

        {/* Main Card */}
        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
          {/* Summary */}
          <div className="border-b bg-slate-50 p-6">
            <div className="grid gap-5 md:grid-cols-2">
              <button
                type="button"
                onClick={() =>
                  navigate(`/audits/${data.audit_id}`)
                }
                className="flex gap-3 rounded-xl p-2 text-left transition hover:bg-white"
              >
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
              </button>

              <button
                type="button"
                onClick={() =>
                  navigate(`/controls/${data.control_id}`)
                }
                className="flex gap-3 rounded-xl p-2 text-left transition hover:bg-white"
              >
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
              </button>
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

          {/* Control Evidence */}
          <div className="border-t p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Control Evidence
                </h2>

                <p className="text-sm text-slate-500">
                  Evidence currently associated with{" "}
                  {data.control_name}
                </p>
              </div>

              {!evidenceLoading && !evidenceError && (
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                  {controlEvidence.length}{" "}
                  {controlEvidence.length === 1
                    ? "File"
                    : "Files"}
                </span>
              )}
            </div>

            <div className="mt-4">
              {evidenceLoading ? (
                <div className="rounded-lg border border-dashed p-8 text-center text-sm text-slate-500">
                  Loading control evidence...
                </div>
              ) : evidenceError ? (
                <div className="rounded-lg border border-amber-200 bg-amber-50 p-5 text-sm text-amber-700">
                  Control evidence could not be loaded.
                </div>
              ) : controlEvidence.length === 0 ? (
                <div className="rounded-lg border border-dashed p-8 text-center">
                  <FileText className="mx-auto h-8 w-8 text-slate-300" />

                  <p className="mt-3 font-medium text-slate-700">
                    No evidence is currently associated with this control
                  </p>

                  <p className="mt-1 text-sm text-slate-500">
                    Upload evidence against the control to support this finding.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {controlEvidence.map((item) => (
                    <div
                      key={item.id}
                      className="flex flex-col gap-4 rounded-xl border p-4 transition hover:bg-slate-50 md:flex-row md:items-center md:justify-between"
                    >
                      <div className="flex min-w-0 items-start gap-3">
                        <div className="rounded-lg bg-blue-100 p-2">
                          <FileText className="h-5 w-5 text-blue-600" />
                        </div>

                        <div className="min-w-0">
                          <p className="truncate font-medium text-slate-900">
                            {item.title}
                          </p>

                          <p className="truncate text-sm text-slate-500">
                            {item.file_name}
                          </p>

                          <p className="mt-1 text-xs text-slate-400">
                            Uploaded{" "}
                            {new Date(
                              item.uploaded_at
                            ).toLocaleDateString()}
                          </p>
                        </div>
                      </div>

                      <button
                        type="button"
                        onClick={() =>
                          navigate(`/evidence/${item.id}`)
                        }
                        className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-white hover:text-blue-600"
                      >
                        <Eye size={16} />
                        View Evidence
                      </button>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </div>

          {/* Corrective Actions */}
          <div className="border-t p-6">
            <div className="flex items-center justify-between gap-4">
              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Corrective Actions
                </h2>

                <p className="text-sm text-slate-500">
                  Remediation actions created from this audit finding
                </p>
              </div>

              {!actionsLoading && !actionsError && (
                <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                  {relatedActions.length}{" "}
                  {relatedActions.length === 1
                    ? "Action"
                    : "Actions"}
                </span>
              )}
            </div>

            <div className="mt-4">
              {actionsLoading ? (
                <div className="rounded-lg border border-dashed p-8 text-center text-sm text-slate-500">
                  Loading corrective actions...
                </div>
              ) : actionsError ? (
                <div className="rounded-lg border border-amber-200 bg-amber-50 p-5 text-sm text-amber-700">
                  Corrective actions could not be loaded.
                </div>
              ) : relatedActions.length === 0 ? (
                <div className="rounded-lg border border-dashed p-8 text-center">
                  <ClipboardCheck className="mx-auto h-8 w-8 text-slate-300" />

                  <p className="mt-3 font-medium text-slate-700">
                    No corrective actions created for this finding
                  </p>

                  <p className="mt-1 text-sm text-slate-500">
                    Remediation actions will appear here once created.
                  </p>
                </div>
              ) : (
                <div className="space-y-3">
                  {relatedActions.map((action) => (
                    <div
                      key={action.id}
                      className="flex flex-col gap-4 rounded-xl border p-4 transition hover:bg-slate-50 md:flex-row md:items-center md:justify-between"
                    >
                      <div className="min-w-0">
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-xs font-medium text-slate-400">
                            Action #{action.id}
                          </span>

                          <span
                            className={`rounded-full px-2.5 py-1 text-xs font-semibold ${priorityClass(
                              action.priority
                            )}`}
                          >
                            {action.priority}
                          </span>

                          <span
                            className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${statusClass(
                              action.status
                            )}`}
                          >
                            {action.status}
                          </span>
                        </div>

                        <h3 className="mt-2 truncate font-semibold text-slate-900">
                          {action.title}
                        </h3>

                        <p className="mt-1 text-sm text-slate-500">
                          Assigned to{" "}
                          {action.assignee_name}
                          {action.due_date
                            ? ` · Due ${new Date(
                                action.due_date
                              ).toLocaleDateString()}`
                            : ""}
                        </p>
                      </div>

                      <button
                        type="button"
                        onClick={() =>
                          navigate(
                            `/corrective-actions/${action.id}`
                          )
                        }
                        className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-white hover:text-indigo-600"
                      >
                        <Eye size={16} />
                        View Action
                      </button>
                    </div>
                  ))}
                </div>
              )}
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