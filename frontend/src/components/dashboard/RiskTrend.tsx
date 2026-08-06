import DashboardCard from "./DashboardCard";
import { TrendingUp } from "lucide-react";

import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  Tooltip,
  ResponsiveContainer,
  CartesianGrid,
} from "recharts";

const data = [
  { month: "Jan", risks: 6 },
  { month: "Feb", risks: 8 },
  { month: "Mar", risks: 7 },
  { month: "Apr", risks: 5 },
  { month: "May", risks: 4 },
  { month: "Jun", risks: 3 },
];

export default function RiskTrend() {
  return (
    <DashboardCard
      title="Risk Trend"
      subtitle="Open risks over the last 6 months"
      icon={<TrendingUp size={24} className="text-blue-600" />}
    >
      <div className="h-64">

        <ResponsiveContainer width="100%" height="100%">

          <LineChart data={data}>

            <CartesianGrid strokeDasharray="3 3" />

            <XAxis dataKey="month" />

            <YAxis />

            <Tooltip />

            <Line
              type="monotone"
              dataKey="risks"
              stroke="#2563eb"
              strokeWidth={3}
              dot={{ r: 5 }}
            />

          </LineChart>

        </ResponsiveContainer>

      </div>
    </DashboardCard>
  );
}