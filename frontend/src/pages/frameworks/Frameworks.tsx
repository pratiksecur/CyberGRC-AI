import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useFrameworks } from "@/hooks/useFrameworks";
import { useDeleteFramework } from "@/hooks/useDeleteFramework";

import FrameworkStats from "@/components/frameworks/FrameworkStats";
import FrameworkFilters from "@/components/frameworks/FrameworkFilters";
import FrameworkTable from "@/components/frameworks/FrameworkTable";
import RecentFrameworks from "@/components/frameworks/RecentFrameworks";
import FrameworkVersionChart from "@/components/frameworks/FrameworkVersionChart";
import FrameworkCards from "@/components/frameworks/FrameworkCards";

export default function Frameworks() {
  const navigate = useNavigate();

  const deleteMutation = useDeleteFramework();

  const {
    data,
    isLoading,
    error,
  } = useFrameworks();

  const [search, setSearch] = useState("");
  const [version, setVersion] = useState("");

  const filteredFrameworks = useMemo(() => {
    if (!data) return [];

    return data.filter((framework) => {
      const matchesSearch =
        framework.name
          .toLowerCase()
          .includes(search.toLowerCase()) ||
        framework.description
          .toLowerCase()
          .includes(search.toLowerCase());

      const matchesVersion =
        version === "" ||
        (version === "Latest"
          ? framework.version
              .toLowerCase()
              .includes("latest")
          : !framework.version
              .toLowerCase()
              .includes("latest"));

      return (
        matchesSearch &&
        matchesVersion
      );
    });
  }, [data, search, version]);

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading Frameworks...
        </div>
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Failed to load frameworks.
        </div>
      </AppLayout>
    );
  }

  const latestVersions = filteredFrameworks.filter(
    (framework) =>
      framework.version
        .toLowerCase()
        .includes("latest")
  ).length;

  const olderVersions =
    filteredFrameworks.length -
    latestVersions;

  return (
    <AppLayout>
      <div className="space-y-6">

        {/* Header */}

        <div>
          <h1 className="text-3xl font-bold">
            Framework Management
          </h1>

          <p className="text-slate-500">
            Manage compliance frameworks.
          </p>
        </div>

        {/* Filters */}

        <FrameworkFilters
          search={search}
          onSearchChange={setSearch}
          version={version}
          onVersionChange={setVersion}
          onCreate={() =>
            navigate("/frameworks/new")
          }
        />

        {/* Statistics */}

        <FrameworkStats
          totalFrameworks={
            filteredFrameworks.length
          }
          latestVersion={latestVersions}
          oldVersions={olderVersions}
          totalDocuments={
            filteredFrameworks.length
          }
        />

        {/* Charts */}

        <div className="grid gap-6 lg:grid-cols-2">

          <FrameworkVersionChart
            latest={latestVersions}
            older={olderVersions}
          />

          <FrameworkCards
            frameworks={filteredFrameworks}
          />

        </div>

        {/* Recent */}

        <RecentFrameworks
          frameworks={filteredFrameworks}
        />

        {/* Table */}

        <FrameworkTable
          frameworks={filteredFrameworks}
          onView={(id) =>
            navigate(`/frameworks/${id}`)
          }
          onEdit={(id) =>
            navigate(`/frameworks/${id}/edit`)
          }
          onDelete={async (id) => {
            if (!window.confirm(
              "Delete this framework?"
            )) {
              return;
            }

            try {
              await deleteMutation.mutateAsync(id);
            } catch {
              alert(
                "Failed to delete framework."
              );
            }
          }}
        />

      </div>
    </AppLayout>
  );
}