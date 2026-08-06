import DashboardCard from "./DashboardCard";
import { ShieldCheck } from "lucide-react";

interface Props {
  score: number;
}

export default function SecurityHealth({ score }: Props) {
  const getStatus = () => {
    if (score >= 90)
      return {
        bg: "bg-emerald-500",
        text: "Excellent",
        color: "text-emerald-600",
      };

    if (score >= 75)
      return {
        bg: "bg-blue-500",
        text: "Good",
        color: "text-blue-600",
      };

    if (score >= 50)
      return {
        bg: "bg-amber-500",
        text: "Needs Attention",
        color: "text-amber-600",
      };

    return {
      bg: "bg-red-500",
      text: "Critical",
      color: "text-red-600",
    };
  };

  const status = getStatus();

  return (
    <DashboardCard
      title="Security Health"
      subtitle="Overall Cybersecurity Score"
      icon={<ShieldCheck size={24} className="text-emerald-600" />}
    >
      <div className="space-y-6">

        <div className="text-center">

          <h1 className="text-6xl font-bold text-slate-900">
            {score}
          </h1>

          <p className="text-slate-500">
            out of 100
          </p>

        </div>

        <div className="h-4 w-full rounded-full bg-slate-200">

          <div
            className={`h-4 rounded-full transition-all duration-500 ${status.bg}`}
            style={{ width: `${score}%` }}
          />

        </div>

        <div className="text-center">

          <span
            className={`text-lg font-semibold ${status.color}`}
          >
            {status.text}
          </span>

        </div>

        <div className="grid grid-cols-2 gap-4 text-center">

          <div>

            <p className="text-2xl font-bold text-emerald-600">
              42
            </p>

            <p className="text-sm text-slate-500">
              Active Controls
            </p>

          </div>

          <div>

            <p className="text-2xl font-bold text-red-600">
              3
            </p>

            <p className="text-sm text-slate-500">
              Critical Risks
            </p>

          </div>

        </div>

      </div>
    </DashboardCard>
  );
}