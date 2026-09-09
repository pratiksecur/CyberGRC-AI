import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useFrameworkControls } from "@/hooks/useFrameworkControls";
import { useFrameworks } from "@/hooks/useFrameworks";
import { useDeleteFrameworkControl } from "@/hooks/useDeleteFrameworkControl";

import FrameworkControlFilters from "@/components/framework-controls/FrameworkControlFilters";
import FrameworkControlTable from "@/components/framework-controls/FrameworkControlTable";

export default function FrameworkControls() {
  const navigate = useNavigate();

  const {
    data: controls,
    isLoading: controlsLoading,
    error: controlsError,
  } = useFrameworkControls();

  const {
    data: frameworks,
    isLoading: frameworksLoading,
  } = useFrameworks();

  const deleteMutation =
    useDeleteFrameworkControl();

  const [search, setSearch] =
    useState("");

  const [frameworkId, setFrameworkId] =
    useState("");

  const filteredControls = useMemo(() => {
    if (!controls) return [];

    return controls.filter((control) => {
      const query =
        search.toLowerCase();

      const matchesSearch =
        control.control_code
          .toLowerCase()
          .includes(query) ||
        control.title
          .toLowerCase()
          .includes(query) ||
        control.description
          .toLowerCase()
          .includes(query);

      const matchesFramework =
        frameworkId === "" ||
        control.framework_id ===
          Number(frameworkId);

      return (
        matchesSearch &&
        matchesFramework
      );
    });
  }, [
    controls,
    search,
    frameworkId,
  ]);

  if (
    controlsLoading ||
    frameworksLoading
  ) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading Framework Controls...
        </div>
      </AppLayout>
    );
  }

  if (
    controlsError ||
    !controls ||
    !frameworks
  ) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Failed to load framework controls.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>

      <div className="space-y-6">

        <div>

          <h1 className="text-3xl font-bold">
            Framework Controls
          </h1>

          <p className="text-slate-500">
            Manage controls defined by compliance frameworks.
          </p>

        </div>

        <FrameworkControlFilters
          search={search}
          onSearchChange={setSearch}
          frameworkId={frameworkId}
          onFrameworkChange={
            setFrameworkId
          }
          frameworks={frameworks}
          onCreate={() =>
            navigate(
              "/framework-controls/new"
            )
          }
        />

        <FrameworkControlTable
          controls={filteredControls}
          onView={(id) =>
            navigate(
              `/framework-controls/${id}`
            )
          }
          onEdit={(id) =>
            navigate(
              `/framework-controls/${id}/edit`
            )
          }
          onDelete={async (id) => {
            if (
              !window.confirm(
                "Are you sure you want to delete this framework control?"
              )
            ) {
              return;
            }

            try {
              await deleteMutation.mutateAsync(
                id
              );
            } catch (error) {
              console.error(error);
              alert(
                "Failed to delete framework control."
              );
            }
          }}
        />

      </div>

    </AppLayout>
  );
}