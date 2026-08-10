import AppLayout from "@/layouts/AppLayout";

import RiskTable from "@/components/risks/RiskTable";

import { useRisks } from "@/hooks/useRisks";

import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";
import { useNavigate } from "react-router-dom";

export default function Risks() {

  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
  } = useRisks();

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10 text-center">
          Loading Risks...
        </div>
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

        {/* Header */}

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

        {/* Risk Table */}

        <RiskTable risks={data} />

      </div>

    </AppLayout>
  );
}