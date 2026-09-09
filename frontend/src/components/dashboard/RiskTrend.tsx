import DashboardCard from "./DashboardCard";

import {
  TrendingUp,
} from "lucide-react";

import {
  useRiskTrend,
} from "@/hooks/useRiskTrend";

import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
} from "recharts";


export default function RiskTrend() {

  const {
    data,
    isLoading,
    error,
  } = useRiskTrend();


  if (isLoading) {

    return (
      <DashboardCard
        title="Risk Trend"
        subtitle="Risks created over the last 6 months"
        icon={
          <TrendingUp
            size={24}
            className="text-blue-600"
          />
        }
      >

        <p className="text-slate-500">
          Loading chart...
        </p>

      </DashboardCard>
    );
  }


  if (error || !data) {

    return (
      <DashboardCard
        title="Risk Trend"
        subtitle="Risks created over the last 6 months"
        icon={
          <TrendingUp
            size={24}
            className="text-blue-600"
          />
        }
      >

        <p className="text-red-500">
          Failed to load chart.
        </p>

      </DashboardCard>
    );
  }


  return (
    <DashboardCard
      title="Risk Trend"
      subtitle="Risks created over the last 6 months"
      icon={
        <TrendingUp
          size={24}
          className="text-blue-600"
        />
      }
    >

      <div className="h-72">

        <ResponsiveContainer
          width="100%"
          height="100%"
        >

          <LineChart
            data={data}
          >

            <CartesianGrid
              strokeDasharray="3 3"
            />

            <XAxis
              dataKey="month"
            />

            <YAxis
              allowDecimals={false}
            />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="risks"
              stroke="#2563eb"
              strokeWidth={3}
              dot={{ r: 5 }}
              activeDot={{ r: 8 }}
              animationDuration={1200}
            />

          </LineChart>

        </ResponsiveContainer>

      </div>

    </DashboardCard>
  );
}