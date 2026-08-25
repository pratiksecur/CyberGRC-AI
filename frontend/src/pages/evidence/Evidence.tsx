import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useEvidence } from "@/hooks/useEvidence";
import { useDeleteEvidence } from "@/hooks/useDeleteEvidence";

import EvidenceStats from "@/components/evidence/EvidenceStats";
import EvidenceFilters from "@/components/evidence/EvidenceFilters";
import EvidenceCards from "@/components/evidence/EvidenceCards";
import RecentEvidence from "@/components/evidence/RecentEvidence";
import EvidenceTable from "@/components/evidence/EvidenceTable";

export default function Evidence() {
  const navigate = useNavigate();

  const deleteMutation = useDeleteEvidence();

  const {
    data,
    isLoading,
    error,
  } = useEvidence();

  const [search, setSearch] = useState("");

  const filteredEvidence = useMemo(() => {
    if (!data) return [];

    return data.filter((evidence) => {
      return (
        evidence.title
          .toLowerCase()
          .includes(search.toLowerCase()) ||
        evidence.description
          .toLowerCase()
          .includes(search.toLowerCase()) ||
        evidence.file_name
          .toLowerCase()
          .includes(search.toLowerCase())
      );
    });
  }, [data, search]);

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading Evidence...
        </div>
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Failed to load evidence.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="space-y-6">

        {/* Header */}

        <div>
          <h1 className="text-3xl font-bold">
            Evidence Management
          </h1>

          <p className="text-slate-500">
            Manage cybersecurity evidence.
          </p>
        </div>

        {/* Filters */}

        <EvidenceFilters
          search={search}
          onSearchChange={setSearch}
          onCreate={() =>
            navigate("/evidence/new")
          }
        />

        {/* Statistics */}

        <EvidenceStats
          totalEvidence={filteredEvidence.length}
          totalFiles={filteredEvidence.length}
        />

        {/* Evidence Overview */}

        <div className="grid gap-6 lg:grid-cols-2">

          <EvidenceCards
            evidence={filteredEvidence}
          />

        </div>

        {/* Recent Evidence */}

        <RecentEvidence
          evidence={filteredEvidence}
        />

        {/* Evidence Table */}

        <EvidenceTable
          evidence={filteredEvidence}
          onEdit={(id) =>
            navigate(`/evidence/${id}/edit`)
          }
          onDelete={async (id) => {
            if (
              !confirm(
                "Delete this evidence?"
              )
            ) {
              return;
            }

            try {
              await deleteMutation.mutateAsync(id);
            } catch {
              alert(
                "Failed to delete evidence."
              );
            }
          }}
        />

      </div>
    </AppLayout>
  );
}