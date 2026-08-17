import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface Props {
  latest: number;
  older: number;
}

const COLORS = ["#2563eb", "#f59e0b"];

export default function FrameworkVersionChart({
  latest,
  older,
}: Props) {
  const data = [
    {
      name: "Latest",
      value: latest,
    },
    {
      name: "Older",
      value: older,
    },
  ];

  return (
    <div className="rounded-2xl border bg-white p-6">

      <h2 className="mb-6 text-lg font-semibold">
        Framework Versions
      </h2>

      <div className="h-72">

        <ResponsiveContainer width="100%" height="100%">

          <PieChart>

            <Pie
              data={data}
              dataKey="value"
              outerRadius={90}
              label
            >
              {data.map((_, index) => (
                <Cell
                  key={index}
                  fill={COLORS[index]}
                />
              ))}
            </Pie>

            <Tooltip />

          </PieChart>

        </ResponsiveContainer>

      </div>

    </div>
  );
}