import type { Risk } from "@/api/risks";

import {
  ResponsiveContainer,
  BarChart,
  Bar,
  XAxis,
  YAxis,
  Tooltip,
  CartesianGrid,
} from "recharts";

interface Props {
  risks: Risk[];
}

export default function RiskSeverityChart({
  risks,
}: Props) {

  const data = [
    {
      name: "Low",
      value: risks.filter(
        (risk) => risk.risk_score <= 5
      ).length,
    },
    {
      name: "Medium",
      value: risks.filter(
        (risk) =>
          risk.risk_score > 5 &&
          risk.risk_score <= 10
      ).length,
    },
    {
      name: "High",
      value: risks.filter(
        (risk) =>
          risk.risk_score > 10 &&
          risk.risk_score < 15
      ).length,
    },
    {
      name: "Critical",
      value: risks.filter(
        (risk) => risk.risk_score >= 15
      ).length,
    },
  ];

  return (

    <div className="rounded-2xl border bg-white p-6 shadow-sm">

      <h2 className="mb-6 text-lg font-semibold">
        Risk Severity Distribution
      </h2>

      <div className="h-80">

        <ResponsiveContainer
          width="100%"
          height="100%"
        >

          <BarChart data={data}>

            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey="name" />

            <YAxis />

            <Tooltip />

            <Bar
                dataKey="value"
                fill="#2563eb"
                radius={[8, 8, 0, 0]}
            />

          </BarChart>

        </ResponsiveContainer>

      </div>

    </div>

  );

}