import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useAudits } from "@/hooks/useAudits";
import { useDeleteAudit } from "@/hooks/useDeleteAudit";

import AuditFilters from "@/components/audits/AuditFilters";
import AuditStats from "@/components/audits/AuditStats";
import AuditStatusChart from "@/components/audits/AuditStatusChart";
import AuditCards from "@/components/audits/AuditCards";
import RecentAudits from "@/components/audits/RecentAudits";
import AuditTable from "@/components/audits/AuditTable";

export default function Audits() {
  const navigate = useNavigate();

  const deleteMutation = useDeleteAudit();

  const {
    data,
    isLoading,
    error,
  } = useAudits();

  const [search, setSearch] = useState("");

  const [status, setStatus] = useState("");

  const filteredAudits = useMemo(() => {
    if (!data) return [];

    return data.filter((audit) => {
      const matchesSearch =
        audit.name
          .toLowerCase()
          .includes(search.toLowerCase()) ||
        audit.scope
          .toLowerCase()
          .includes(search.toLowerCase());

      const matchesStatus =
        status === "" ||
        audit.status === status;

      return (
        matchesSearch &&
        matchesStatus
      );
    });
  }, [data, search, status]);

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading Audits...
        </div>
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Failed to load audits.
        </div>
      </AppLayout>
    );
  }

  const planned = filteredAudits.filter(
    (a) => a.status === "Planned"
  ).length;

  const inProgress = filteredAudits.filter(
    (a) => a.status === "In Progress"
  ).length;

  const completed = filteredAudits.filter(
    (a) => a.status === "Completed"
  ).length;

  return (
    <AppLayout>
      <div className="space-y-6">

        {/* Header */}

        <div>
          <h1 className="text-3xl font-bold">
            Audit Management
          </h1>

          <p className="text-slate-500">
            Manage cybersecurity audits.
          </p>
        </div>

        {/* Filters */}

        <AuditFilters
          search={search}
          onSearchChange={setSearch}
          status={status}
          onStatusChange={setStatus}
          onCreate={() =>
            navigate("/audits/new")
          }
        />

        {/* Statistics */}

        <AuditStats
          totalAudits={
            filteredAudits.length
          }
          planned={planned}
          inProgress={inProgress}
          completed={completed}
        />

        {/* Charts */}

        <div className="grid gap-6 lg:grid-cols-2">

          <AuditStatusChart
            planned={planned}
            inProgress={inProgress}
            completed={completed}
          />

          <AuditCards
            audits={filteredAudits}
          />

        </div>

        {/* Recent Audits */}

        <RecentAudits
          audits={filteredAudits}
        />

        {/* Table */}

        <AuditTable
          audits={filteredAudits}
          onView={(id) =>
            navigate(`/audits/${id}`)
          }
          onEdit={(id) =>
            navigate(`/audits/${id}/edit`)
          }
          onDelete={async (id) => {
            const confirmed = window.confirm(
              "Are you sure you want to delete this audit?\n\nThis action cannot be undone."
            );

            if (!confirmed) return;

            try {
              await deleteMutation.mutateAsync(id);

              window.alert("Audit deleted successfully.");
            } catch (error) {
              console.error(error);

              window.alert(
                "Unable to delete the audit. Please try again."
              );
            }
          }}
        />

      </div>
    </AppLayout>
  );
}