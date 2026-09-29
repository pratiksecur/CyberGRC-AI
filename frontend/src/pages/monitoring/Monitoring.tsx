import {
  Activity,
  AlertCircle,
  AlertTriangle,
  ArrowRight,
  CheckCircle2,
  Clock,
  FileWarning,
  RefreshCw,
  ShieldAlert,
  ShieldCheck,
  UserCheck,
  XCircle,
} from "lucide-react";

import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useMonitoring } from "@/hooks/useMonitoring";


// ==========================================================
// Helpers
// ==========================================================

function severityClass(
  severity: string
) {
  switch (severity.toLowerCase()) {
    case "critical":
      return "bg-red-100 text-red-700 border-red-200";

    case "high":
      return "bg-orange-100 text-orange-700 border-orange-200";

    case "medium":
      return "bg-yellow-100 text-yellow-700 border-yellow-200";

    default:
      return "bg-blue-100 text-blue-700 border-blue-200";
  }
}


function priorityClass(
  priority: string
) {
  switch (priority.toUpperCase()) {
    case "CRITICAL":
      return "bg-red-100 text-red-700 border-red-200";

    case "HIGH":
      return "bg-orange-100 text-orange-700 border-orange-200";

    case "MEDIUM":
      return "bg-yellow-100 text-yellow-700 border-yellow-200";

    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
  }
}


function stateClass(
  state: string
) {
  switch (state.toUpperCase()) {
    case "REASSESSMENT_REQUIRED":
    case "REQUIRES_REASSESSMENT":
      return "bg-red-100 text-red-700 border-red-200";

    case "DEGRADED":
    case "STALE":
      return "bg-orange-100 text-orange-700 border-orange-200";

    case "CURRENT":
      return "bg-emerald-100 text-emerald-700 border-emerald-200";

    default:
      return "bg-slate-100 text-slate-700 border-slate-200";
  }
}


function formatLabel(
  value: string
) {
  return value
    .toLowerCase()
    .split("_")
    .map(
      (part) =>
        part.charAt(0).toUpperCase() +
        part.slice(1)
    )
    .join(" ");
}


function formatDateTime(
  value: string
) {
  if (!value) {
    return "—";
  }

  return new Date(value).toLocaleString(
    "en-IE",
    {
      dateStyle: "medium",
      timeStyle: "short",
    }
  );
}


function resourcePath(
  resourceType: string,
  resourceId: number
) {
  switch (
    resourceType.toLowerCase()
  ) {
    case "risk":
      return `/risks/${resourceId}`;

    case "control":
      return `/controls/${resourceId}`;

    case "evidence":
      return `/evidence/${resourceId}`;

    case "audit":
      return `/audits/${resourceId}`;

    case "finding":
    case "audit_finding":
      return `/audit-findings/${resourceId}`;

    case "corrective_action":
    case "corrective action":
      return `/corrective-actions/${resourceId}`;

    default:
      return null;
  }
}


// ==========================================================
// Page
// ==========================================================

