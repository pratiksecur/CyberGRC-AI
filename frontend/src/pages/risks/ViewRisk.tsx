import { type ComponentType } from "react";
import { useNavigate, useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";
import RiskAIInsights from "@/components/ai/RiskAIInsights";

import { Button } from "@/components/ui/button";

import {
  AlertTriangle,
  ArrowLeft,
  Brain,
  CheckCircle2,
  ClipboardCheck,
  FileCheck2,
  Pencil,
  RefreshCw,
  ShieldAlert,
  Target,
} from "lucide-react";

import { useRisk } from "@/hooks/useRisk";
import {
  useRiskIntelligence,
} from "@/hooks/useGRCIntelligence";
import {
  useRiskMonitoring,
} from "@/hooks/useMonitoring";

import Can from "@/components/auth/Can";

import RiskScoreBadge from "@/components/risks/RiskScoreBadge";
import RiskStatusBadge from "@/components/risks/RiskStatusBadge";


// ==========================================================
// Helpers
// ==========================================================

function riskScoreClass(score: number) {
  if (score >= 20) {
    return "bg-red-100 text-red-700 border-red-200";
  }

  if (score >= 15) {
    return "bg-orange-100 text-orange-700 border-orange-200";
  }

  if (score >= 8) {
    return "bg-yellow-100 text-yellow-700 border-yellow-200";
  }

  return "bg-green-100 text-green-700 border-green-200";
}


function formatPercent(value: number) {
  return `${value.toFixed(1)}%`;
}


// ==========================================================
// Page
// ==========================================================

export default function ViewRisk() {
  const navigate = useNavigate();

  const { id } = useParams();

  const riskId = Number(id);

  const {
    data,
    isLoading,
    error,
  } = useRisk(riskId);

  const {
    data: intelligence,
    isLoading: intelligenceLoading,
    error: intelligenceError,
    refetch: refetchIntelligence,
    isFetching: intelligenceFetching,
  } = useRiskIntelligence(riskId);

  const {
    data: monitoring,
    isLoading: monitoringLoading,
    error: monitoringError,
    refetch: refetchMonitoring,
    isFetching: monitoringFetching,
  } = useRiskMonitoring(riskId);


  // ========================================================
  // Loading
  // ========================================================

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10 text-center">
          Loading Risk...
        </div>
      </AppLayout>
    );
  }


  // ========================================================
  // Error
  // ========================================================

  if (error || !data) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Risk not found.
        </div>
      </AppLayout>
    );
  }


  const metrics = intelligence?.metrics;

  const criticalAlerts =
    monitoring?.alerts.filter(
      (alert) =>
        alert.severity.toLowerCase() === "critical"
    ) ?? [];

  const highAlerts =
    monitoring?.alerts.filter(
      (alert) =>
        alert.severity.toLowerCase() === "high"
    ) ?? [];


  return (
    <AppLayout>

      <div className="mx-auto max-w-7xl space-y-6">

        {/* ==================================================
            Header
        ================================================== */}

        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

          <div>

            <div className="flex items-center gap-3">

              <h1 className="text-3xl font-bold text-slate-900">
                {data.title}
              </h1>

              <RiskScoreBadge
                score={data.risk_score}
              />

            </div>

            <p className="mt-2 text-slate-500">
              Risk Details and GRC Posture
            </p>

          </div>


          <div className="flex flex-wrap gap-3">

            {/* Back */}

            <Button
              variant="outline"
              onClick={() => navigate("/risks")}
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>


            {/* Intelligence */}

            <Button
              variant="outline"
              onClick={() => navigate("/intelligence")}
            >
              <Brain className="mr-2 h-4 w-4" />
              GRC Intelligence
            </Button>


            {/* Monitoring */}

            <Button
              variant="outline"
              onClick={() => navigate("/monitoring")}
            >
              <ShieldAlert className="mr-2 h-4 w-4" />
              Monitoring
            </Button>


            {/* Edit */}

            <Can resource="risks" action="update">
              <Button
                onClick={() =>
                  navigate(`/risks/${data.id}/edit`)
                }
              >
                <Pencil className="mr-2 h-4 w-4" />
                Edit Risk
              </Button>
            </Can>

          </div>

        </div>


        {/* ==================================================
            Description
        ================================================== */}

        <div className="rounded-xl border bg-white p-6 shadow-sm">

          <h2 className="mb-3 text-lg font-semibold">
            Description
          </h2>

          <p className="leading-7 text-slate-600">
            {data.description}
          </p>

        </div>


        {/* ==================================================
            Risk Details
        ================================================== */}

        <div className="grid gap-6 md:grid-cols-2">

          <div className="rounded-xl border bg-white p-6 shadow-sm">

            <h2 className="mb-5 text-lg font-semibold">
              Risk Information
            </h2>

            <div className="space-y-4">

              <div className="flex justify-between">
                <span className="text-slate-500">
                  Likelihood
                </span>

                <span>
                  {data.likelihood}
                </span>
              </div>


              <div className="flex justify-between">
                <span className="text-slate-500">
                  Impact
                </span>

                <span>
                  {data.impact}
                </span>
              </div>


              <div className="flex justify-between">
                <span className="text-slate-500">
                  Owner
                </span>

                <span>
                  User #{data.owner_id}
                </span>
              </div>

            </div>

          </div>


          <div className="rounded-xl border bg-white p-6 shadow-sm">

            <h2 className="mb-5 text-lg font-semibold">
              Assessment
            </h2>

            <div className="space-y-4">

              <div className="flex justify-between">

                <span className="text-slate-500">
                  Risk Score
                </span>

                <RiskScoreBadge
                  score={data.risk_score}
                />

              </div>


              <div className="flex justify-between">

                <span className="text-slate-500">
                  Status
                </span>

                <RiskStatusBadge
                  status={data.status}
                />

              </div>


              <div className="flex justify-between">

                <span className="text-slate-500">
                  Created
                </span>

                <span>
                  {new Date(
                    data.created_at
                  ).toLocaleDateString()}
                </span>

              </div>


              <div className="flex justify-between">

                <span className="text-slate-500">
                  Updated
                </span>

                <span>
                  {new Date(
                    data.updated_at
                  ).toLocaleDateString()}
                </span>

              </div>

            </div>

          </div>

        </div>


        {/* ==================================================
            GRC Intelligence
        ================================================== */}

        <section className="rounded-2xl border bg-white shadow-sm">

          <div className="border-b p-6">

            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">

              <div className="flex items-start gap-3">

                <div className="rounded-xl bg-indigo-50 p-3">

                  <Brain className="h-6 w-6 text-indigo-600" />

                </div>

                <div>

                  <h2 className="text-lg font-semibold text-slate-900">
                    GRC Intelligence
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Connected intelligence across controls, evidence,
                    findings, remediation, and residual risk.
                  </p>

                </div>

              </div>


              <div className="flex gap-2">

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => refetchIntelligence()}
                  disabled={
                    intelligenceLoading ||
                    intelligenceFetching
                  }
                >
                  <RefreshCw
                    className={`mr-2 h-4 w-4 ${
                      intelligenceFetching
                        ? "animate-spin"
                        : ""
                    }`}
                  />
                  Refresh
                </Button>


                <Button
                  size="sm"
                  onClick={() => navigate("/intelligence")}
                >
                  Open Intelligence
                </Button>

              </div>

            </div>

          </div>


          <div className="p-6">

            {intelligenceLoading ? (

              <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

                {Array.from({ length: 8 }).map(
                  (_, index) => (
                    <div
                      key={index}
                      className="h-24 animate-pulse rounded-xl bg-slate-100"
                    />
                  )
                )}

              </div>

            ) : intelligenceError || !intelligence || !metrics ? (

              <div className="rounded-xl border border-red-200 bg-red-50 p-5">

                <div className="flex items-start gap-3">

                  <AlertTriangle className="mt-0.5 h-5 w-5 text-red-600" />

                  <div>

                    <h3 className="font-semibold text-red-700">
                      Intelligence unavailable
                    </h3>

                    <p className="mt-1 text-sm text-red-600">
                      Risk intelligence could not be loaded.
                    </p>

                  </div>

                </div>

              </div>

            ) : (

              <>

                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

                  <IntelligenceMetric
                    label="Controls"
                    value={metrics.control_count}
                    icon={Target}
                  />

                  <IntelligenceMetric
                    label="Evidence Coverage"
                    value={formatPercent(
                      metrics.evidence_coverage_percent
                    )}
                    icon={FileCheck2}
                  />

                  <IntelligenceMetric
                    label="Control Effectiveness"
                    value={formatPercent(
                      metrics.average_control_effectiveness
                    )}
                    icon={CheckCircle2}
                  />

                  <IntelligenceMetric
                    label="Frameworks"
                    value={metrics.framework_count}
                    icon={ClipboardCheck}
                  />

                  <IntelligenceMetric
                    label="Findings"
                    value={metrics.finding_count}
                    icon={AlertTriangle}
                  />

                  <IntelligenceMetric
                    label="Open Findings"
                    value={metrics.open_findings}
                    icon={AlertTriangle}
                  />

                  <IntelligenceMetric
                    label="Overdue Actions"
                    value={metrics.overdue_actions}
                    icon={ShieldAlert}
                  />

                  <IntelligenceMetric
                    label="Residual Risk"
                    value={metrics.estimated_residual_risk.toFixed(1)}
                    icon={ShieldAlert}
                    emphasis={
                      metrics.estimated_residual_risk >= 15
                        ? "critical"
                        : undefined
                    }
                  />

                </div>


                <div className="mt-6 grid gap-4 md:grid-cols-3">

                  <PostureCard
                    title="Control Coverage"
                    value={`${metrics.control_count} controls`}
                    detail={`${metrics.controls_with_evidence} with evidence`}
                  />

                  <PostureCard
                    title="Remediation"
                    value={formatPercent(
                      metrics.remediation_completion_percent
                    )}
                    detail={`${metrics.open_actions} open actions`}
                  />

                  <PostureCard
                    title="Findings"
                    value={`${metrics.critical_findings} critical`}
                    detail={`${metrics.open_findings} open findings`}
                  />

                </div>

              </>

            )}

          </div>

        </section>


        {/* ==================================================
            AI Risk Intelligence
        ================================================== */}

        <RiskAIInsights riskId={riskId} />


        {/* ==================================================
            Continuous Monitoring
        ================================================== */}

        <section className="rounded-2xl border bg-white shadow-sm">

          <div className="border-b p-6">

            <div className="flex flex-col justify-between gap-4 sm:flex-row sm:items-center">

              <div className="flex items-start gap-3">

                <div className="rounded-xl bg-red-50 p-3">

                  <ShieldAlert className="h-6 w-6 text-red-600" />

                </div>

                <div>

                  <h2 className="text-lg font-semibold text-slate-900">
                    Continuous Monitoring
                  </h2>

                  <p className="mt-1 text-sm text-slate-500">
                    Current monitoring conditions detected for this risk.
                  </p>

                </div>

              </div>


              <div className="flex gap-2">

                <Button
                  variant="outline"
                  size="sm"
                  onClick={() => refetchMonitoring()}
                  disabled={
                    monitoringLoading ||
                    monitoringFetching
                  }
                >
                  <RefreshCw
                    className={`mr-2 h-4 w-4 ${
                      monitoringFetching
                        ? "animate-spin"
                        : ""
                    }`}
                  />
                  Refresh
                </Button>


                <Button
                  size="sm"
                  onClick={() => navigate("/monitoring")}
                >
                  Open Monitoring
                </Button>

              </div>

            </div>

          </div>


          <div className="p-6">

            {monitoringLoading ? (

              <div className="grid gap-4 md:grid-cols-3">

                {Array.from({ length: 3 }).map(
                  (_, index) => (
                    <div
                      key={index}
                      className="h-24 animate-pulse rounded-xl bg-slate-100"
                    />
                  )
                )}

              </div>

            ) : monitoringError || !monitoring ? (

              <div className="rounded-xl border border-red-200 bg-red-50 p-5">

                <div className="flex items-start gap-3">

                  <AlertTriangle className="mt-0.5 h-5 w-5 text-red-600" />

                  <div>

                    <h3 className="font-semibold text-red-700">
                      Monitoring unavailable
                    </h3>

                    <p className="mt-1 text-sm text-red-600">
                      Risk monitoring could not be loaded.
                    </p>

                  </div>

                </div>

              </div>

            ) : (

              <>

                <div className="grid gap-4 md:grid-cols-3">

                  <PostureCard
                    title="Total Alerts"
                    value={String(monitoring.alerts.length)}
                    detail="Current detected conditions"
                  />

                  <PostureCard
                    title="Critical Alerts"
                    value={String(criticalAlerts.length)}
                    detail="Immediate attention conditions"
                    emphasis={
                      criticalAlerts.length > 0
                        ? "critical"
                        : undefined
                    }
                  />

                  <PostureCard
                    title="High Alerts"
                    value={String(highAlerts.length)}
                    detail="High-priority conditions"
                    emphasis={
                      highAlerts.length > 0
                        ? "warning"
                        : undefined
                    }
                  />

                </div>


                {monitoring.alerts.length === 0 ? (

                  <div className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 p-5">

                    <div className="flex items-start gap-3">

                      <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" />

                      <div>

                        <h3 className="font-semibold text-emerald-700">
                          No active monitoring alerts
                        </h3>

                        <p className="mt-1 text-sm text-emerald-600">
                          No monitored conditions currently require
                          attention for this risk.
                        </p>

                      </div>

                    </div>

                  </div>

                ) : (

                  <div className="mt-6 space-y-3">

                    {monitoring.alerts
                      .slice(0, 5)
                      .map((alert) => (

                        <div
                          key={`${alert.alert_type}-${alert.resource_type}-${alert.resource_id}`}
                          className="rounded-xl border p-4"
                        >

                          <div className="flex items-start justify-between gap-4">

                            <div className="min-w-0">

                              <div className="flex flex-wrap items-center gap-2">

                                <span
                                  className={`rounded-full border px-2.5 py-1 text-xs font-semibold uppercase ${riskScoreClass(
                                    alert.severity
                                      .toLowerCase() === "critical"
                                      ? 20
                                      : alert.severity
                                          .toLowerCase() === "high"
                                        ? 15
                                        : alert.severity
                                            .toLowerCase() === "medium"
                                          ? 8
                                          : 1
                                  )}`}
                                >
                                  {alert.severity}
                                </span>

                                <span className="text-xs font-medium uppercase tracking-wide text-slate-400">
                                  {alert.alert_type.replace(
                                    /_/g,
                                    " "
                                  )}
                                </span>

                              </div>


                              <h3 className="mt-2 font-semibold text-slate-900">
                                {alert.title}
                              </h3>


                              <p className="mt-1 text-sm leading-6 text-slate-600">
                                {alert.message}
                              </p>

                            </div>


                            <span className="shrink-0 text-xs text-slate-400">
                              {new Date(
                                alert.detected_at
                              ).toLocaleString()}
                            </span>

                          </div>

                        </div>

                      ))}

                  </div>

                )}

              </>

            )}

          </div>

        </section>


        {/* ==================================================
            Connected GRC Lifecycle
        ================================================== */}

        <section className="rounded-2xl border border-slate-700 bg-slate-900 p-6">

          <div className="flex items-start gap-3">

            <div className="rounded-lg bg-slate-950 p-2">

              <Brain className="h-5 w-5 text-indigo-400" />

            </div>

            <div>

              <h2 className="text-sm font-semibold text-white">
                Connected GRC Lifecycle
              </h2>

              <p className="mt-1 text-sm leading-6 text-slate-300">
                This risk is evaluated across its connected controls,
                evidence, frameworks, findings, corrective actions,
                and monitoring conditions. Intelligence and monitoring
                respect the same resource visibility boundaries as the
                underlying GRC data.
              </p>

            </div>

          </div>

        </section>

      </div>

    </AppLayout>
  );
}


