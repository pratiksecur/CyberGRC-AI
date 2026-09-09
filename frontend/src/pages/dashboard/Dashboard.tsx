import AppLayout from "@/layouts/AppLayout";

import StatCard from "@/components/dashboard/StatCard";
import AISummary from "@/components/dashboard/AISummary";
import SecurityHealth from "@/components/dashboard/SecurityHealth";
import RecentActivity from "@/components/dashboard/RecentActivity";
import RiskTrend from "@/components/dashboard/RiskTrend";
import FindingsActionsOverview from "@/components/dashboard/FindingsActionsOverview";
import CriticalRemediation from "@/components/dashboard/CriticalRemediation";

import { useDashboard } from "@/hooks/useDashboard";
import { useExecutiveSummary } from "@/hooks/useExecutiveSummary";
import { useAuth } from "@/contexts/AuthContext";

import {
  ShieldAlert,
  ShieldCheck,
  ClipboardList,
  BadgeCheck,
  FileCheck2,
  ListChecks,
  AlertTriangle,
} from "lucide-react";

import {
  hasPermission,
  type UserRole,
} from "@/auth/permissions";


const icons = {
  risk: ShieldAlert,
  control: ShieldCheck,
  audit: ClipboardList,
  compliance: BadgeCheck,
  evidence: FileCheck2,
  findings: AlertTriangle,
  actions: ListChecks,
};


interface DashboardStat {
  title: string;
  value: number | string;
  subtitle: string;
  icon: keyof typeof icons;
  color: string;
}


function createDashboardStats(
  role: UserRole,
  data: {
    totalRisks: number;
    controls: number;
    audits: number;
    compliance: number;
    activeControls: number;
    totalEvidence: number;
    totalFindings: number;
    criticalFindings: number;
    totalActions: number;
    pendingActions: number;
    criticalRisks: number;
  }
): DashboardStat[] {

  // ==================================================
  // RISK ANALYST
  // ==================================================

  if (role === "Risk Analyst") {

    return [
      {
        title: "My Risks",
        value: data.totalRisks,
        subtitle:
          `${data.criticalRisks} Critical`,
        icon: "risk",
        color: "bg-red-500",
      },

      {
        title: "My Controls",
        value: data.controls,
        subtitle:
          `${data.activeControls} Active`,
        icon: "control",
        color: "bg-emerald-500",
      },

      {
        title: "Findings",
        value: data.totalFindings,
        subtitle:
          `${data.criticalFindings} Critical`,
        icon: "findings",
        color: "bg-amber-500",
      },

      {
        title: "Pending Actions",
        value: data.pendingActions,
        subtitle:
          `${data.totalActions} Total`,
        icon: "actions",
        color: "bg-blue-600",
      },
    ];
  }


  // ==================================================
  // AUDITOR
  // ==================================================

  if (role === "Auditor") {

    return [
      {
        title: "My Audits",
        value: data.audits,
        subtitle: "Assigned audits",
        icon: "audit",
        color: "bg-blue-600",
      },

      {
        title: "Findings",
        value: data.totalFindings,
        subtitle:
          `${data.criticalFindings} Critical`,
        icon: "findings",
        color: "bg-red-500",
      },

      {
        title: "Corrective Actions",
        value: data.totalActions,
        subtitle:
          `${data.pendingActions} Pending`,
        icon: "actions",
        color: "bg-emerald-500",
      },

      {
        title: "Control Effectiveness",
        value:
          `${data.compliance}%`,
        subtitle:
          "Authorized controls",
        icon: "compliance",
        color: "bg-amber-500",
      },
    ];
  }


  // ==================================================
  // EMPLOYEE
  // ==================================================

  if (role === "Employee") {

    return [
      {
        title: "My Risks",
        value: data.totalRisks,
        subtitle:
          `${data.criticalRisks} Critical`,
        icon: "risk",
        color: "bg-red-500",
      },

      {
        title: "My Evidence",
        value: data.totalEvidence,
        subtitle:
          "Uploaded evidence",
        icon: "evidence",
        color: "bg-amber-500",
      },

      {
        title: "My Actions",
        value: data.totalActions,
        subtitle:
          `${data.pendingActions} Pending`,
        icon: "actions",
        color: "bg-emerald-500",
      },

      {
        title: "Critical Risks",
        value: data.criticalRisks,
        subtitle:
          "Within your scope",
        icon: "risk",
        color: "bg-blue-600",
      },
    ];
  }


  // ==================================================
  // ADMIN / GRC MANAGER
  // ==================================================

  return [
    {
      title: "Total Risks",
      value: data.totalRisks,
      subtitle:
        `${data.criticalRisks} Critical`,
      icon: "risk",
      color: "bg-red-500",
    },

    {
      title: "Controls",
      value: data.controls,
      subtitle:
        `${data.activeControls} Active`,
      icon: "control",
      color: "bg-emerald-500",
    },

    {
      title: "Audits",
      value: data.audits,
      subtitle:
        "Within your scope",
      icon: "audit",
      color: "bg-blue-600",
    },

    {
      title: "Control Effectiveness",
      value:
        `${data.compliance}%`,
      subtitle:
        "Authorized controls",
      icon: "compliance",
      color: "bg-amber-500",
    },
  ];
}