export default function Monitoring() {
  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
    refetch,
    isFetching,
  } = useMonitoring();


  // ========================================================
  // Loading
  // ========================================================

  if (isLoading) {
    return (
      <AppLayout>

        <div className="mx-auto max-w-7xl space-y-6">

          <div className="h-10 w-80 animate-pulse rounded-lg bg-slate-200" />

          <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
            {Array.from({ length: 8 }).map(
              (_, index) => (
                <div
                  key={index}
                  className="h-28 animate-pulse rounded-xl bg-slate-100"
                />
              )
            )}
          </div>

          <div className="h-96 animate-pulse rounded-xl bg-slate-100" />

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

        <div className="mx-auto max-w-4xl">

          <div className="rounded-2xl border border-red-200 bg-red-50 p-6">

            <div className="flex items-start gap-3">

              <AlertTriangle className="mt-0.5 h-6 w-6 text-red-600" />

              <div>

                <h2 className="font-semibold text-red-700">
                  Continuous Monitoring Unavailable
                </h2>

                <p className="mt-1 text-sm leading-6 text-red-600">
                  The monitoring overview could not be loaded.
                  Please try again.
                </p>

                <button
                  type="button"
                  onClick={() => refetch()}
                  className="mt-4 inline-flex items-center rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
                >
                  <RefreshCw className="mr-2 h-4 w-4" />
                  Try Again
                </button>

              </div>

            </div>

          </div>

        </div>

      </AppLayout>
    );
  }


  const metrics = data.metrics;

  const riskResponses =
    data.risk_responses ?? [];

  const responseRisks =
    riskResponses.filter(
      (response) =>
        response.response_required
    );


  return (
    <AppLayout>

      <div className="mx-auto max-w-7xl space-y-8">

        {/* ==================================================
            Header
        ================================================== */}

        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-emerald-50 p-3">
              <Activity className="h-7 w-7 text-emerald-600" />
            </div>

            <div>

              <h1 className="text-3xl font-bold text-slate-900">
                Continuous Monitoring
              </h1>

              <p className="mt-1 text-slate-500">
                Deterministic monitoring of current GRC risk and remediation conditions.
              </p>

            </div>

          </div>


          <div className="flex items-center gap-3">

            <span className="hidden text-xs text-slate-400 sm:inline">
              Updated {formatDateTime(data.generated_at)}
            </span>

            <button
              type="button"
              onClick={() => refetch()}
              disabled={isFetching}
              className="inline-flex items-center justify-center rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50 disabled:opacity-50"
            >
              <RefreshCw
                className={`mr-2 h-4 w-4 ${
                  isFetching
                    ? "animate-spin"
                    : ""
                }`}
              />
              Refresh
            </button>

          </div>

        </div>


        {/* ==================================================
            Alert Summary
        ================================================== */}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <MetricCard
            title="Total Alerts"
            value={metrics.total_alerts}
            icon={AlertCircle}
          />

          <MetricCard
            title="Critical Alerts"
            value={metrics.critical_alerts}
            icon={ShieldAlert}
            emphasis="critical"
          />

          <MetricCard
            title="High Alerts"
            value={metrics.high_alerts}
            icon={AlertTriangle}
          />

          <MetricCard
            title="Medium Alerts"
            value={metrics.medium_alerts}
            icon={Clock}
          />

        </div>


        {/* ==================================================
            Monitoring Conditions
        ================================================== */}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <MetricCard
            title="Critical Risks"
            value={metrics.critical_risks}
            icon={ShieldAlert}
            emphasis="critical"
          />

          <MetricCard
            title="Risks Without Controls"
            value={metrics.risks_without_controls}
            icon={ShieldCheck}
          />

          <MetricCard
            title="Controls Without Evidence"
            value={metrics.controls_without_evidence}
            icon={FileWarning}
          />

          <MetricCard
            title="Ineffective Controls"
            value={metrics.ineffective_controls}
            icon={XCircle}
          />

          <MetricCard
            title="Critical Findings"
            value={metrics.critical_findings}
            icon={AlertTriangle}
          />

          <MetricCard
            title="Open Findings"
            value={metrics.open_findings}
            icon={Activity}
          />

          <MetricCard
            title="Overdue Actions"
            value={metrics.overdue_actions}
            icon={Clock}
            emphasis="critical"
          />

          <MetricCard
            title="Stale Evidence"
            value={metrics.stale_evidence}
            icon={FileWarning}
          />

        </div>


        {/* ==================================================
            Continuous Risk State
        ================================================== */}

        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">

          <MetricCard
            title="Degraded Risks"
            value={metrics.degraded_risks}
            icon={AlertTriangle}
            emphasis={
              metrics.degraded_risks > 0
                ? "critical"
                : undefined
            }
          />

          <MetricCard
            title="Reassessment Required"
            value={metrics.reassessment_required_risks}
            icon={ShieldAlert}
            emphasis={
              metrics.reassessment_required_risks > 0
                ? "critical"
                : undefined
            }
          />

          <MetricCard
            title="Treatment Alerts"
            value={metrics.treatment_alerts}
            icon={RefreshCw}
          />

          <MetricCard
            title="Elevated Residual Risk"
            value={metrics.elevated_residual_risks}
            icon={ShieldAlert}
            emphasis={
              metrics.elevated_residual_risks > 0
                ? "critical"
                : undefined
            }
          />

        </div>


        {/* ==================================================
            Phase 57 — Response Summary
        ================================================== */}

        <div className="grid gap-4 sm:grid-cols-3">

          <MetricCard
            title="Response Required"
            value={metrics.response_required_risks}
            icon={AlertTriangle}
            emphasis={
              metrics.response_required_risks > 0
                ? "critical"
                : undefined
            }
          />

          <MetricCard
            title="Human Approval Required"
            value={metrics.human_approval_required_risks}
            icon={UserCheck}
            emphasis={
              metrics.human_approval_required_risks > 0
                ? "critical"
                : undefined
            }
          />

          <MetricCard
            title="Critical Responses"
            value={metrics.critical_response_risks}
            icon={ShieldAlert}
            emphasis={
              metrics.critical_response_risks > 0
                ? "critical"
                : undefined
            }
          />

        </div>


        {/* ==================================================
            Continuous Risk State Explanation
        ================================================== */}

        <div className="rounded-2xl border bg-slate-50 p-6">

          <div className="flex items-start gap-3">

            <div className="rounded-lg bg-white p-2 shadow-sm">
              <Activity className="h-5 w-5 text-emerald-600" />
            </div>

            <div>

              <h2 className="font-semibold text-slate-900">
                Continuous Risk State
              </h2>

              <p className="mt-1 max-w-4xl text-sm leading-6 text-slate-600">
                Risk state is continuously derived from the current treatment,
                control, evidence, finding, and remediation conditions.
                A degraded state indicates that the current risk posture has
                changed, while reassessment required indicates that the existing
                treatment assessment should be reviewed.
              </p>

            </div>

          </div>

        </div>


        {/* ==================================================
            Phase 57 — Response Posture
        ================================================== */}

        <div className="rounded-2xl border bg-white shadow-sm">

          <div className="border-b p-6">

            <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

              <div className="flex items-start gap-3">

                <div className="rounded-lg bg-red-50 p-2">
                  <ShieldAlert className="h-5 w-5 text-red-600" />
                </div>

                <div>

                  <h2 className="text-lg font-semibold text-slate-900">
                    Response Posture
                  </h2>

                  <p className="mt-1 max-w-3xl text-sm leading-6 text-slate-500">
                    Deterministic response recommendations derived from the
                    current continuous risk state. High-impact decisions remain
                    subject to human approval.
                  </p>

                </div>

              </div>

              <span
                className={`rounded-full px-3 py-1 text-xs font-semibold ${
                  responseRisks.length > 0
                    ? "bg-red-100 text-red-700"
                    : "bg-emerald-100 text-emerald-700"
                }`}
              >
                {responseRisks.length} response
                {responseRisks.length === 1
                  ? ""
                  : "s"} required
              </span>

            </div>

          </div>


          <div className="divide-y">

            {responseRisks.length === 0 ? (

              <div className="p-10 text-center">

                <CheckCircle2 className="mx-auto h-8 w-8 text-emerald-500" />

                <p className="mt-3 font-medium text-slate-700">
                  No active response requirements
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  All visible risks currently have a monitor-only response posture.
                </p>

              </div>

            ) : (

              responseRisks.map(
                (response) => {

                  const primaryDecision =
                    response.decisions[0];

                  return (
                    <div
                      key={response.risk_id}
                      className="p-6 transition hover:bg-slate-50"
                    >

                      <div className="flex flex-col gap-5 lg:flex-row lg:items-start lg:justify-between">

                        <div className="min-w-0">

                          <div className="flex flex-wrap items-center gap-2">

                            <h3 className="font-semibold text-slate-900">
                              Risk #{response.risk_id}
                            </h3>

                            <span
                              className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${stateClass(
                                response.risk_state
                              )}`}
                            >
                              {formatLabel(
                                response.risk_state
                              )}
                            </span>

                            <span
                              className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${stateClass(
                                response.treatment_state
                              )}`}
                            >
                              Treatment:{" "}
                              {formatLabel(
                                response.treatment_state
                              )}
                            </span>

                          </div>


                          <div className="mt-4 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">

                            <ResponseDetail
                              label="Priority"
                              value={formatLabel(
                                response.priority
                              )}
                              className={priorityClass(
                                response.priority
                              )}
                            />

                            <ResponseDetail
                              label="Response Required"
                              value={
                                response.response_required
                                  ? "Yes"
                                  : "No"
                              }
                              className={
                                response.response_required
                                  ? "bg-red-100 text-red-700 border-red-200"
                                  : "bg-emerald-100 text-emerald-700 border-emerald-200"
                              }
                            />

                            <ResponseDetail
                              label="Reassessment"
                              value={
                                response.reassessment_required
                                  ? "Required"
                                  : "Not Required"
                              }
                              className={
                                response.reassessment_required
                                  ? "bg-red-100 text-red-700 border-red-200"
                                  : "bg-slate-100 text-slate-700 border-slate-200"
                              }
                            />

                            <ResponseDetail
                              label="Human Approval"
                              value={
                                response.human_approval_required
                                  ? "Required"
                                  : "Not Required"
                              }
                              className={
                                response.human_approval_required
                                  ? "bg-red-100 text-red-700 border-red-200"
                                  : "bg-emerald-100 text-emerald-700 border-emerald-200"
                              }
                            />

                          </div>


                          <div className="mt-5">

                            <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                              Recommended Decision
                            </p>

                            <div className="mt-2 flex flex-wrap items-center gap-2">

                              {primaryDecision ? (
                                <span
                                  className={`rounded-lg border px-3 py-2 text-sm font-semibold ${priorityClass(
                                    primaryDecision.priority
                                  )}`}
                                >
                                  {formatLabel(
                                    primaryDecision.decision
                                  )}
                                </span>
                              ) : (
                                <span className="text-sm text-slate-500">
                                  No decision recorded
                                </span>
                              )}

                            </div>

                          </div>


                          {response.decisions.length > 1 && (

                            <div className="mt-4">

                              <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                                Additional Decisions
                              </p>

                              <div className="mt-2 flex flex-wrap gap-2">

                                {response.decisions
                                  .slice(1)
                                  .map(
                                    (decision) => (
                                      <span
                                        key={`${decision.decision}-${decision.priority}-${decision.reason_codes.join(
                                          "-"
                                        )}`}
                                        className="rounded-lg border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-medium text-slate-700"
                                      >
                                        {formatLabel(
                                          decision.decision
                                        )}
                                      </span>
                                    )
                                  )}

                              </div>

                            </div>

                          )}


                          {primaryDecision &&
                            primaryDecision.reason_codes.length > 0 && (

                              <div className="mt-4">

                                <p className="text-xs font-semibold uppercase tracking-wide text-slate-400">
                                  Response Drivers
                                </p>

                                <div className="mt-2 flex flex-wrap gap-2">

                                  {primaryDecision.reason_codes.map(
                                    (reasonCode) => (
                                      <span
                                        key={reasonCode}
                                        className="rounded-full border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-medium text-slate-600"
                                      >
                                        {formatLabel(
                                          reasonCode
                                        )}
                                      </span>
                                    )
                                  )}

                                </div>

                              </div>

                            )}

                        </div>


                        <div className="flex shrink-0 flex-col gap-3 lg:items-end">

                          {response.human_approval_required && (

                            <div className="inline-flex items-center rounded-lg border border-red-200 bg-red-50 px-3 py-2 text-xs font-semibold text-red-700">

                              <UserCheck className="mr-2 h-4 w-4" />

                              Human approval required

                            </div>

                          )}

                          <button
                            type="button"
                            onClick={() =>
                              navigate(
                                `/risks/${response.risk_id}`
                              )
                            }
                            className="inline-flex items-center justify-center rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm transition hover:bg-slate-50"
                          >
                            View Risk
                            <ArrowRight className="ml-2 h-4 w-4" />
                          </button>

                        </div>

                      </div>

                    </div>
                  );
                }
              )

            )}

          </div>

        </div>


        {/* ==================================================
            Explanation
        ================================================== */}

        <div className="rounded-2xl border bg-slate-50 p-6">

          <div className="flex items-start gap-3">

            <div className="rounded-lg bg-white p-2 shadow-sm">
              <Activity className="h-5 w-5 text-emerald-600" />
            </div>

            <div>

              <h2 className="font-semibold text-slate-900">
                Deterministic GRC Monitoring
              </h2>

              <p className="mt-1 max-w-4xl text-sm leading-6 text-slate-600">
                Monitoring alerts and response recommendations are calculated
                from the current database state rather than generated by an AI
                model. This provides predictable detection of critical risks,
                missing controls, evidence gaps, ineffective controls, findings,
                remediation issues, stale evidence, and response requirements.
              </p>

            </div>

          </div>

        </div>


        {/* ==================================================
            Alerts
        ================================================== */}

        <div className="rounded-2xl border bg-white shadow-sm">

          <div className="border-b p-6">

            <div className="flex items-center justify-between">

              <div>

                <h2 className="text-lg font-semibold text-slate-900">
                  Active Monitoring Alerts
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Current alerts visible within your authorization scope.
                </p>

              </div>

              <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-600">
                {data.alerts.length} alerts
              </span>

            </div>

          </div>


          <div className="divide-y">

            {data.alerts.length === 0 ? (

              <div className="p-10 text-center">

                <CheckCircle2 className="mx-auto h-8 w-8 text-emerald-500" />

                <p className="mt-3 font-medium text-slate-700">
                  No active monitoring alerts
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  No monitored GRC conditions currently require attention.
                </p>

              </div>

            ) : (

              data.alerts.map(
                (alert, index) => {

                  const path =
                    resourcePath(
                      alert.resource_type,
                      alert.resource_id
                    );

                  return (
                    <div
                      key={`${alert.alert_type}-${alert.resource_type}-${alert.resource_id}-${index}`}
                      className="flex flex-col gap-4 p-6 transition hover:bg-slate-50 lg:flex-row lg:items-center lg:justify-between"
                    >

                      <div className="flex min-w-0 items-start gap-4">

                        <div className="mt-0.5 rounded-lg bg-slate-100 p-2">

                          <AlertTriangle className="h-5 w-5 text-slate-600" />

                        </div>

                        <div className="min-w-0">

                          <div className="flex flex-wrap items-center gap-2">

                            <h3 className="font-semibold text-slate-900">
                              {alert.title}
                            </h3>

                            <span
                              className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${severityClass(
                                alert.severity
                              )}`}
                            >
                              {alert.severity}
                            </span>

                          </div>

                          <p className="mt-1 text-sm leading-6 text-slate-600">
                            {alert.message}
                          </p>

                          <p className="mt-2 text-xs text-slate-400">
                            {alert.resource_type} #{alert.resource_id}
                            {" · "}
                            Detected {formatDateTime(alert.detected_at)}
                          </p>

                        </div>

                      </div>


                      {path && (

                        <button
                          type="button"
                          onClick={() =>
                            navigate(path)
                          }
                          className="inline-flex shrink-0 items-center self-start rounded-lg border border-slate-200 bg-white px-3 py-2 text-xs font-medium text-slate-700 transition hover:bg-slate-50 lg:self-center"
                        >
                          View Resource
                          <ArrowRight className="ml-2 h-4 w-4" />
                        </button>

                      )}

                    </div>
                  );
                }
              )

            )}

          </div>

        </div>

      </div>

    </AppLayout>
  );
}


// ==========================================================
// Response Detail
// ==========================================================

interface ResponseDetailProps {
  label: string;
  value: string;
  className: string;
}


function ResponseDetail({
  label,
  value,
  className,
}: ResponseDetailProps) {

  return (
    <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">

      <p className="text-xs font-medium text-slate-500">
        {label}
      </p>

      <span
        className={`mt-2 inline-flex rounded-full border px-2.5 py-1 text-xs font-semibold ${className}`}
      >
        {value}
      </span>

    </div>
  );
}


// ==========================================================
// Metric Card
// ==========================================================

interface MetricCardProps {
  title: string;
  value: number;
  icon: React.ComponentType<{
    className?: string;
  }>;
  emphasis?: "critical";
}


function MetricCard({
  title,
  value,
  icon: Icon,
  emphasis,
}: MetricCardProps) {

  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">

      <div className="flex items-start justify-between">

        <div>

          <p className="text-sm font-medium text-slate-500">
            {title}
          </p>

          <p
            className={`mt-2 text-2xl font-bold ${
              emphasis === "critical"
                ? "text-red-600"
                : "text-slate-900"
            }`}
          >
            {value}
          </p>

        </div>

        <div className="rounded-lg bg-slate-100 p-2">
          <Icon className="h-5 w-5 text-slate-600" />
        </div>

      </div>

    </div>
  );
}