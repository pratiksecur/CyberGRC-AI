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
            trend="+2 this week"
            trendPositive={true}
            icon={ShieldCheck}
            iconColor="bg-blue-600"
        />

        <StatCard
            title="Open Risks"
            value={open}
            subtitle="Require attention"
            trend="+1 today"
            trendPositive={true}
            icon={ShieldAlert}
            iconColor="bg-amber-500"
        />

        <StatCard
            title="Critical Risks"
            value={critical}
            subtitle="Score ≥ 15"
            trend="-1 today"
            trendPositive={false}
            icon={TriangleAlert}
            iconColor="bg-red-600"
        />

        <StatCard
            title="Average Score"
            value={average}
            subtitle="Overall risk level"
            trend="+0.8"
            trendPositive={true}
            icon={BarChart3}
            iconColor="bg-emerald-600"
        />

    </div>

  );

}