export default function Dashboard() {

  const { user } = useAuth();

  const {
    data,
    isLoading,
    error,
  } = useDashboard();

  const role =
    user?.role as UserRole | undefined;


  // ==================================================
  // EXECUTIVE SUMMARY PERMISSION
  // ==================================================

  const canViewExecutiveSummary =
    hasPermission(
      role,
      "ai_executive_summary",
      "view"
    );


  const {
    data: aiData,
    isLoading: aiLoading,
    error: aiError,
  } = useExecutiveSummary(
    canViewExecutiveSummary
  );


  // ==================================================
  // GREETING
  // ==================================================

  const hour =
    new Date().getHours();

  let greeting =
    "Good Morning";

  if (
    hour >= 12 &&
    hour < 17
  ) {

    greeting =
      "Good Afternoon";

  } else if (
    hour >= 17 &&
    hour < 21
  ) {

    greeting =
      "Good Evening";

  } else if (
    hour >= 21 ||
    hour < 5
  ) {

    greeting =
      "Good Night";
  }


  const userName =
    user?.full_name ||
    "there";


  // ==================================================
  // LOADING
  // ==================================================

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


  // ==================================================
  // ERROR
  // ==================================================

  if (
    error ||
    !data ||
    !role
  ) {

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


  // ==================================================
  // ROLE FLAGS
  // ==================================================

  const isAdmin =
    role === "Admin";

  const isGRCManager =
    role === "GRC Manager";

  const isEmployee =
    role === "Employee";

  const showFindingsOverview =
    !isEmployee;

  const showSecurityHealth =
    !isEmployee;

  const showRiskTrend =
    role !== "Auditor" &&
    role !== "Employee";

  const showCriticalRemediation =
    !isEmployee;

  const showActivity = true;


  // ==================================================
  // ROLE-SPECIFIC DESCRIPTION
  // ==================================================

  const dashboardDescription =
    isAdmin
      ? "Here's your organization's cybersecurity posture today."

      : isGRCManager
        ? "Here's the GRC posture across your management scope today."

        : role === "Risk Analyst"
          ? "Here's your risk and remediation posture today."

          : role === "Auditor"
            ? "Here's your audit and findings posture today."

            : "Here's your assigned GRC work and current status.";


  const dashboardStats =
    createDashboardStats(
      role,
      data
    );


  // ==================================================
  // RENDER
  // ==================================================

  return (
    <AppLayout>

      <div className="space-y-8">


        {/* ==================================================
            HEADER
        ================================================== */}

        <div>

          <h1 className="text-4xl font-bold text-slate-900">

            {greeting},{" "}
            {userName} 👋

          </h1>

          <p className="mt-2 text-slate-500">

            {dashboardDescription}

          </p>

        </div>


        {/* ==================================================
            KPI CARDS
        ================================================== */}

        <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">

          {dashboardStats.map(
            (stat) => {

              const Icon =
                icons[stat.icon];

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

            }
          )}

        </div>


        {/* ==================================================
            FINDINGS / REMEDIATION
        ================================================== */}

        {showFindingsOverview && (

          <FindingsActionsOverview
            totalFindings={
              data.totalFindings
            }

            openFindings={
              data.openFindings
            }

            criticalFindings={
              data.criticalFindings
            }

            totalActions={
              data.totalActions
            }

            pendingActions={
              data.pendingActions
            }

            overdueActions={
              data.overdueActions
            }
          />

        )}


        {/* ==================================================
            AI + SECURITY HEALTH
        ================================================== */}

        <div
          className={
            `grid gap-6 ${
              showSecurityHealth &&
              canViewExecutiveSummary
                ? "lg:grid-cols-3"
                : "lg:grid-cols-1"
            }`
          }
        >


          {/* ----------------------------------------------
              AI EXECUTIVE SUMMARY

              This entire block does NOT exist for roles
              without ai_executive_summary permission.
          ---------------------------------------------- */}

          {canViewExecutiveSummary && (

            <div className="lg:col-span-2">

              {aiLoading ? (

                <div className="rounded-2xl border bg-white p-8 text-center">

                  <p className="text-slate-500">

                    Generating AI Executive Summary...

                  </p>

                </div>

              ) : aiError || !aiData ? (

                <div className="rounded-2xl border bg-white p-8 text-center">

                  <p className="text-red-500">

                    Failed to load AI summary.

                  </p>

                </div>

              ) : (

                <AISummary
                  riskLevel={
                    aiData.organization_risk_level
                  }

                  summary={
                    aiData.executive_summary
                  }

                  priorities={
                    aiData.top_priorities
                  }

                  nextSteps={
                    aiData.recommended_next_steps
                  }
                />

              )}

            </div>

          )}


          {/* ----------------------------------------------
              SECURITY HEALTH
          ---------------------------------------------- */}

          {showSecurityHealth && (

            <div
              className={
                canViewExecutiveSummary
                  ? ""
                  : "lg:col-span-1"
              }
            >

              <SecurityHealth
                score={
                  data.securityHealth
                }

                activeControls={
                  data.activeControls
                }

                criticalRisks={
                  data.criticalRisks
                }
              />

            </div>

          )}

        </div>


        {/* ==================================================
            RECENT ACTIVITY / RISK TREND
        ================================================== */}

        {showActivity && (

          <div
            className={
              `grid gap-6 ${
                showRiskTrend
                  ? "lg:grid-cols-2"
                  : "lg:grid-cols-1"
              }`
            }
          >

            <RecentActivity />

            {showRiskTrend && (
              <RiskTrend />
            )}

          </div>

        )}


        {/* ==================================================
            CRITICAL REMEDIATION
        ================================================== */}

        {showCriticalRemediation && (

          <CriticalRemediation
            data={
              data.criticalRemediation
            }
          />

        )}

      </div>

    </AppLayout>
  );
}