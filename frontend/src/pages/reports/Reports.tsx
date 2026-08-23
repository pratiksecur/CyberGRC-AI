import {
  BarChart3,
  ClipboardCheck,
  FileCheck2,
  ShieldAlert,
  ListChecks,
  ArrowRight,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

export default function Reports() {
  const navigate = useNavigate();

  const reports = [
    {
      title: "Risk Report",
      description:
        "Review organizational risks, severity distribution, risk scores, and ownership.",
      icon: ShieldAlert,
      color: "red",
      path: "/reports/risks",
    },

    {
      title: "Audit Report",
      description:
        "Review audit status, findings, severity distribution, and audit performance.",
      icon: ClipboardCheck,
      color: "blue",
      path: "/reports/audits",
    },

    {
      title: "Compliance Report",
      description:
        "Review framework coverage, controls, effectiveness, evidence, and findings.",
      icon: FileCheck2,
      color: "green",
      path: "/reports/compliance",
    },

    {
      title: "Corrective Actions Report",
      description:
        "Track remediation actions, priorities, assignees, due dates, and overdue items.",
      icon: ListChecks,
      color: "orange",
      path: "/reports/corrective-actions",
    },
  ];

  return (
    <AppLayout>
      <div className="mx-auto max-w-7xl space-y-8">

        {/* Header */}

        <div>
          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-indigo-50 p-3">
              <BarChart3 className="h-6 w-6 text-indigo-600" />
            </div>

            <div>
              <h1 className="text-3xl font-bold text-slate-900">
                Reports
              </h1>

              <p className="mt-1 text-slate-500">
                Security, risk, audit, compliance, and remediation reporting.
              </p>
            </div>

          </div>
        </div>

        {/* Report Cards */}

        <div className="grid gap-6 md:grid-cols-2">

          {reports.map((report) => {

            const Icon = report.icon;

            return (
              <button
                key={report.title}
                type="button"
                onClick={() => navigate(report.path)}
                className="group rounded-2xl border bg-white p-6 text-left shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
              >

                <div className="flex items-start justify-between">

                  <div className="flex items-center gap-4">

                    <div className="rounded-xl bg-slate-100 p-3 transition group-hover:bg-indigo-50">

                      <Icon
                        className="h-6 w-6 text-slate-600 transition group-hover:text-indigo-600"
                      />

                    </div>

                    <div>

                      <h2 className="font-semibold text-slate-900">
                        {report.title}
                      </h2>

                      <p className="mt-1 max-w-xl text-sm leading-6 text-slate-500">
                        {report.description}
                      </p>

                    </div>

                  </div>

                  <ArrowRight
                    className="mt-1 h-5 w-5 text-slate-300 transition group-hover:translate-x-1 group-hover:text-indigo-600"
                  />

                </div>

              </button>
            );
          })}

        </div>

        {/* Information */}

        <div className="rounded-2xl border bg-slate-50 p-6">

          <div className="flex items-start gap-3">

            <div className="rounded-lg bg-indigo-100 p-2">
              <BarChart3 className="h-5 w-5 text-indigo-600" />
            </div>

            <div>

              <h2 className="font-semibold text-slate-900">
                GRC Reporting Workspace
              </h2>

              <p className="mt-1 text-sm leading-6 text-slate-600">
                Use the reports workspace to review live information from
                the CyberGRC platform. Reports are generated from the current
                database state and can be used for governance, risk,
                compliance, audit, and remediation reviews.
              </p>

            </div>

          </div>

        </div>

      </div>
    </AppLayout>
  );
}