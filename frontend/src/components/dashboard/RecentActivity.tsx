import DashboardCard from "./DashboardCard";
import {
  Activity,
  ShieldAlert,
  ShieldCheck,
  ClipboardList,
  FileText,
} from "lucide-react";

const activities = [
  {
    icon: ShieldAlert,
    title: "High Risk Created",
    description: "SQL Injection Vulnerability",
    time: "2 hours ago",
    color: "text-red-500",
  },
  {
    icon: ShieldCheck,
    title: "Control Implemented",
    description: "Multi-Factor Authentication",
    time: "5 hours ago",
    color: "text-emerald-500",
  },
  {
    icon: ClipboardList,
    title: "Audit Started",
    description: "ISO 27001 Internal Audit",
    time: "Yesterday",
    color: "text-blue-500",
  },
  {
    icon: FileText,
    title: "Evidence Uploaded",
    description: "Firewall Configuration.pdf",
    time: "2 days ago",
    color: "text-amber-500",
  },
];

export default function RecentActivity() {
  return (
    <DashboardCard
      title="Recent Activity"
      subtitle="Latest cybersecurity events"
      icon={<Activity size={24} className="text-blue-600" />}
    >
      <div className="divide-y">

        {activities.map((activity) => {
          const Icon = activity.icon;

          return (
            <div
              key={activity.title}
              className="flex items-start gap-4 py-4 first:pt-0 last:pb-0 transition-colors hover:bg-slate-50"
            >
              <div
                className={`rounded-xl bg-slate-100 p-3 ${activity.color}`}
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
                {activity.time}
              </span>

            </div>
          );
        })}

      </div>
    </DashboardCard>
  );
}