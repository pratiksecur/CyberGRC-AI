import { useParams, useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useControl } from "@/hooks/useControl";
import { useFrameworkControls } from "@/hooks/useFrameworkControls";
import { useFrameworks } from "@/hooks/useFrameworks";
import { useFrameworkControlsForControl } from "@/hooks/useFrameworkControlsForControl";
import { useCreateControlFrameworkMapping } from "@/hooks/useCreateControlFrameworkMapping";

import Can from "@/components/auth/Can";

export default function ViewControl() {
  const { id } = useParams();
  const navigate = useNavigate();

  const controlId = Number(id);

  const {
    data,
    isLoading,
    error,
  } = useControl(controlId);

  const {
    data: frameworkControls,
    isLoading: frameworkControlsLoading,
  } = useFrameworkControls();

  const {
    data: frameworks,
    isLoading: frameworksLoading,
  } = useFrameworks();

  const {
    data: mappedFrameworkControls,
    isLoading: mappingsLoading,
  } =
    useFrameworkControlsForControl(
      controlId
    );

  const mappingMutation =
    useCreateControlFrameworkMapping();

  if (
    isLoading ||
    frameworkControlsLoading ||
    frameworksLoading ||
    mappingsLoading
  ) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading control...
        </div>
      </AppLayout>
    );
  }

  if (
    error ||
    !data ||
    !frameworkControls ||
    !frameworks
  ) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Failed to load control.
        </div>
      </AppLayout>
    );
  }

  const mappedIds = new Set(
    (mappedFrameworkControls ?? []).map(
      (item) => item.id
    )
  );

  const availableFrameworkControls =
    frameworkControls.filter(
      (item) => !mappedIds.has(item.id)
    );

  const frameworkNameById =
    new Map(
      frameworks.map((framework) => [
        framework.id,
        `${framework.name} ${framework.version}`,
      ])
    );

  return (
    <AppLayout>

      <div className="mx-auto max-w-4xl space-y-6">

        {/* Header */}

        <div className="flex items-center justify-between">

          <div>

            <h1 className="text-3xl font-bold">
              {data.title}
            </h1>

            <p className="text-slate-500">
              View cybersecurity control
            </p>

          </div>

          <button
            type="button"
            onClick={() =>
              navigate("/controls")
            }
            className="rounded-lg border px-4 py-2 hover:bg-slate-100"
          >
            Back
          </button>

        </div>

        {/* Details */}

        <div className="space-y-8 rounded-2xl border bg-white p-8">

          <div>

            <h2 className="mb-2 text-lg font-semibold">
              Description
            </h2>

            <p className="text-slate-600">
              {data.description}
            </p>

          </div>

          <div className="grid gap-6 md:grid-cols-2">

            <div>

              <p className="text-sm text-slate-500">
                Control Type
              </p>

              <p className="font-medium">
                {data.control_type}
              </p>

            </div>

            <div>

              <p className="text-sm text-slate-500">
                Status
              </p>

              <p className="font-medium">
                {data.status}
              </p>

            </div>

            <div>

              <p className="text-sm text-slate-500">
                Effectiveness
              </p>

              <p className="font-medium">
                {data.effectiveness}%
              </p>

            </div>

            <div>

              <p className="text-sm text-slate-500">
                Owner
              </p>

              <p className="font-medium">
                User #{data.owner_id}
              </p>

            </div>

            <div>

              <p className="text-sm text-slate-500">
                Created
              </p>

              <p className="font-medium">
                {new Date(
                  data.created_at
                ).toLocaleString()}
              </p>

            </div>

            <div>

              <p className="text-sm text-slate-500">
                Updated
              </p>

              <p className="font-medium">
                {new Date(
                  data.updated_at
                ).toLocaleString()}
              </p>

            </div>

          </div>

        </div>

        {/* Framework Mapping */}

        <div className="rounded-2xl border bg-white">

          <div className="border-b p-6">

            <h2 className="text-lg font-semibold">
              Framework Requirements
            </h2>

            <p className="text-sm text-slate-500">
              Compliance requirements mapped to this control.
            </p>

          </div>

          <div className="space-y-4 p-6">

            {mappedFrameworkControls &&
            mappedFrameworkControls.length > 0 ? (

              mappedFrameworkControls.map(
                (frameworkControl) => (

                  <button
                    key={frameworkControl.id}
                    type="button"
                    onClick={() =>
                      navigate(
                        `/framework-controls/${frameworkControl.id}`
                      )
                    }
                    className="flex w-full items-center justify-between rounded-lg border p-4 text-left hover:bg-slate-50"
                  >

                    <div>

                      <p className="font-mono text-sm text-blue-600">
                        {frameworkControl.control_code}
                      </p>

                      <p className="font-medium">
                        {frameworkControl.title}
                      </p>

                      <p className="text-sm text-slate-500">
                        {frameworkNameById.get(
                          frameworkControl.framework_id
                        ) ??
                          `Framework #${frameworkControl.framework_id}`}
                      </p>

                    </div>

                    <span className="text-sm text-blue-600">
                      View
                    </span>

                  </button>

                )
              )

            ) : (

              <p className="text-sm text-slate-500">
                No framework requirements are mapped to this control.
              </p>

            )}

          </div>

          {/* Create Mapping */}

          <Can
            resource="control_framework_mappings"
            action="create"
          >
            <div className="border-t p-6">

              <h3 className="mb-3 font-semibold">
                Map Framework Requirement
              </h3>

              <div className="flex flex-col gap-3 sm:flex-row">

                <select
                  id="framework-control"
                  defaultValue=""
                  className="flex-1 rounded-lg border px-4 py-2"
                >
                  <option value="">
                    Select framework requirement
                  </option>

                  {availableFrameworkControls.map(
                    (frameworkControl) => (
                      <option
                        key={frameworkControl.id}
                        value={frameworkControl.id}
                      >
                        {frameworkControl.control_code} —{" "}
                        {frameworkControl.title}
                      </option>
                    )
                  )}

                </select>

                <button
                  type="button"
                  disabled={
                    mappingMutation.isPending ||
                    availableFrameworkControls.length === 0
                  }
                  onClick={async () => {
                    const select =
                      document.getElementById(
                        "framework-control"
                      ) as HTMLSelectElement;

                    const frameworkControlId =
                      Number(select.value);

                    if (
                      !frameworkControlId
                    ) {
                      alert(
                        "Please select a framework requirement."
                      );
                      return;
                    }

                    try {
                      await mappingMutation.mutateAsync({
                        control_id:
                          controlId,
                        framework_control_id:
                          frameworkControlId,
                      });

                      select.value = "";
                    } catch (error) {
                      console.error(error);
                      alert(
                        "Failed to create framework mapping."
                      );
                    }
                  }}
                  className="rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {mappingMutation.isPending
                    ? "Mapping..."
                    : "Map Control"}
                </button>

              </div>

            </div>
          </Can>

        </div>

      </div>

    </AppLayout>
  );
}