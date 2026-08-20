import {
  AlertTriangle,
  CircleAlert,
  CircleCheck,
  FileWarning,
  ShieldAlert,
} from "lucide-react";

import type { AuditFinding } from "@/api/auditFindings";

interface Props {
  findings: AuditFinding[];
}

export default function AuditFindingStats({
  findings,
}: Props) {
  const total = findings.length;

  const critical = findings.filter(
    (finding) => finding.severity === "Critical"
  ).length;

  const high = findings.filter(
    (finding) => finding.severity === "High"
  ).length;

  const medium = findings.filter(
    (finding) => finding.severity === "Medium"
  ).length;

  const low = findings.filter(
    (finding) => finding.severity === "Low"
  ).length;

  const open = findings.filter(
    (finding) => finding.status === "Open"
  ).length;

  const inProgress = findings.filter(
    (finding) => finding.status === "In Progress"
  ).length;

  const closed = findings.filter(
    (finding) => finding.status === "Closed"
  ).length;

  const severityData = [
    {
      label: "Critical",
      value: critical,
      color: "bg-red-500",
      text: "text-red-700",
    },
    {
      label: "High",
      value: high,
      color: "bg-orange-500",
      text: "text-orange-700",
    },
    {
      label: "Medium",
      value: medium,
      color: "bg-yellow-500",
      text: "text-yellow-700",
    },
    {
      label: "Low",
      value: low,
      color: "bg-green-500",
      text: "text-green-700",
    },
  ];

  const cards = [
    {
      label: "Total Findings",
      value: total,
      icon: FileWarning,
      iconBg: "bg-slate-100",
      iconColor: "text-slate-700",
    },
    {
      label: "Critical",
      value: critical,
      icon: ShieldAlert,
      iconBg: "bg-red-100",
      iconColor: "text-red-600",
    },
    {
      label: "High",
      value: high,
      icon: AlertTriangle,
      iconBg: "bg-orange-100",
      iconColor: "text-orange-600",
    },
    {
      label: "Medium",
      value: medium,
      icon: CircleAlert,
      iconBg: "bg-yellow-100",
      iconColor: "text-yellow-600",
    },
    {
      label: "Low",
      value: low,
      icon: CircleCheck,
      iconBg: "bg-green-100",
      iconColor: "text-green-600",
    },
  ];

  return (
    <div className="space-y-6">

      {/* Statistics Cards */}
      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">

        {cards.map((card) => {
          const Icon = card.icon;

          return (
            <div
              key={card.label}
              className="rounded-xl border bg-white p-5 shadow-sm transition hover:shadow-md"
            >
              <div className="flex items-center justify-between">

                <div>
                  <p className="text-sm font-medium text-slate-500">
                    {card.label}
                  </p>

                  <p className="mt-2 text-3xl font-bold text-slate-900">
                    {card.value}
                  </p>
                </div>

                <div
                  className={`rounded-xl p-3 ${card.iconBg}`}
                >
                  <Icon
                    size={22}
                    className={card.iconColor}
                  />
                </div>

              </div>
            </div>
          );
        })}

      </div>

      {/* Severity Overview */}
      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <div className="mb-5 flex items-center justify-between">

          <div>
            <h2 className="text-lg font-semibold text-slate-900">
              Severity Overview
            </h2>

            <p className="text-sm text-slate-500">
              Distribution of audit findings by severity
            </p>
          </div>

          <div className="text-sm text-slate-500">
            {total} total
          </div>

        </div>

        <div className="space-y-4">

          {severityData.map((item) => {

            const percentage =
              total === 0
                ? 0
                : Math.round(
                    (item.value / total) * 100
                  );

            return (
              <div key={item.label}>

                <div className="mb-1 flex items-center justify-between text-sm">

                  <span
                    className={`font-medium ${item.text}`}
                  >
                    {item.label}
                  </span>

                  <span className="text-slate-500">
                    {item.value}{" "}
                    ({percentage}%)
                  </span>

                </div>

                <div className="h-2 overflow-hidden rounded-full bg-slate-100">

                  <div
                    className={`h-full rounded-full ${item.color} transition-all`}
                    style={{
                      width: `${percentage}%`,
                    }}
                  />

                </div>

              </div>
            );

          })}

        </div>

        {/* Status Summary */}
        <div className="mt-6 grid grid-cols-3 gap-3 border-t pt-5">

          <div className="rounded-lg bg-blue-50 p-3 text-center">
            <p className="text-xs font-medium text-blue-600">
              Open
            </p>

            <p className="mt-1 text-xl font-bold text-blue-700">
              {open}
            </p>
          </div>

          <div className="rounded-lg bg-yellow-50 p-3 text-center">
            <p className="text-xs font-medium text-yellow-600">
              In Progress
            </p>

            <p className="mt-1 text-xl font-bold text-yellow-700">
              {inProgress}
            </p>
          </div>

          <div className="rounded-lg bg-green-50 p-3 text-center">
            <p className="text-xs font-medium text-green-600">
              Closed
            </p>

            <p className="mt-1 text-xl font-bold text-green-700">
              {closed}
            </p>
          </div>

        </div>

      </div>

    </div>
  );
}