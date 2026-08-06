import AppLayout from "@/layouts/AppLayout";

import StatCard from "@/components/dashboard/StatCard";
import AISummary from "@/components/dashboard/AISummary";

import {
  ShieldAlert,
  ShieldCheck,
  ClipboardList,
  BadgeCheck,
} from "lucide-react";

import {
  dashboardStats,
  aiSummary,
} from "@/data/dashboard";

const icons = {
  risk: ShieldAlert,
  control: ShieldCheck,
  audit: ClipboardList,
  compliance: BadgeCheck,
};

export default function Dashboard() {
  return (
    <AppLayout>
      <div className="space-y-8">

        {/* Header */}

        <div>

          <h1 className="text-4xl font-bold text-slate-900">
            Good Morning, Pratik 👋
          </h1>

          <p className="mt-2 text-slate-500">
            Here's your organization's cybersecurity posture today.
          </p>

        </div>

        {/* KPI Cards */}

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">

          {dashboardStats.map((stat) => {
            const Icon =
              icons[
                stat.icon as keyof typeof icons
              ];

            return (
              <StatCard
                key={stat.title}
                title={stat.title}
                value={stat.value}
                subtitle={stat.subtitle}
                icon={Icon}
                iconColor={stat.color}
              />
            );
          })}

        </div>

        {/* Dashboard Widgets */}

        <div className="grid gap-6 lg:grid-cols-3">

          {/* AI Summary */}

          <div className="lg:col-span-2">

            <AISummary
              riskLevel={aiSummary.organizationRiskLevel}
              summary={aiSummary.executiveSummary}
              priorities={aiSummary.topPriorities}
              nextSteps={aiSummary.recommendedNextSteps}
            />

          </div>

          {/* Placeholder */}

          <div className="rounded-2xl border border-dashed border-slate-300 bg-white p-6">

            <h2 className="text-xl font-bold">
              Risk Trend
            </h2>

            <p className="mt-4 text-slate-500">
              Chart coming in the next phase...
            </p>

          </div>

        </div>

      </div>
    </AppLayout>
  );
}