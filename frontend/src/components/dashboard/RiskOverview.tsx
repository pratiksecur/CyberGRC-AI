import StatCard from "./StatCard";

import {
  ShieldAlert,
  ShieldCheck,
  TriangleAlert,
  BarChart3,
} from "lucide-react";

import type { Risk } from "@/api/risks";

interface Props {
  risks: Risk[];
}

export default function RiskOverview({
  risks,
}: Props) {

  const total = risks.length;

  const open = risks.filter(
    (risk) => risk.status === "Open"
  ).length;

  const critical = risks.filter(
    (risk) => risk.risk_score >= 15
  ).length;

  const average =
    total > 0
      ? (
          risks.reduce(
            (sum, risk) => sum + risk.risk_score,
            0
          ) / total
        ).toFixed(1)
      : "0";

  return (

    <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">

      <StatCard
        title="Total Risks"
        value={total}
        subtitle="All registered risks"
        icon={ShieldCheck}
        iconColor="bg-blue-600"
      />

      <StatCard
        title="Open Risks"
        value={open}
        subtitle="Require attention"
        icon={ShieldAlert}
        iconColor="bg-amber-500"
      />

      <StatCard
        title="Critical Risks"
        value={critical}
        subtitle="Score ≥ 15"
        icon={TriangleAlert}
        iconColor="bg-red-600"
      />

      <StatCard
        title="Average Score"
        value={average}
        subtitle="Overall risk level"
        icon={BarChart3}
        iconColor="bg-emerald-600"
      />

    </div>

  );

}