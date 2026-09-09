import { useNavigate, useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

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
    data: mappedControls,
    isLoading: mappingsLoading,
  } =
    useControlsForFrameworkControl(
      frameworkControlId
    );

  if (
    isLoading ||
    mappingsLoading
  ) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading framework control...
        </div>
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Framework control not found.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="mx-auto max-w-5xl space-y-6">
        <div className="flex items-center justify-between">
          <div>
            <p className="font-mono text-sm text-blue-600">
              {data.control_code}
            </p>

            <h1 className="mt-1 text-3xl font-bold">
              {data.title}
            </h1>

            <p className="mt-2 text-slate-500">
              Framework Control
            </p>
          </div>

          <div className="flex gap-3">
            <button
              type="button"
              onClick={() =>
                navigate("/framework-controls")
              }
              className="rounded-lg border px-4 py-2 hover:bg-slate-100"
            >
              Back
            </button>

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
                className="rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
              >
                Edit
              </button>
            </Can>
          </div>
        </div>

        <div className="rounded-2xl border bg-white p-8">
          <div className="space-y-6">
            <div>
              <p className="text-sm font-semibold text-slate-500">
                Control Code
              </p>

              <p className="mt-1 font-mono">
                {data.control_code}
              </p>
            </div>

            <div>
              <p className="text-sm font-semibold text-slate-500">
                Framework
              </p>

              <p className="mt-1">
                Framework #{data.framework_id}
              </p>
            </div>

            <div>
              <p className="text-sm font-semibold text-slate-500">
                Description
              </p>

              <p className="mt-1 whitespace-pre-wrap text-slate-600">
                {data.description}
              </p>
            </div>

            <div className="grid gap-6 md:grid-cols-2">
              <div>
                <p className="text-sm font-semibold text-slate-500">
                  Created
                </p>

                <p className="mt-1">
                  {new Date(
                    data.created_at
                  ).toLocaleString()}
                </p>
              </div>

              <div>
                <p className="text-sm font-semibold text-slate-500">
                  Updated
                </p>

                <p className="mt-1">
                  {new Date(
                    data.updated_at
                  ).toLocaleString()}
                </p>
              </div>
            </div>
          </div>
        </div>

        <div className="rounded-2xl border bg-white">
          <div className="border-b p-6">
            <h2 className="text-lg font-semibold">
              Mapped Organizational Controls
            </h2>

            <p className="text-sm text-slate-500">
              Controls currently mapped to this framework requirement.
            </p>
          </div>

          <div className="p-6">
            {!mappedControls ||
            mappedControls.length === 0 ? (
              <p className="text-sm text-slate-500">
                No controls are currently mapped.
              </p>
            ) : (
              <div className="space-y-3">
                {mappedControls.map(
                  (control) => (
                    <button
                      key={control.id}
                      type="button"
                      onClick={() =>
                        navigate(
                          `/controls/${control.id}`
                        )
                      }
                      className="flex w-full items-center justify-between rounded-lg border p-4 text-left transition hover:bg-slate-50"
                    >
                      <div>
                        <p className="font-medium">
                          {control.title}
                        </p>

                        <p className="text-sm text-slate-500">
                          {control.control_type}
                        </p>
                      </div>

                      <span className="text-sm text-blue-600">
                        View
                      </span>
                    </button>
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