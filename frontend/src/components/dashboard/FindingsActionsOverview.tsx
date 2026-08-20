import {
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  ClipboardCheck,
  ListChecks,
  Clock3,
} from "lucide-react";

interface Props {
  totalFindings: number;
  openFindings: number;
  criticalFindings: number;

  totalActions: number;
  pendingActions: number;
  overdueActions: number;
}

export default function FindingsActionsOverview({
  totalFindings,
  openFindings,
  criticalFindings,
  totalActions,
  pendingActions,
  overdueActions,
}: Props) {
  const stats = [
    {
      title: "Total Findings",
      value: totalFindings,
      subtitle: "Audit findings",
      icon: ClipboardCheck,
      iconBg: "bg-blue-100",
      iconColor: "text-blue-600",
    },
    {
      title: "Open Findings",
      value: openFindings,
      subtitle: "Require attention",
      icon: AlertCircle,
      iconBg: "bg-amber-100",
      iconColor: "text-amber-600",
    },
    {
      title: "Critical Findings",
      value: criticalFindings,
      subtitle: "High priority issues",
      icon: AlertTriangle,
      iconBg: "bg-red-100",
      iconColor: "text-red-600",
    },
    {
      title: "Total Actions",
      value: totalActions,
      subtitle: "Remediation actions",
      icon: ListChecks,
      iconBg: "bg-emerald-100",
      iconColor: "text-emerald-600",
    },
    {
      title: "Pending Actions",
      value: pendingActions,
      subtitle: "Awaiting completion",
      icon: Clock3,
      iconBg: "bg-orange-100",
      iconColor: "text-orange-600",
    },
    {
      title: "Overdue Actions",
      value: overdueActions,
      subtitle: "Past due date",
      icon: CheckCircle2,
      iconBg: "bg-purple-100",
      iconColor: "text-purple-600",
    },
  ];

  return (
    <div className="space-y-4">

      <div>
        <h2 className="text-xl font-semibold text-slate-900">
          Findings & Remediation
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Current audit findings and corrective action status.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">

        {stats.map((stat) => {
          const Icon = stat.icon;

          return (
            <div
              key={stat.title}
              className="rounded-2xl border bg-white p-5 shadow-sm transition-shadow hover:shadow-md"
            >

              <div className="flex items-start justify-between">

                <div>

                  <p className="text-sm font-medium text-slate-500">
                    {stat.title}
                  </p>

                  <p className="mt-2 text-3xl font-bold text-slate-900">
                    {stat.value}
                  </p>

                  <p className="mt-1 text-xs text-slate-500">
                    {stat.subtitle}
                  </p>

                </div>

                <div
                  className={`flex h-11 w-11 items-center justify-center rounded-xl ${stat.iconBg}`}
                >
                  <Icon
                    className={`h-5 w-5 ${stat.iconColor}`}
                  />
                </div>

              </div>

            </div>
          );
        })}

      </div>

    </div>
  );
}