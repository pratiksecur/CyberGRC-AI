import {
  AlertTriangle,
  BarChart3,
  CheckCircle2,
  ClipboardCheck,
  FileWarning,
  Gauge,
  GitBranch,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";

import type { ExecutiveIntelligence } from "@/api/executiveIntelligence";
import { useExecutiveIntelligence } from "@/hooks/useExecutiveIntelligence";

interface Props {
  intelligence?: ExecutiveIntelligence;
  isLoading?: boolean;
  error?: unknown;
}

function postureClass(level: string) {
  switch (level.toUpperCase()) {
    case "CRITICAL":
      return "text-red-600";

    case "HIGH":
      return "text-orange-600";

    case "WEAK":
      return "text-red-600";

    case "MODERATE":
      return "text-yellow-600";

    case "STRONG":
    case "LOW":
      return "text-green-600";

    default:
      return "text-slate-600";
  }
}

function MetricCard({
  icon: Icon,
  label,
  value,
  detail,
}: {
  icon: typeof ShieldAlert;
  label: string;
  value: string | number;
  detail: string;
}) {
  return (
    <div className="rounded-xl border bg-white p-5 shadow-sm">
      <div className="flex items-center justify-between">
        <div className="rounded-lg bg-slate-100 p-2">
          <Icon className="h-5 w-5 text-slate-700" />
        </div>
      </div>

      <div className="mt-4">
        <p className="text-sm text-slate-500">
          {label}
        </p>

        <p className="mt-1 text-2xl font-semibold text-slate-900">
          {value}
        </p>

        <p className="mt-1 text-xs text-slate-500">
          {detail}
        </p>
      </div>
    </div>
  );
}

export default function ExecutiveIntelligence({
  intelligence: suppliedIntelligence,
  isLoading: suppliedLoading,
  error: suppliedError,
}: Props) {
  const query = useExecutiveIntelligence();

  const intelligence =
    suppliedIntelligence ?? query.data;

  const isLoading =
    suppliedLoading ?? query.isLoading;

  const error =
    suppliedError ?? query.error;

  if (isLoading) {
    return (
      <section className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="animate-pulse space-y-4">
          <div className="h-6 w-64 rounded bg-slate-200" />
          <div className="h-4 w-96 rounded bg-slate-200" />
          <div className="grid gap-4 md:grid-cols-4">
            <div className="h-28 rounded bg-slate-200" />
            <div className="h-28 rounded bg-slate-200" />
            <div className="h-28 rounded bg-slate-200" />
            <div className="h-28 rounded bg-slate-200" />
          </div>
        </div>
      </section>
    );
  }

  if (error || !intelligence) {
    return (
      <section className="rounded-xl border bg-white p-6 shadow-sm">
        <div className="flex items-center gap-3">
          <AlertTriangle className="h-5 w-5 text-orange-500" />

          <div>
            <h2 className="font-semibold text-slate-900">
              Executive intelligence unavailable
            </h2>

            <p className="text-sm text-slate-500">
              Deterministic executive metrics could not be loaded.
            </p>
          </div>
        </div>
      </section>
    );
  }

  const risk = intelligence.risk_posture;
  const compliance =
    intelligence.compliance_posture;
  const controls =
    intelligence.control_health;
  const findings =
    intelligence.findings;
  const remediation =
    intelligence.remediation;
  const treatment =
    intelligence.treatment_effectiveness;
  const workflows =
    intelligence.workflow_health;

  return (
    <section className="space-y-6">
      <div>
        <div className="flex items-center gap-2">
          <Gauge className="h-6 w-6 text-indigo-600" />

          <h2 className="text-xl font-semibold text-slate-900">
            Executive Risk & Compliance Intelligence
          </h2>
        </div>

        <p className="mt-1 text-sm text-slate-500">
          Deterministic enterprise posture derived from the visible GRC state.
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <MetricCard
          icon={ShieldAlert}
          label="Risk posture"
          value={risk.level}
          detail={`${risk.critical} critical · ${risk.high} high`}
        />

        <MetricCard
          icon={ShieldCheck}
          label="Compliance posture"
          value={compliance.level}
          detail={`${compliance.score}% control effectiveness`}
        />

        <MetricCard
          icon={BarChart3}
          label="Control health"
          value={`${controls.average_effectiveness}%`}
          detail={`${controls.ineffective} ineffective · ${controls.degraded} degraded`}
        />

        <MetricCard
          icon={FileWarning}
          label="Critical findings"
          value={findings.critical_open}
          detail={`${findings.open} open findings`}
        />
      </div>

      <div className="grid gap-6 lg:grid-cols-3">
        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <ClipboardCheck className="h-5 w-5 text-slate-700" />

            <h3 className="font-semibold text-slate-900">
              Remediation
            </h3>
          </div>

          <div className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500">
                Open actions
              </span>

              <span className="font-medium">
                {remediation.open_actions}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-500">
                Overdue actions
              </span>

              <span className="font-medium text-orange-600">
                {remediation.overdue_actions}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-500">
                Open findings
              </span>

              <span className="font-medium">
                {findings.open}
              </span>
            </div>
          </div>
        </div>

        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <GitBranch className="h-5 w-5 text-slate-700" />

            <h3 className="font-semibold text-slate-900">
              Treatment & workflows
            </h3>
          </div>

          <div className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500">
                Active treatments
              </span>

              <span className="font-medium">
                {treatment.active}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-500">
                Overdue treatments
              </span>

              <span className="font-medium text-orange-600">
                {treatment.overdue}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-500">
                Open workflows
              </span>

              <span className="font-medium">
                {workflows.open}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-500">
                Escalated workflows
              </span>

              <span className="font-medium text-red-600">
                {workflows.escalated}
              </span>
            </div>
          </div>
        </div>

        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <div className="flex items-center gap-2">
            <CheckCircle2 className="h-5 w-5 text-slate-700" />

            <h3 className="font-semibold text-slate-900">
              Evidence coverage
            </h3>
          </div>

          <div className="mt-4 space-y-3 text-sm">
            <div className="flex justify-between">
              <span className="text-slate-500">
                Active controls
              </span>

              <span className="font-medium">
                {compliance.active_controls}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-500">
                Missing evidence
              </span>

              <span className="font-medium text-orange-600">
                {compliance.controls_without_evidence}
              </span>
            </div>

            <div className="flex justify-between">
              <span className="text-slate-500">
                Stale evidence
              </span>

              <span className="font-medium text-orange-600">
                {compliance.stale_evidence}
              </span>
            </div>
          </div>
        </div>
      </div>

      <div className="rounded-xl border bg-white p-5 shadow-sm">
        <div className="flex items-center gap-2">
          <ShieldAlert className="h-5 w-5 text-slate-700" />

          <h3 className="font-semibold text-slate-900">
            Why the posture looks this way
          </h3>
        </div>

        <div className="mt-4 space-y-3">
          {intelligence.explainability.map(
            (item) => (
              <div
                key={item.signal}
                className="rounded-lg border bg-slate-50 p-4"
              >
                <div className="flex items-center justify-between gap-4">
                  <div>
                    <p className="font-medium text-slate-900">
                      {item.signal.replaceAll(
                        "_",
                        " ",
                      )}
                    </p>

                    <p className="mt-1 text-sm text-slate-600">
                      {item.why}
                    </p>
                  </div>

                  <span
                    className={`shrink-0 text-xs font-semibold ${postureClass(
                      item.severity,
                    )}`}
                  >
                    {item.count}
                  </span>
                </div>
              </div>
            ),
          )}
        </div>
      </div>

      {intelligence.business_unit_exposure.length >
        0 && (
        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <h3 className="font-semibold text-slate-900">
            Risk exposure by owner
          </h3>

          <div className="mt-4 overflow-x-auto">
            <table className="w-full text-left text-sm">
              <thead>
                <tr className="border-b text-slate-500">
                  <th className="pb-3">
                    Owner
                  </th>

                  <th className="pb-3">
                    Risks
                  </th>

                  <th className="pb-3">
                    Critical
                  </th>

                  <th className="pb-3">
                    High
                  </th>

                  <th className="pb-3">
                    Max score
                  </th>
                </tr>
              </thead>

              <tbody>
                {intelligence.business_unit_exposure.map(
                  (item) => (
                    <tr
                      key={item.owner_id}
                      className="border-b last:border-0"
                    >
                      <td className="py-3 font-medium">
                        {item.owner_name}
                      </td>

                      <td className="py-3">
                        {item.risk_count}
                      </td>

                      <td className="py-3 text-red-600">
                        {item.critical_risks}
                      </td>

                      <td className="py-3 text-orange-600">
                        {item.high_risks}
                      </td>

                      <td className="py-3">
                        {item.max_risk_score}
                      </td>
                    </tr>
                  ),
                )}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </section>
  );
}