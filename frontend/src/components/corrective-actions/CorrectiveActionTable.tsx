import {
  Eye,
  Pencil,
  Trash2,
} from "lucide-react";

import type { CorrectiveAction } from "@/api/correctiveActions";

interface Props {
  actions: CorrectiveAction[];

  onView: (id: number) => void;
  onEdit: (id: number) => void;
  onDelete: (id: number) => void;
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

function statusClass(status: string) {
  switch (status) {
    case "Completed":
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

function isOverdue(action: CorrectiveAction) {
  if (!action.due_date) return false;

  if (
    action.status === "Completed" ||
    action.status === "Closed"
  ) {
    return false;
  }

  return (
    new Date(action.due_date) <
    new Date()
  );
}

export default function CorrectiveActionTable({
  actions,
  onView,
  onEdit,
  onDelete,
}: Props) {
  return (
    <div className="overflow-hidden rounded-xl border bg-white shadow-sm">
      <div className="overflow-x-auto">
        <table className="min-w-full">
          <thead className="border-b bg-slate-50">
            <tr>
              <th className="px-6 py-4 text-left text-sm font-semibold">
                Corrective Action
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Finding
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Assignee
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Priority
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Status
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Due Date
              </th>

              <th className="px-6 py-4 text-right text-sm font-semibold">
                Actions
              </th>
            </tr>
          </thead>

          <tbody>
            {actions.map((action) => {
              const overdue =
                isOverdue(action);

              return (
                <tr
                  key={action.id}
                  className="border-b transition hover:bg-slate-50 last:border-0"
                >
                  {/* Action */}

                  <td className="px-6 py-5">
                    <div className="font-semibold text-slate-900">
                      {action.title}
                    </div>

                    <div className="mt-1 max-w-xs truncate text-sm text-slate-500">
                      {action.description}
                    </div>
                  </td>

                  {/* Finding */}

                  <td className="px-6 py-5">
                    <div className="max-w-xs truncate text-sm text-slate-700">
                      {action.finding_title}
                    </div>

                    <div className="mt-1 text-xs text-slate-400">
                      Finding #{action.finding_id}
                    </div>
                  </td>

                  {/* Assignee */}

                  <td className="px-6 py-5">
                    <div className="text-sm font-medium text-slate-800">
                      {action.assignee_name}
                    </div>
                  </td>

                  {/* Priority */}

                  <td className="px-6 py-5">
                    <span
                      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${priorityClass(
                        action.priority
                      )}`}
                    >
                      {action.priority}
                    </span>
                  </td>

                  {/* Status */}

                  <td className="px-6 py-5">
                    <span
                      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${statusClass(
                        action.status
                      )}`}
                    >
                      {action.status}
                    </span>
                  </td>

                  {/* Due Date */}

                  <td className="px-6 py-5">
                    {action.due_date ? (
                      <div>
                        <div
                          className={`text-sm font-medium ${
                            overdue
                              ? "text-red-600"
                              : "text-slate-700"
                          }`}
                        >
                          {new Date(
                            action.due_date
                          ).toLocaleDateString()}
                        </div>

                        {overdue && (
                          <div className="mt-1 text-xs font-medium text-red-500">
                            Overdue
                          </div>
                        )}
                      </div>
                    ) : (
                      <span className="text-sm text-slate-400">
                        No due date
                      </span>
                    )}
                  </td>

                  {/* Actions */}

                  <td className="px-6 py-5 text-right">
                    <div className="flex justify-end gap-1">
                      <button
                        type="button"
                        onClick={() =>
                          onView(action.id)
                        }
                        title="View Action"
                        className="rounded-lg p-2 text-slate-600 transition hover:bg-blue-100 hover:text-blue-600"
                      >
                        <Eye size={18} />
                      </button>

                      <button
                        type="button"
                        onClick={() =>
                          onEdit(action.id)
                        }
                        title="Edit Action"
                        className="rounded-lg p-2 text-slate-600 transition hover:bg-amber-100 hover:text-amber-600"
                      >
                        <Pencil size={18} />
                      </button>

                      <button
                        type="button"
                        onClick={() =>
                          onDelete(action.id)
                        }
                        title="Delete Action"
                        className="rounded-lg p-2 text-slate-600 transition hover:bg-red-100 hover:text-red-600"
                      >
                        <Trash2 size={18} />
                      </button>
                    </div>
                  </td>
                </tr>
              );
            })}

            {actions.length === 0 && (
              <tr>
                <td
                  colSpan={7}
                  className="p-12 text-center"
                >
                  <div className="text-sm font-medium text-slate-600">
                    No corrective actions found.
                  </div>

                  <div className="mt-1 text-sm text-slate-400">
                    Try changing your filters or create a new corrective action.
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