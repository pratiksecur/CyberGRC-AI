import {
  PieChart,
  Pie,
  Cell,
  ResponsiveContainer,
  Tooltip,
} from "recharts";

interface Props {
  planned: number;
  inProgress: number;
  completed: number;
}

export default function AuditStatusChart({
  planned,
  inProgress,
  completed,
}: Props) {
  const data = [
    {
      name: "Planned",
      value: planned,
    },
    {
      name: "In Progress",
      value: inProgress,
    },
    {
      name: "Completed",
      value: completed,
    },
  ];

  const colors = [
    "#3B82F6",
    "#F59E0B",
    "#22C55E",
  ];

  return (
    <div className="rounded-2xl border bg-white p-6">

      <h2 className="mb-4 text-lg font-semibold">
        Audit Status
      </h2>

      <ResponsiveContainer
        width="100%"
        height={300}
      >
        <PieChart>

          <Pie
            data={data}
            dataKey="value"
            outerRadius={100}
            label
          >

            {data.map((_, index) => (
              <Cell
                key={index}
                fill={colors[index]}
              />
            ))}

          </Pie>

          <Tooltip />

        </PieChart>
      </ResponsiveContainer>

    </div>
  );
}