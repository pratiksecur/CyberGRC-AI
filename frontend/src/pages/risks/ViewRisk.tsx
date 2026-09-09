import { useNavigate, useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { Button } from "@/components/ui/button";
import {
  ArrowLeft,
  Pencil,
} from "lucide-react";

import { useRisk } from "@/hooks/useRisk";

import Can from "@/components/auth/Can";

import RiskScoreBadge from "@/components/risks/RiskScoreBadge";
import RiskStatusBadge from "@/components/risks/RiskStatusBadge";

export default function ViewRisk() {
  const navigate = useNavigate();

  const { id } = useParams();

  const {
    data,
    isLoading,
    error,
  } = useRisk(Number(id));

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10 text-center">
          Loading Risk...
        </div>
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Risk not found.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>

      <div className="mx-auto max-w-5xl space-y-6">

        {/* Header */}

        <div className="flex items-center justify-between">

          <div>

            <h1 className="text-3xl font-bold">
              {data.title}
            </h1>

            <p className="mt-2 text-slate-500">
              Risk Details
            </p>

          </div>

          <div className="flex gap-3">

            {/* Back */}

            <Button
              variant="outline"
              onClick={() => navigate("/risks")}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>

            {/* Edit */}

            <Can resource="risks" action="update">
              <Button
                onClick={() =>
                  navigate(`/risks/${data.id}/edit`)
                }
              >
                <Pencil className="mr-2 h-4 w-4" />
                Edit Risk
              </Button>
            </Can>

          </div>

        </div>

        {/* Description */}

        <div className="rounded-xl border bg-white p-6 shadow-sm">

          <h2 className="mb-3 text-lg font-semibold">
            Description
          </h2>

          <p className="leading-7 text-slate-600">
            {data.description}
          </p>

        </div>

        {/* Details */}

        <div className="grid gap-6 md:grid-cols-2">

          <div className="rounded-xl border bg-white p-6 shadow-sm">

            <h2 className="mb-5 text-lg font-semibold">
              Risk Information
            </h2>

            <div className="space-y-4">

              <div className="flex justify-between">
                <span className="text-slate-500">
                  Likelihood
                </span>

                <span>
                  {data.likelihood}
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-500">
                  Impact
                </span>

                <span>
                  {data.impact}
                </span>
              </div>

              <div className="flex justify-between">
                <span className="text-slate-500">
                  Owner
                </span>

                <span>
                  User #{data.owner_id}
                </span>
              </div>

            </div>

          </div>

          <div className="rounded-xl border bg-white p-6 shadow-sm">

            <h2 className="mb-5 text-lg font-semibold">
              Assessment
            </h2>

            <div className="space-y-4">

              <div className="flex justify-between">

                <span className="text-slate-500">
                  Risk Score
                </span>

                <RiskScoreBadge
                  score={data.risk_score}
                />

              </div>

              <div className="flex justify-between">

                <span className="text-slate-500">
                  Status
                </span>

                <RiskStatusBadge
                  status={data.status}
                />

              </div>

              <div className="flex justify-between">

                <span className="text-slate-500">
                  Created
                </span>

                <span>
                  {new Date(
                    data.created_at
                  ).toLocaleDateString()}
                </span>

              </div>

              <div className="flex justify-between">

                <span className="text-slate-500">
                  Updated
                </span>

                <span>
                  {new Date(
                    data.updated_at
                  ).toLocaleDateString()}
                </span>

              </div>

            </div>

          </div>

        </div>

      </div>

    </AppLayout>
  );
}