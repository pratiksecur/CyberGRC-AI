import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  CalendarDays,
  Eye,
  FileText,
  Pencil,
  ShieldCheck,
} from "lucide-react";

import AppLayout from "@/layouts/AppLayout";

import { useFramework } from "@/hooks/useFramework";
import { useFrameworkControl } from "@/hooks/useFrameworkControl";
import { useControlsForFrameworkControl } from "@/hooks/useControlsForFrameworkControl";

import Can from "@/components/auth/Can";

export default function ViewFrameworkControl() {
  const { id } = useParams();
  const navigate = useNavigate();

  const frameworkControlId = Number(id);

  const {
    data,
    isLoading,
    error,
  } = useFrameworkControl(
    frameworkControlId
  );

  const {
    data: framework,
    isLoading: frameworkLoading,
  } = useFramework(
    data?.framework_id ?? 0
  );

  const {
    data: mappedControls,
    isLoading: mappingsLoading,
    error: mappingsError,
  } = useControlsForFrameworkControl(
    frameworkControlId
  );

  if (
    isLoading ||
    frameworkLoading ||
    mappingsLoading
  ) {
    return (
      <AppLayout>
        <div className="mx-auto max-w-5xl space-y-4">
          <div className="h-5 w-32 animate-pulse rounded bg-slate-200" />
          <div className="h-10 w-80 animate-pulse rounded bg-slate-200" />
          <div className="h-72 animate-pulse rounded-2xl bg-slate-100" />
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
              Framework Requirement Not Found
            </h2>

            <p className="mt-1 text-sm text-red-600">
              The requested framework requirement could not be found within your access scope.
            </p>

            <button
              type="button"
              onClick={() =>
                navigate("/framework-controls")
              }
              className="mt-4 flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
            >
              <ArrowLeft size={16} />
              Back to Framework Requirements
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
                navigate(
                  `/frameworks/${data.framework_id}`
                )
              }
              className="mb-4 flex items-center gap-2 text-sm text-slate-500 transition hover:text-slate-900"
            >
              <ArrowLeft size={16} />
              Back to Framework
            </button>

            <div className="flex items-start gap-3">
              <div className="rounded-xl bg-blue-100 p-3">
                <ShieldCheck
                  size={22}
                  className="text-blue-600"
                />
              </div>

              <div>
                <p className="font-mono text-sm font-semibold text-blue-600">
                  {data.control_code}
                </p>

                <h1 className="mt-1 text-3xl font-bold text-slate-900">
                  {data.title}
                </h1>

                <p className="mt-1 text-slate-500">
                  Framework Requirement #{data.id}
                </p>
              </div>
            </div>
          </div>

          <Can
            resource="framework_controls"
            action="update"
          >
            <button
              type="button"
              onClick={() =>
                navigate(
                  `/framework-controls/${data.id}/edit`
                )
              }
              className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700"
            >
              <Pencil size={16} />
              Edit Requirement
            </button>
          </Can>
        </div>

        {/* Requirement Overview */}
        <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">
          <div className="border-b bg-slate-50 p-6">
            <div className="flex items-center gap-3">
              <div className="rounded-lg bg-blue-100 p-2.5">
                <FileText
                  size={20}
                  className="text-blue-600"
                />
              </div>

              <div>
                <h2 className="text-lg font-semibold text-slate-900">
                  Requirement Details
                </h2>

                <p className="text-sm text-slate-500">
                  Framework requirement and compliance mapping context
                </p>
              </div>
            </div>
          </div>

          <div className="p-6">
            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <p className="text-sm font-semibold text-slate-500">
                  Requirement Code
                </p>

                <p className="mt-1 font-mono font-medium text-slate-900">
                  {data.control_code}
                </p>
              </div>

              <div>
                <p className="text-sm font-semibold text-slate-500">
                  Framework
                </p>

                <button
                  type="button"
                  onClick={() =>
                    navigate(
                      `/frameworks/${data.framework_id}`
                    )
                  }
                  className="mt-1 text-left font-medium text-indigo-600 transition hover:text-indigo-800"
                >
                  {framework?.name ??
                    `Framework #${data.framework_id}`}
                </button>

                <p className="mt-1 text-xs text-slate-400">
                  Version{" "}
                  {framework?.version ??
                    "—"}
                </p>
              </div>
            </div>

            <div className="mt-6 border-t pt-6">
              <p className="text-sm font-semibold text-slate-500">
                Description
              </p>

              <p className="mt-2 whitespace-pre-wrap leading-7 text-slate-600">
                {data.description}
              </p>
            </div>

            <div className="mt-6 grid gap-6 border-t pt-6 md:grid-cols-2">
              <div className="flex items-start gap-3">
                <CalendarDays
                  size={18}
                  className="mt-0.5 text-slate-400"
                />

                <div>
                  <p className="text-sm font-semibold text-slate-500">
                    Created
                  </p>

                  <p className="mt-1 text-sm text-slate-700">
                    {new Date(
                      data.created_at
                    ).toLocaleString()}
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3">
                <CalendarDays
                  size={18}
                  className="mt-0.5 text-slate-400"
                />

                <div>
                  <p className="text-sm font-semibold text-slate-500">
                    Updated
                  </p>

                  <p className="mt-1 text-sm text-slate-700">
                    {new Date(
                      data.updated_at
                    ).toLocaleString()}
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Organizational Control Mappings */}
        <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">
          <div className="flex items-center justify-between gap-4 border-b bg-slate-50 p-6">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                Mapped Organizational Controls
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Organizational controls that satisfy or support this framework requirement.
              </p>
            </div>

            {!mappingsError && (
              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-semibold text-slate-700">
                {mappedControls?.length ?? 0}{" "}
                {(mappedControls?.length ?? 0) === 1
                  ? "Control"
                  : "Controls"}
              </span>
            )}
          </div>

          <div className="p-6">
            {mappingsError ? (
              <div className="rounded-lg border border-amber-200 bg-amber-50 p-5">
                <p className="font-medium text-amber-800">
                  Organizational control mappings could not be loaded.
                </p>

                <p className="mt-1 text-sm text-amber-700">
                  Please refresh the page and try again.
                </p>
              </div>
            ) : !mappedControls ||
              mappedControls.length === 0 ? (
              <div className="rounded-xl border border-dashed p-10 text-center">
                <ShieldCheck className="mx-auto h-9 w-9 text-slate-300" />

                <p className="mt-3 font-medium text-slate-700">
                  No organizational controls are mapped
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  Controls mapped to this framework requirement will appear here.
                </p>
              </div>
            ) : (
              <div className="space-y-3">
                {mappedControls.map(
                  (control) => (
                    <div
                      key={control.id}
                      className="flex flex-col gap-4 rounded-xl border p-4 transition hover:border-slate-300 hover:bg-slate-50 md:flex-row md:items-center md:justify-between"
                    >
                      <div className="flex min-w-0 items-start gap-3">
                        <div className="rounded-lg bg-indigo-100 p-2">
                          <ShieldCheck
                            size={18}
                            className="text-indigo-600"
                          />
                        </div>

                        <div className="min-w-0">
                          <p className="truncate font-semibold text-slate-900">
                            {control.title}
                          </p>

                          <p className="mt-1 text-sm text-slate-500">
                            {control.control_type}
                          </p>

                          <div className="mt-2 flex flex-wrap gap-2 text-xs">
                            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-slate-600">
                              Status: {control.status}
                            </span>

                            <span className="rounded-full bg-slate-100 px-2.5 py-1 text-slate-600">
                              Effectiveness:{" "}
                              {control.effectiveness}%
                            </span>
                          </div>
                        </div>
                      </div>

                      <button
                        type="button"
                        onClick={() =>
                          navigate(
                            `/controls/${control.id}`
                          )
                        }
                        className="inline-flex shrink-0 items-center justify-center gap-2 rounded-lg border px-4 py-2 text-sm font-medium text-slate-700 transition hover:bg-white hover:text-indigo-600"
                      >
                        <Eye size={16} />
                        View Control
                      </button>
                    </div>
                  )
                )}
              </div>
            )}
          </div>
        </div>
      </div>
    </AppLayout>
  );
}