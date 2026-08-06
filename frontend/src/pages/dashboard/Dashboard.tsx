import AppLayout from "@/layouts/AppLayout";

import StatCard from "@/components/dashboard/StatCard";
import AISummary from "@/components/dashboard/AISummary";
import SecurityHealth from "@/components/dashboard/SecurityHealth";
import RecentActivity from "@/components/dashboard/RecentActivity";
import RiskTrend from "@/components/dashboard/RiskTrend";

import { useDashboard } from "@/hooks/useDashboard";

import {
  ShieldAlert,
  ShieldCheck,
  ClipboardList,
  BadgeCheck,
} from "lucide-react";

import { aiSummary } from "@/data/dashboard";

const icons = {
  risk: ShieldAlert,
  control: ShieldCheck,
  audit: ClipboardList,
  compliance: BadgeCheck,
};

const createDashboardStats = (data: {
  totalRisks: number;
  controls: number;
  audits: number;
  compliance: number;
  activeControls: number;
}) => [
  {
    title: "Total Risks",
    value: data.totalRisks,
    subtitle: "Live Database",
    icon: "risk",
    color: "bg-red-500",
  },
  {
    title: "Controls",
    value: data.controls,
    subtitle: `${data.activeControls} Active`,
    icon: "control",
    color: "bg-emerald-500",
  },
  {
    title: "Audits",
    value: data.audits,
    subtitle: "In Database",
    icon: "audit",
    color: "bg-blue-600",
  },
  {
    title: "Compliance",
    value: `${data.compliance}%`,
    subtitle: "ISO 27001",
    icon: "compliance",
    color: "bg-amber-500",
  },
];

export default function Dashboard() {

  const { data, isLoading, error } = useDashboard();

  if (isLoading) {
    return (
      <AppLayout>
        <div className="flex h-96 items-center justify-center">
          <p className="text-lg text-slate-500">
            Loading dashboard...
          </p>
        </div>
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="flex h-96 items-center justify-center">
          <p className="text-lg text-red-500">
            Failed to load dashboard.
          </p>
        </div>
      </AppLayout>
    );
  }

  const dashboardStats = createDashboardStats(data);

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

          <div className="lg:col-span-2">

            <AISummary
              riskLevel={aiSummary.organizationRiskLevel}
              summary={aiSummary.executiveSummary}
              priorities={aiSummary.topPriorities}
              nextSteps={aiSummary.recommendedNextSteps}
            />

          </div>

          <SecurityHealth
            score={data.securityHealth}
            activeControls={data.activeControls}
            criticalRisks={data.criticalRisks}
          />

        </div>

        <div className="grid gap-6 lg:grid-cols-2">

          <RecentActivity />

          <RiskTrend />

        </div>

      </div>
    </AppLayout>
  );
}