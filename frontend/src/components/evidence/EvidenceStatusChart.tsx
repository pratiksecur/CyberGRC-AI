import {
  PieChart,
  Pie,
  Cell,
  Tooltip,
  ResponsiveContainer,
} from "recharts";

interface Props {
  approved: number;
  pending: number;
}

const COLORS = [
  "#16a34a",
  "#f59e0b",
];

export default function EvidenceStatusChart({
  approved,
  pending,
}: Props) {
  const data = [
    {
      name: "Approved",
      value: approved,
    },
    {
      name: "Pending",
      value: pending,
    },
  ];

  return (
    <div className="rounded-2xl border bg-white p-6">

      <h2 className="mb-6 text-lg font-semibold">
        Evidence Status
      </h2>

      <div className="h-72">

        <ResponsiveContainer>

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