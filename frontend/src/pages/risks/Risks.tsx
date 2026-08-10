import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import RiskTable from "@/components/risks/RiskTable";
import RiskFilters from "@/components/risks/RiskFilters";

import { useRisks } from "@/hooks/useRisks";

import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

import RiskOverview from "@/components/dashboard/RiskOverview";
import RiskSeverityChart from "@/components/dashboard/RiskSeverityChart";
import RiskStatusChart from "@/components/dashboard/RiskStatusChart";
import RecentRisks from "@/components/dashboard/RecentRisks";
import HighestRisk from "@/components/dashboard/HighestRisk";
import DashboardSkeleton from "@/components/dashboard/DashboardSkeleton";

export default function Risks() {

  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
  } = useRisks();

  const [search, setSearch] = useState("");
  const [status, setStatus] = useState("");
  const [sort, setSort] = useState("");

  const filteredRisks = useMemo(() => {

    if (!data) return [];

    let risks = [...data];

    // Search

    if (search) {

      const query = search.toLowerCase();

      risks = risks.filter((risk) =>
        risk.title.toLowerCase().includes(query) ||
        risk.description.toLowerCase().includes(query)
      );

    }

    // Status

    if (status) {

      risks = risks.filter(
        (risk) => risk.status === status
      );

    }

    // Sort

    if (sort === "high") {

      risks.sort(
        (a, b) => b.risk_score - a.risk_score
      );

    }

    if (sort === "low") {

      risks.sort(
        (a, b) => a.risk_score - b.risk_score
      );

    }

    return risks;

  }, [data, search, status, sort]);

  if (isLoading) {
    return (
      <AppLayout>
        <DashboardSkeleton />
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="p-10 text-center text-red-500">
          Failed to load risks.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>

      <div className="space-y-6">

        <div className="flex items-center justify-between">

          <div>

            <h1 className="text-3xl font-bold">
              Risk Management
            </h1>

            <p className="text-slate-500">
              View and manage cybersecurity risks.
            </p>

          </div>

          <Button
            onClick={() => navigate("/risks/new")}
          >
            <Plus className="mr-2 h-4 w-4" />
            New Risk
          </Button>

        </div>

        <RiskFilters
          search={search}
          onSearchChange={setSearch}
          status={status}
          onStatusChange={setStatus}
          sort={sort}
          onSortChange={setSort}
        />

        <RiskOverview risks={filteredRisks} />

          <div className="grid gap-6 lg:grid-cols-2">

            <RiskSeverityChart
              risks={filteredRisks}
            />

            <RiskStatusChart
              risks={filteredRisks}
            />

          </div>

          <div className="grid gap-6 lg:grid-cols-2">

            <RecentRisks
              risks={filteredRisks}
            />

            <HighestRisk
              risks={filteredRisks}
            />

          </div>

        <RiskTable
          risks={filteredRisks}
        />

      </div>

    </AppLayout>
  );
}