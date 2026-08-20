import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useAuditFindings } from "@/hooks/useAuditFindings";
import { useDeleteAuditFinding } from "@/hooks/useDeleteAuditFinding";

import { useAudits } from "@/hooks/useAudits";

import AuditFindingFilters from "@/components/audit-findings/AuditFindingFilters";
import AuditFindingStats from "@/components/audit-findings/AuditFindingStats";
import AuditFindingTable from "@/components/audit-findings/AuditFindingTable";

export default function AuditFindings() {
  const navigate = useNavigate();

  const {
    data: findings = [],
    isLoading: findingsLoading,
    error: findingsError,
  } = useAuditFindings();

  const {
    data: audits = [],
    isLoading: auditsLoading,
  } = useAudits();

  const deleteMutation =
    useDeleteAuditFinding();

  const [search, setSearch] =
    useState("");

  const [severity, setSeverity] =
    useState("");

  const [status, setStatus] =
    useState("");

  const [auditId, setAuditId] =
    useState("");

  const filteredFindings = useMemo(() => {

    return findings.filter((finding) => {

      const searchValue =
        search.toLowerCase().trim();

      const matchesSearch =
        searchValue === "" ||
        finding.title
          .toLowerCase()
          .includes(searchValue) ||
        finding.description
          .toLowerCase()
          .includes(searchValue) ||
        finding.audit_name
          .toLowerCase()
          .includes(searchValue) ||
        finding.control_name
          .toLowerCase()
          .includes(searchValue);

      const matchesSeverity =
        severity === "" ||
        finding.severity === severity;

      const matchesStatus =
        status === "" ||
        finding.status === status;

      const matchesAudit =
        auditId === "" ||
        finding.audit_id === Number(auditId);

      return (
        matchesSearch &&
        matchesSeverity &&
        matchesStatus &&
        matchesAudit
      );

    });

  }, [
    findings,
    search,
    severity,
    status,
    auditId,
  ]);

  async function handleDelete(
    id: number
  ) {
    const confirmed =
      window.confirm(
        "Are you sure you want to delete this audit finding?"
      );

    if (!confirmed) {
      return;
    }

    try {

      await deleteMutation.mutateAsync(
        id
      );

    } catch {

      window.alert(
        "Failed to delete audit finding."
      );

    }
  }

  if (
    findingsLoading ||
    auditsLoading
  ) {
    return (
      <AppLayout>

        <div className="space-y-6">

          <div>
            <div className="h-8 w-64 animate-pulse rounded bg-slate-200" />

            <div className="mt-2 h-4 w-48 animate-pulse rounded bg-slate-100" />
          </div>

          <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">

            {Array.from({
              length: 5,
            }).map((_, index) => (
              <div
                key={index}
                className="h-28 animate-pulse rounded-xl bg-slate-100"
              />
            ))}

          </div>

          <div className="h-24 animate-pulse rounded-xl bg-slate-100" />

          <div className="h-64 animate-pulse rounded-xl bg-slate-100" />

        </div>

      </AppLayout>
    );
  }

  if (findingsError) {
    return (
      <AppLayout>

        <div className="rounded-xl border border-red-200 bg-red-50 p-6">

          <h2 className="font-semibold text-red-700">
            Failed to load audit findings
          </h2>

          <p className="mt-1 text-sm text-red-600">
            Please refresh the page and try again.
          </p>

        </div>

      </AppLayout>
    );
  }

  return (
    <AppLayout>

      <div className="space-y-6">

        {/* Header */}
        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

          <div>

            <h1 className="text-3xl font-bold text-slate-900">
              Audit Findings
            </h1>

            <p className="mt-1 text-slate-500">
              Identify, track and manage issues discovered during audits.
            </p>

          </div>

          <div className="text-sm text-slate-500">

            Showing{" "}
            <span className="font-semibold text-slate-700">
              {filteredFindings.length}
            </span>{" "}
            of{" "}
            <span className="font-semibold text-slate-700">
              {findings.length}
            </span>{" "}
            findings

          </div>

        </div>

        {/* Stats */}
        <AuditFindingStats
          findings={findings}
        />

        {/* Filters */}
        <AuditFindingFilters
          search={search}
          severity={severity}
          status={status}
          auditId={auditId}
          audits={audits}
          onSearchChange={setSearch}
          onSeverityChange={setSeverity}
          onStatusChange={setStatus}
          onAuditChange={setAuditId}
          onCreate={() =>
            navigate("/audit-findings/new")
          }
        />

        {/* Table */}
        <AuditFindingTable
          findings={filteredFindings}
          onView={(id) =>
            navigate(
              `/audit-findings/${id}`
            )
          }
          onEdit={(id) =>
            navigate(
              `/audit-findings/${id}/edit`
            )
          }
          onDelete={handleDelete}
        />

      </div>

    </AppLayout>
  );
}