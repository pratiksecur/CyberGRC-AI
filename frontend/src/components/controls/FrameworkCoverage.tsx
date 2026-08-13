import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface Props {
  data: {
    framework: string;
    count: number;
  }[];
}

export default function FrameworkCoverage({
  data,
}: Props) {
  return (
    <div className="rounded-2xl border bg-white p-6 shadow-sm">

      <h2 className="mb-4 text-lg font-semibold">
        Framework Coverage
      </h2>

      <div className="h-72">

        <ResponsiveContainer width="100%" height="100%">

          <BarChart data={data}>

            <XAxis dataKey="framework" />

            <YAxis />

            <Tooltip />

            <Bar
              dataKey="count"
              fill="#2563EB"
              radius={[6, 6, 0, 0]}
            />

          </BarChart>

        </ResponsiveContainer>

      </div>

    </div>
  );
}