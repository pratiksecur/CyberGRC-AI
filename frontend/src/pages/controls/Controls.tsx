import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useControls } from "@/hooks/useControls";
import { useDeleteControl } from "@/hooks/useDeleteControl";

import ControlFilters from "@/components/controls/ControlFilters";
import ControlStats from "@/components/controls/ControlStats";
import ControlStatusChart from "@/components/controls/ControlStatusChart";
import FrameworkCoverage from "@/components/controls/FrameworkCoverage";
import RecentControls from "@/components/controls/RecentControls";
import HighestFramework from "@/components/controls/HighestFramework";
import ControlsTable from "@/components/controls/ControlsTable";

export default function Controls() {
  const navigate = useNavigate();

  const deleteMutation = useDeleteControl();

  const {
    data,
    isLoading,
    error,
  } = useControls();

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [type, setType] = useState("");

  const filteredControls = useMemo(() => {
    if (!data) return [];

    return data.filter((control) => {
      const matchesSearch =
        control.title
          .toLowerCase()
          .includes(search.toLowerCase()) ||
        control.description
          .toLowerCase()
          .includes(search.toLowerCase()) ||
        control.control_type
          .toLowerCase()
          .includes(search.toLowerCase());

      const matchesStatus =
        status === "" ||
        control.status === status;

      const matchesType =
        type === "" ||
        control.control_type === type;

      return (
        matchesSearch &&
        matchesStatus &&
        matchesType
      );
    });
  }, [data, search, status, type]);

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading Controls...
        </div>
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Failed to load controls.
        </div>
      </AppLayout>
    );
  }

  const activeControls = filteredControls.filter(
    (c) => c.status === "Active"
  ).length;

  const inactiveControls = filteredControls.filter(
    (c) => c.status !== "Active"
  ).length;

  const frameworkData = [
    ...new Map(
      filteredControls.map((control) => [
        control.control_type,
        {
          framework: control.control_type,
          count: filteredControls.filter(
            (c) =>
              c.control_type === control.control_type
          ).length,
        },
      ])
    ).values(),
  ];

  return (
    <AppLayout>
      <div className="space-y-6">

        {/* Header */}

        <div>
          <h1 className="text-3xl font-bold">
            Control Management
          </h1>

          <p className="text-slate-500">
            Manage cybersecurity controls.
          </p>
        </div>

        {/* Filters */}

        <ControlFilters
          search={search}
          onSearchChange={setSearch}
          status={status}
          onStatusChange={setStatus}
          framework={type}
          onFrameworkChange={setType}
          onCreate={() => navigate("/controls/new")}
        />

        {/* Statistics */}

        <ControlStats
          totalControls={filteredControls.length}
          activeControls={activeControls}
          inactiveControls={inactiveControls}
          frameworks={frameworkData.length}
        />

        {/* Charts */}

        <div className="grid gap-6 lg:grid-cols-2">

          <ControlStatusChart
            active={activeControls}
            inactive={inactiveControls}
          />

          <FrameworkCoverage
            data={frameworkData}
          />

        </div>

        {/* Recent Controls */}

        <div className="grid gap-6 lg:grid-cols-2">

          <RecentControls
            controls={filteredControls}
          />

          <HighestFramework
            controls={filteredControls}
          />

        </div>

        {/* Controls Table */}

        <ControlsTable
          controls={filteredControls}
          onView={(id) =>
            navigate(`/controls/${id}`)
          }
          onEdit={(id) =>
            navigate(`/controls/${id}/edit`)
          }
          onDelete={async (id) => {
            const confirmed = window.confirm(
              "Are you sure you want to delete this control?"
            );

            if (!confirmed) return;

            try {
              await deleteMutation.mutateAsync(id);
            } catch (error) {
              console.error(error);
              alert("Failed to delete control.");
            }
          }}
        />

      </div>
    </AppLayout>
  );
}