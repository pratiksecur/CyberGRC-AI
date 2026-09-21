import { useMemo } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  CalendarDays,
  ClipboardList,
  Eye,
  Pencil,
} from "lucide-react";

import AppLayout from "@/layouts/AppLayout";

import { useAudit } from "@/hooks/useAudit";
import { useAuditFindings } from "@/hooks/useAuditFindings";

import AuditAIInsights from "@/components/ai/AuditAIInsights";

function severityClass(severity: string) {
  switch (severity) {
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

function statusClass(status: string) {
  switch (status) {
    case "Closed":
      return "bg-green-100 text-green-700";

    case "In Progress":
      return "bg-yellow-100 text-yellow-700";

    case "Open":
      return "bg-blue-100 text-blue-700";

    default:
      return "bg-slate-100 text-slate-700";
  }
}

export default function ViewAudit() {
  const { id } = useParams();
  const navigate = useNavigate();

  const auditId = Number(id);

  const {
    data: audit,
    isLoading,
    error,
  } = useAudit(auditId);

  const {
    data: findings,
    isLoading: findingsLoading,
    error: findingsError,
  } = useAuditFindings();

  const auditFindings = useMemo(() => {
    if (!findings) {
      return [];
    }

    return findings.filter(
      (finding) => finding.audit_id === auditId
    );
  }, [findings, auditId]);

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading audit...
        </div>
      </AppLayout>
    );
  }

  if (error || !audit) {
    return (
      <AppLayout>
        <div className="mx-auto max-w-4xl p-10">
          <div className="rounded-xl border border-red-200 bg-red-50 p-6">
            <h2 className="font-semibold text-red-700">
              Audit not found
            </h2>

            <p className="mt-1 text-sm text-red-600">
              The requested audit could not be found within your access scope.
            </p>

            <button
              type="button"
              onClick={() => navigate("/audits")}
              className="mt-4 flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
            >
              <ArrowLeft size={16} />
              Back to Audits
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
              onClick={() => navigate("/audits")}
              className="mb-4 flex items-center gap-2 text-sm text-slate-500 transition hover:text-slate-900"
            >
              <ArrowLeft size={16} />
              Back to Audits
            </button>

            <h1 className="text-3xl font-bold text-slate-900">
              {audit.name}
            </h1>

            <p className="mt-1 text-slate-500">
              Audit #{audit.id}
            </p>
          </div>

          <button
            type="button"
            onClick={() =>
              navigate(`/audits/${audit.id}/edit`)
            }
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700"
          >
            <Pencil size={16} />
            Edit Audit
          </button>
        </div>

        {/* Audit Details */}
        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
          <div className="border-b bg-slate-50 p-6">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-indigo-100 p-2.5">
                <ClipboardList
                  size={20}
                  className="text-indigo-600"
                />
              </div>

              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Audit Details
                </h2>

                <p className="text-sm text-slate-500">
                  Scope, ownership, schedule, and lifecycle status
                </p>
              </div>
            </div>
          </div>

          <div className="p-6">
            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <p className="text-sm text-slate-500">
                  Framework
                </p>

                <p className="mt-1 font-medium text-slate-900">
                  Framework #{audit.framework_id}
                </p>
              </div>

              <div>
                <p className="text-sm text-slate-500">
                  Auditor
                </p>

                <p className="mt-1 font-medium text-slate-900">
                  User #{audit.auditor_id}
                </p>
              </div>

              <div>
                <p className="text-sm text-slate-500">
                  Status
                </p>

                <span className="mt-2 inline-flex rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">
                  {audit.status}
                </span>
              </div>

              <div>
                <p className="text-sm text-slate-500">
                  Scope
                </p>

                <p className="mt-1 whitespace-pre-wrap leading-6 text-slate-700">
                  {audit.scope}
                </p>
              </div>
            </div>

            <div className="mt-6 grid gap-6 border-t pt-6 md:grid-cols-2">
              <div className="flex items-start gap-3">
                <CalendarDays
                  size={18}
                  className="mt-0.5 text-slate-400"
                />

                <div>
                  <p className="text-sm text-slate-500">
                    Audit Period
                  </p>

                  <p className="mt-1 font-medium text-slate-900">
                    {new Date(
                      audit.start_date
                    ).toLocaleDateString()}{" "}
                    –{" "}
                    {new Date(
                      audit.end_date
                    ).toLocaleDateString()}
                  </p>
                </div>
              </div>

              <div>
                <p className="text-sm text-slate-500">
                  Created / Updated
                </p>

                <p className="mt-1 font-medium text-slate-900">
                  {new Date(
                    audit.created_at
                  ).toLocaleString()}
                </p>

                <p className="mt-1 text-xs text-slate-400">
                  Updated{" "}
                  {new Date(
                    audit.updated_at
                  ).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Findings */}
        <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
          <div className="flex items-center justify-between border-b bg-slate-50 p-6">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-orange-100 p-2.5">
                <ClipboardList
                  size={20}
                  className="text-orange-600"
                />
              </div>

              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Audit Findings
                </h2>

                <p className="text-sm text-slate-500">
                  Findings raised during this audit
                </p>
              </div>
            </div>

            {!findingsLoading && !findingsError && (
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                {auditFindings.length}{" "}
                {auditFindings.length === 1
                  ? "Finding"
                  : "Findings"}
              </span>
            )}
          </div>

          <div className="p-6">
            {findingsLoading ? (
              <div className="rounded-lg border border-dashed p-8 text-center text-sm text-slate-500">
                Loading audit findings...
              </div>
            ) : findingsError ? (
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-5 text-sm text-amber-700">
                Findings could not be loaded for this audit.
              </div>
            ) : auditFindings.length === 0 ? (
              <div className="rounded-lg border border-dashed p-8 text-center">
                <ClipboardList className="mx-auto h-8 w-8 text-slate-300" />

                <p className="mt-3 font-medium text-slate-700">
                  No findings recorded for this audit
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  Findings created against this audit will appear here.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {auditFindings.map((finding) => (
                  <div
                    key={finding.id}
                    className="flex flex-col gap-4 rounded-xl border p-4 transition hover:border-slate-300 hover:bg-slate-50 md:flex-row md:items-center md:justify-between"
                  >
                    <div className="min-w-0">
                      <div className="flex flex-wrap items-center gap-2">
                        <span className="text-xs font-medium text-slate-400">
                          Finding #{finding.id}
                        </span>

                        <span
                          className={`rounded-full px-2.5 py-1 text-xs font-semibold ${severityClass(
                            finding.severity
                          )}`}
                        >
                          {finding.severity}
                        </span>

                        <span
                          className={`rounded-full px-2.5 py-1 text-xs font-semibold ${statusClass(
                            finding.status
                          )}`}
                        >
                          {finding.status}
                        </span>
                      </div>

                      <h3 className="mt-2 truncate font-semibold text-slate-900">
                        {finding.title}
                      </h3>

                      <p className="mt-1 text-sm text-slate-500">
                        Control: {finding.control_name}
                      </p>
                    </div>

                    <button
                      type="button"
                      onClick={() =>
                        navigate(
                          `/audit-findings/${finding.id}`
                        )
                      }
                      className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-white hover:text-indigo-600"
                    >
                      <Eye size={16} />
                      View Finding
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        </div>

        {/* AI Audit Intelligence */}
        <AuditAIInsights auditId={audit.id} />
      </div>
    </AppLayout>
  );
}