// ==========================================================
// Intelligence Metric
// ==========================================================

interface IntelligenceMetricProps {
  label: string;
  value: number | string;
  icon: ComponentType<{
    className?: string;
  }>;
  emphasis?: "critical";
}

function IntelligenceMetric({
  label,
  value,
  icon: Icon,
  emphasis,
}: IntelligenceMetricProps) {
  return (
    <div
      className={`rounded-xl border p-4 ${
        emphasis === "critical"
          ? "border-red-200 bg-red-50"
          : "bg-slate-50"
      }`}
    >

      <div className="flex items-center justify-between">

        <span className="text-sm text-slate-500">
          {label}
        </span>

        <Icon
          className={`h-5 w-5 ${
            emphasis === "critical"
              ? "text-red-600"
              : "text-slate-400"
          }`}
        />

      </div>

      <p
        className={`mt-2 text-2xl font-bold ${
          emphasis === "critical"
            ? "text-red-700"
            : "text-slate-900"
        }`}
      >
        {value}
      </p>

    </div>
  );
}


// ==========================================================
// Posture Card
// ==========================================================

interface PostureCardProps {
  title: string;
  value: string;
  detail: string;
  emphasis?: "critical" | "warning";
}

function PostureCard({
  title,
  value,
  detail,
  emphasis,
}: PostureCardProps) {
  return (
    <div
      className={`rounded-xl border p-5 ${
        emphasis === "critical"
          ? "border-red-200 bg-red-50"
          : emphasis === "warning"
            ? "border-orange-200 bg-orange-50"
            : "bg-slate-50"
      }`}
    >

      <p className="text-sm font-medium text-slate-500">
        {title}
      </p>

      <p
        className={`mt-2 text-xl font-bold ${
          emphasis === "critical"
            ? "text-red-700"
            : emphasis === "warning"
              ? "text-orange-700"
              : "text-slate-900"
        }`}
      >
        {value}
      </p>

      <p className="mt-1 text-xs text-slate-500">
        {detail}
      </p>

    </div>
  );
}