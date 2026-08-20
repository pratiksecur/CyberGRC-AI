import {
  ClipboardCheck,
  CircleCheck,
  Clock3,
  AlertTriangle,
} from "lucide-react";

import type { CorrectiveAction } from "@/api/correctiveActions";

interface Props {
  actions: CorrectiveAction[];
}

export default function CorrectiveActionOverview({
  actions,
}: Props) {
  const total = actions.length;

  const open = actions.filter(
    (action) => action.status === "Open"
  ).length;

  const inProgress = actions.filter(
    (action) => action.status === "In Progress"
  ).length;

  const completed = actions.filter(
    (action) =>
      action.status === "Completed" ||
      action.status === "Closed"
  ).length;

  const overdue = actions.filter((action) => {
    if (!action.due_date) return false;

    if (
      action.status === "Completed" ||
      action.status === "Closed"
    ) {
      return false;
    }

    return (
      new Date(action.due_date) <
      new Date()
    );
  }).length;

  const stats = [
    {
      label: "Total Actions",
      value: total,
      icon: ClipboardCheck,
      iconClass:
        "bg-slate-100 text-slate-600",
    },
    {
      label: "Open",
      value: open,
      icon: Clock3,
      iconClass:
        "bg-blue-100 text-blue-600",
    },
    {
      label: "In Progress",
      value: inProgress,
      icon: AlertTriangle,
      iconClass:
        "bg-yellow-100 text-yellow-600",
    },
    {
      label: "Completed",
      value: completed,
      icon: CircleCheck,
      iconClass:
        "bg-green-100 text-green-600",
    },
    {
      label: "Overdue",
      value: overdue,
      icon: AlertTriangle,
      iconClass:
        "bg-red-100 text-red-600",
    },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-5">
      {stats.map((stat) => {
        const Icon = stat.icon;

        return (
          <div
            key={stat.label}
            className="rounded-xl border bg-white p-5 shadow-sm"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm font-medium text-slate-500">
                  {stat.label}
                </p>

                <h2 className="mt-2 text-3xl font-bold text-slate-900">
                  {stat.value}
                </h2>
              </div>

              <div
                className={`flex h-10 w-10 items-center justify-center rounded-lg ${stat.iconClass}`}
              >
                <Icon size={20} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}