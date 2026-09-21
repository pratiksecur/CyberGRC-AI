import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  CalendarDays,
  ClipboardCheck,
  Eye,
  Pencil,
  User,
} from "lucide-react";

import AppLayout from "@/layouts/AppLayout";

import { useCorrectiveAction } from "@/hooks/useCorrectiveAction";

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
    case "Pending":
      return "bg-blue-100 text-blue-700";

    default:
      return "bg-slate-100 text-slate-700";
  }
}

export default function ViewCorrectiveAction() {
  const { id } = useParams();
  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
  } = useCorrectiveAction(Number(id));

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading Corrective Action...
        </div>
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="mx-auto max-w-4xl p-10">
          <div className="rounded-xl border border-red-200 bg-red-50 p-6">
            <h2 className="font-semibold text-red-700">
              Corrective Action Not Found
            </h2>

            <p className="mt-1 text-sm text-red-600">
              The requested corrective action could not be found within your access scope.
            </p>

            <button
              type="button"
              onClick={() =>
                navigate("/corrective-actions")
              }
              className="mt-4 flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
            >
              <ArrowLeft size={16} />
              Back to Corrective Actions
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
              type="button"
              onClick={() =>
                navigate("/corrective-actions")
              }
              className="mb-4 flex items-center gap-2 text-sm text-slate-500 transition hover:text-slate-900"
            >
              <ArrowLeft size={16} />
              Back to Corrective Actions
            </button>

            <h1 className="text-3xl font-bold text-slate-900">
              {data.title}
            </h1>

            <p className="mt-1 text-slate-500">
              Corrective Action #{data.id}
            </p>
          </div>

          <button
            type="button"
            onClick={() =>
              navigate(
                `/corrective-actions/${data.id}/edit`
              )
            }
            className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700"
          >
            <Pencil size={16} />
            Edit Action
          </button>
        </div>

        {/* Main Card */}
        <div className="rounded-xl border bg-white p-8 shadow-sm">
          {/* Status */}
          <div className="mb-8 flex flex-wrap gap-3">
            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold ${priorityClass(
                data.priority
              )}`}
            >
              {data.priority} Priority
            </span>

            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold ${statusClass(
                data.status
              )}`}
            >
              {data.status}
            </span>
          </div>

          {/* Information */}
          <div className="grid gap-6 md:grid-cols-2">
            <div className="flex gap-3">
              <ClipboardCheck
                className="mt-1 text-slate-400"
                size={20}
              />

              <div>
                <p className="text-sm font-medium text-slate-500">
                  Audit Finding
                </p>

                <p className="mt-1 font-medium text-slate-900">
                  {data.finding_title}
                </p>

                <p className="text-xs text-slate-400">
                  Finding #{data.finding_id}
                </p>

                <button
                  type="button"
                  onClick={() =>
                    navigate(
                      `/audit-findings/${data.finding_id}`
                    )
                  }
                  className="mt-3 inline-flex items-center gap-2 text-sm font-medium text-indigo-600 transition hover:text-indigo-800"
                >
                  <Eye size={15} />
                  View Finding
                </button>
              </div>
            </div>

            <div className="flex gap-3">
              <User
                className="mt-1 text-slate-400"
                size={20}
              />

              <div>
                <p className="text-sm font-medium text-slate-500">
                  Assigned To
                </p>

                <p className="mt-1 font-medium text-slate-900">
                  {data.assignee_name}
                </p>
              </div>
            </div>

            <div className="flex gap-3">
              <CalendarDays
                className="mt-1 text-slate-400"
                size={20}
              />

              <div>
                <p className="text-sm font-medium text-slate-500">
                  Due Date
                </p>

                <p className="mt-1 font-medium text-slate-900">
                  {data.due_date
                    ? new Date(
                        data.due_date
                      ).toLocaleDateString()
                    : "No due date"}
                </p>
              </div>
            </div>

            <div>
              <p className="text-sm font-medium text-slate-500">
                Created
              </p>

              <p className="mt-1 font-medium text-slate-900">
                {new Date(
                  data.created_at
                ).toLocaleString()}
              </p>
            </div>
          </div>

          {/* Description */}
          <div className="mt-8 border-t pt-8">
            <h3 className="font-semibold text-slate-900">
              Description
            </h3>

            <p className="mt-3 whitespace-pre-wrap leading-7 text-slate-600">
              {data.description}
            </p>
          </div>

          {/* Comments */}
          {data.comments && (
            <div className="mt-8 border-t pt-8">
              <h3 className="font-semibold text-slate-900">
                Comments
              </h3>

              <p className="mt-3 whitespace-pre-wrap leading-7 text-slate-600">
                {data.comments}
              </p>
            </div>
          )}

          {/* Completed */}
          {data.completed_at && (
            <div className="mt-8 border-t pt-8">
              <h3 className="font-semibold text-slate-900">
                Completed At
              </h3>

              <p className="mt-2 text-slate-600">
                {new Date(
                  data.completed_at
                ).toLocaleString()}
              </p>
            </div>
          )}
        </div>
      </div>
    </AppLayout>
  );
}