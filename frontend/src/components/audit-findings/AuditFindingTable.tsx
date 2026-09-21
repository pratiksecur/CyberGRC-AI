import {
  Eye,
  Pencil,
  Trash2,
} from "lucide-react";

import Can from "@/components/auth/Can";

import type { AuditFinding } from "@/api/auditFindings";

interface Props {
  findings: AuditFinding[];
  onView: (id: number) => void;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
}

function getSeverityClass(
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

function getStatusClass(
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

export default function AuditFindingTable({
  findings,
  onView,
  onEdit,
  onDelete,
}: Props) {
  return (
    <div className="overflow-hidden rounded-xl border bg-white shadow-sm">

      <div className="overflow-x-auto">

        <table className="w-full min-w-[900px]">

          <thead className="border-b bg-slate-50">

            <tr>

              <th className="p-4 text-left text-sm font-semibold text-slate-600">
                Finding
              </th>

              <th className="p-4 text-left text-sm font-semibold text-slate-600">
                Audit
              </th>

              <th className="p-4 text-left text-sm font-semibold text-slate-600">
                Control
              </th>

              <th className="p-4 text-center text-sm font-semibold text-slate-600">
                Severity
              </th>

              <th className="p-4 text-center text-sm font-semibold text-slate-600">
                Status
              </th>

              <th className="p-4 text-center text-sm font-semibold text-slate-600">
                Actions
              </th>

            </tr>

          </thead>

          <tbody>

            {findings.map((finding) => (

              <tr
                key={finding.id}
                className="border-b transition hover:bg-slate-50 last:border-0"
              >

                <td className="p-4">

                  <div className="max-w-[280px]">

                    <p className="truncate font-semibold text-slate-800">
                      {finding.title}
                    </p>

                    <p className="mt-1 truncate text-xs text-slate-500">
                      Finding #{finding.id}
                    </p>

                  </div>

                </td>

                <td className="p-4">

                  <p className="max-w-[220px] truncate text-sm text-slate-700">
                    {finding.audit_name}
                  </p>

                </td>

                <td className="p-4">

                  <p className="max-w-[220px] truncate text-sm text-slate-700">
                    {finding.control_name}
                  </p>

                </td>

                <td className="p-4 text-center">

                  <span
                    className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${getSeverityClass(
                      finding.severity
                    )}`}
                  >
                    {finding.severity}
                  </span>

                </td>

                <td className="p-4 text-center">

                  <span
                    className={`inline-flex rounded-full border px-3 py-1 text-xs font-semibold ${getStatusClass(
                      finding.status
                    )}`}
                  >
                    {finding.status}
                  </span>

                </td>

                <td className="p-4">

                  <div className="flex justify-center gap-1">

                    <Can
                      resource="audit_findings"
                      action="view"
                    >
                      <button
                        type="button"
                        onClick={() =>
                          onView(finding.id)
                        }
                        title="View Finding"
                        className="rounded-lg p-2 text-slate-500 transition hover:bg-blue-100 hover:text-blue-600"
                      >
                        <Eye size={18} />
                      </button>
                    </Can>

                    <Can
                      resource="audit_findings"
                      action="update"
                    >
                      <button
                        type="button"
                        onClick={() =>
                          onEdit(finding.id)
                        }
                        title="Edit Finding"
                        className="rounded-lg p-2 text-slate-500 transition hover:bg-amber-100 hover:text-amber-600"
                      >
                        <Pencil size={18} />
                      </button>
                    </Can>

                    <Can
                      resource="audit_findings"
                      action="delete"
                    >
                      <button
                        type="button"
                        onClick={() =>
                          onDelete(finding.id)
                        }
                        title="Delete Finding"
                        className="rounded-lg p-2 text-slate-500 transition hover:bg-red-100 hover:text-red-600"
                      >
                        <Trash2 size={18} />
                      </button>
                    </Can>

                  </div>

                </td>

              </tr>

            ))}

            {findings.length === 0 && (

              <tr>

                <td
                  colSpan={6}
                  className="p-12 text-center"
                >

                  <div className="mx-auto max-w-md">

                    <div className="mx-auto mb-4 flex h-12 w-12 items-center justify-center rounded-full bg-slate-100">
                      <Eye
                        size={22}
                        className="text-slate-400"
                      />
                    </div>

                    <h3 className="font-semibold text-slate-800">
                      No audit findings found
                    </h3>

                    <p className="mt-1 text-sm text-slate-500">
                      Try changing your filters or create a new audit finding.
                    </p>

                  </div>

                </td>

              </tr>

            )}

          </tbody>

        </table>

      </div>

    </div>
  );
}