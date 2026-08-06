import DashboardCard from "./DashboardCard";
import {
  Activity,
  ShieldAlert,
  ShieldCheck,
  ClipboardList,
  FileText,
} from "lucide-react";

import { useActivity } from "@/hooks/useActivity";

const iconMap = {
  risk: ShieldAlert,
  control: ShieldCheck,
  audit: ClipboardList,
  evidence: FileText,
};

const colorMap = {
  risk: "text-red-500",
  control: "text-emerald-500",
  audit: "text-blue-500",
  evidence: "text-amber-500",
};

export default function RecentActivity() {

  const { data, isLoading, error } = useActivity();

  if (isLoading) {
    return (
      <DashboardCard
        title="Recent Activity"
        subtitle="Latest cybersecurity events"
        icon={<Activity size={24} className="text-blue-600" />}
      >
        <p className="text-slate-500">
          Loading activity...
        </p>
      </DashboardCard>
    );
  }

  if (error || !data) {
    return (
      <DashboardCard
        title="Recent Activity"
        subtitle="Latest cybersecurity events"
        icon={<Activity size={24} className="text-blue-600" />}
      >
        <p className="text-red-500">
          Failed to load activity.
        </p>
      </DashboardCard>
    );
  }

  return (
    <DashboardCard
      title="Recent Activity"
      subtitle="Latest cybersecurity events"
      icon={<Activity size={24} className="text-blue-600" />}
    >
      <div className="divide-y">

        {data.map((activity, index) => {

          const Icon =
            iconMap[
              activity.type as keyof typeof iconMap
            ] ?? Activity;

          const color =
            colorMap[
              activity.type as keyof typeof colorMap
            ] ?? "text-slate-500";

          return (
            <div
              key={index}
              className="flex items-start gap-4 py-4 first:pt-0 last:pb-0 transition-colors hover:bg-slate-50"
            >

              <div
                className={`rounded-xl bg-slate-100 p-3 ${color}`}
              >
                <Icon size={20} />
              </div>

              <div className="flex-1">

                <h3 className="font-semibold">
                  {activity.title}
                </h3>

                <p className="text-sm text-slate-500">
                  {activity.description}
                </p>

              </div>

              <span className="text-xs whitespace-nowrap text-slate-400">
                {new Date(activity.time).toLocaleDateString()}
              </span>

            </div>
          );

        })}

      </div>
    </DashboardCard>
  );
}