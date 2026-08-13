import AppLayout from "@/layouts/AppLayout";

import { useControls } from "@/hooks/useControls";

import ControlFilters from "@/components/controls/ControlFilters";
import ControlStats from "@/components/controls/ControlStats";
import ControlStatusChart from "@/components/controls/ControlStatusChart";
import FrameworkCoverage from "@/components/controls/FrameworkCoverage";
import RecentControls from "@/components/controls/RecentControls";
import HighestFramework from "@/components/controls/HighestFramework";
import ControlsTable from "@/components/controls/ControlsTable";

export default function Controls() {
  const {
    data,
    isLoading,
    error,
  } = useControls();

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

  const activeControls = data.filter(
    (c) => c.status === "Active"
  ).length;

  const inactiveControls = data.filter(
    (c) => c.status !== "Active"
  ).length;

  const frameworkData = [
    ...new Map(
      data.map((control) => [
        control.control_type,
        {
          framework: control.control_type,
          count: data.filter(
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
          search=""
          onSearchChange={() => {}}
          status=""
          onStatusChange={() => {}}
          framework=""
          onFrameworkChange={() => {}}
          onCreate={() => {}}
        />

        {/* Statistics */}

        <ControlStats
          totalControls={data.length}
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

          <RecentControls controls={data} />

          <HighestFramework controls={data} />

        </div>

        {/* Controls Table */}
        
        <ControlsTable
          controls={data}
          onView={(id) => console.log("View", id)}
          onEdit={(id) => console.log("Edit", id)}
          onDelete={(id) => console.log("Delete", id)}
        />

      </div>
    </AppLayout>
  );
}