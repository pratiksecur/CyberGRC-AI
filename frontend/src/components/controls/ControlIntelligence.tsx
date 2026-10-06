import {
  AlertTriangle,
  CheckCircle2,
  ShieldAlert,
  ShieldCheck,
  Activity,
  FileWarning,
  RefreshCw,
} from "lucide-react";

import type {
  ControlIntelligenceResponse,
} from "@/api/controls";


interface Props {
  intelligence:
    ControlIntelligenceResponse;
}


function postureClass(
  posture: string
) {
  if (posture === "CRITICAL") {
    return "bg-red-100 text-red-700";
  }

  if (posture === "DEGRADED") {
    return "bg-amber-100 text-amber-700";
  }

  return "bg-emerald-100 text-emerald-700";
}


function healthClass(
  state: string
) {
  if (state === "CRITICAL") {
    return "bg-red-100 text-red-700";
  }

  if (state === "DEGRADED") {
    return "bg-amber-100 text-amber-700";
  }

  return "bg-emerald-100 text-emerald-700";
}


export default function ControlIntelligence({
  intelligence,
}: Props) {

  const {
    summary,
    controls,
  } = intelligence;

  return (
    <div className="space-y-6">

      {/* ================================================= */}
      {/* HEADER */}
      {/* ================================================= */}

      <div className="rounded-2xl border bg-white p-6 shadow-sm">

        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

          <div>

            <div className="flex items-center gap-2">

              <Activity
                size={22}
                className="text-blue-600"
              />

              <h2 className="text-xl font-semibold">
                Control Intelligence
              </h2>

            </div>

            <p className="mt-1 text-sm text-slate-500">
              Continuous monitoring of control
              effectiveness, evidence, risk exposure
              and remediation signals.
            </p>

          </div>

          <span
            className={`rounded-full px-4 py-2 text-sm font-semibold ${postureClass(
              summary.overall_posture
            )}`}
          >
            {summary.overall_posture}
          </span>

        </div>

      </div>


      {/* ================================================= */}
      {/* SUMMARY CARDS */}
      {/* ================================================= */}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">

        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <div className="flex items-center justify-between">

            <div>

              <p className="text-sm text-slate-500">
                Average Effectiveness
              </p>

              <p className="mt-2 text-3xl font-bold">
                {summary.average_effectiveness}%
              </p>

            </div>

            <ShieldCheck
              className="text-emerald-600"
              size={28}
            />

          </div>

        </div>


        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <div className="flex items-center justify-between">

            <div>

              <p className="text-sm text-slate-500">
                Control Health
              </p>

              <p className="mt-2 text-3xl font-bold">
                {summary.average_health_score}
              </p>

            </div>

            <Activity
              className="text-blue-600"
              size={28}
            />

          </div>

        </div>


        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <div className="flex items-center justify-between">

            <div>

              <p className="text-sm text-slate-500">
                Evidence Coverage
              </p>

              <p className="mt-2 text-3xl font-bold">
                {summary.evidence_coverage_percent}%
              </p>

            </div>

            <FileWarning
              className="text-amber-600"
              size={28}
            />

          </div>

        </div>


        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <div className="flex items-center justify-between">

            <div>

              <p className="text-sm text-slate-500">
                Remediation Required
              </p>

              <p className="mt-2 text-3xl font-bold">
                {summary.remediation_required}
              </p>

            </div>

            <RefreshCw
              className="text-red-600"
              size={28}
            />

          </div>

        </div>

      </div>


      {/* ================================================= */}
      {/* HEALTH DISTRIBUTION */}
      {/* ================================================= */}

      <div className="grid gap-4 md:grid-cols-3">

        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <div className="flex items-center gap-3">

            <CheckCircle2
              className="text-emerald-600"
              size={22}
            />

            <div>

              <p className="text-sm text-slate-500">
                Healthy Controls
              </p>

              <p className="text-2xl font-bold">
                {summary.healthy_controls}
              </p>

            </div>

          </div>

        </div>


        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <div className="flex items-center gap-3">

            <AlertTriangle
              className="text-amber-600"
              size={22}
            />

            <div>

              <p className="text-sm text-slate-500">
                Degraded Controls
              </p>

              <p className="text-2xl font-bold">
                {summary.degraded_controls}
              </p>

            </div>

          </div>

        </div>


        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <div className="flex items-center gap-3">

            <ShieldAlert
              className="text-red-600"
              size={22}
            />

            <div>

              <p className="text-sm text-slate-500">
                Critical Controls
              </p>

              <p className="text-2xl font-bold">
                {summary.critical_controls}
              </p>

            </div>

          </div>

        </div>

      </div>


      {/* ================================================= */}
      {/* COVERAGE */}
      {/* ================================================= */}

      <div className="grid gap-4 md:grid-cols-3">

        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <p className="text-sm text-slate-500">
            Evidence Coverage
          </p>

          <p className="mt-2 text-2xl font-bold">
            {summary.evidence_coverage_percent}%
          </p>

          <p className="mt-1 text-xs text-slate-400">
            {summary.controls_without_evidence}
            {" "}
            controls without evidence
          </p>

        </div>


        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <p className="text-sm text-slate-500">
            Framework Coverage
          </p>

          <p className="mt-2 text-2xl font-bold">
            {summary.framework_coverage_percent}%
          </p>

          <p className="mt-1 text-xs text-slate-400">
            {summary.framework_mapped_controls}
            {" "}
            controls mapped
          </p>

        </div>


        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <p className="text-sm text-slate-500">
            Risk Coverage
          </p>

          <p className="mt-2 text-2xl font-bold">
            {summary.risk_coverage_percent}%
          </p>

          <p className="mt-1 text-xs text-slate-400">
            {summary.risk_mapped_controls}
            {" "}
            controls mapped to risks
          </p>

        </div>

      </div>


      {/* ================================================= */}
      {/* CONTROL INTELLIGENCE TABLE */}
      {/* ================================================= */}

      <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">

        <div className="border-b p-5">

          <h3 className="text-lg font-semibold">
            Continuous Control Monitoring
          </h3>

          <p className="text-sm text-slate-500">
            Highest-priority control health signals.
          </p>

        </div>


        <div className="overflow-x-auto">

          <table className="min-w-full">

            <thead className="border-b bg-slate-50">

              <tr>

                <th className="px-5 py-4 text-left text-sm font-semibold">
                  Control
                </th>

                <th className="px-5 py-4 text-left text-sm font-semibold">
                  Health
                </th>

                <th className="px-5 py-4 text-left text-sm font-semibold">
                  Effectiveness
                </th>

                <th className="px-5 py-4 text-left text-sm font-semibold">
                  Evidence
                </th>

                <th className="px-5 py-4 text-left text-sm font-semibold">
                  Risks
                </th>

                <th className="px-5 py-4 text-left text-sm font-semibold">
                  Signals
                </th>

                <th className="px-5 py-4 text-left text-sm font-semibold">
                  Action
                </th>

              </tr>

            </thead>


            <tbody>

              {controls.length === 0 ? (

                <tr>

                  <td
                    colSpan={7}
                    className="py-10 text-center text-slate-500"
                  >
                    No control intelligence is
                    available.
                  </td>

                </tr>

              ) : (

                controls.map((control) => (

                  <tr
                    key={control.control_id}
                    className="border-b hover:bg-slate-50"
                  >

                    <td className="px-5 py-5">

                      <div className="font-medium">
                        {control.title}
                      </div>

                      <div className="text-xs text-slate-500">
                        {control.control_type}
                      </div>

                    </td>


                    <td className="px-5 py-5">

                      <span
                        className={`rounded-full px-3 py-1 text-xs font-semibold ${healthClass(
                          control.health_state
                        )}`}
                      >
                        {control.health_state}
                      </span>

                      <div className="mt-1 text-xs text-slate-400">
                        Score {control.health_score}
                      </div>

                    </td>


                    <td className="px-5 py-5">

                      <div className="font-semibold">
                        {control.effectiveness}%
                      </div>

                      <div className="text-xs text-slate-400">
                        {control.effectiveness_trend_signal}
                      </div>

                    </td>


                    <td className="px-5 py-5">

                      <div>
                        {control.evidence_count}
                        {" "}
                        total
                      </div>

                      <div className="text-xs text-slate-400">
                        {control.fresh_evidence}
                        {" "}
                        fresh /{" "}
                        {control.stale_evidence}
                        {" "}
                        stale
                      </div>

                    </td>


                    <td className="px-5 py-5">

                      <div>
                        {control.risk_count}
                        {" "}
                        risks
                      </div>

                      <div className="text-xs text-slate-400">
                        {control.critical_risk_count}
                        {" "}
                        critical
                      </div>

                    </td>


                    <td className="px-5 py-5">

                      {control.monitoring_signals.length === 0 ? (

                        <span className="text-xs text-emerald-600">
                          No active exceptions
                        </span>

                      ) : (

                        <div className="flex flex-wrap gap-1">

                          {control.monitoring_signals
                            .slice(0, 3)
                            .map((signal) => (

                              <span
                                key={signal}
                                className="rounded-full bg-red-50 px-2 py-1 text-[11px] text-red-700"
                              >
                                {signal}
                              </span>

                            ))}

                        </div>

                      )}

                    </td>


                    <td className="max-w-xs px-5 py-5 text-sm text-slate-600">

                      {control.recommended_action}

                    </td>

                  </tr>

                ))

              )}

            </tbody>

          </table>

        </div>

      </div>

    </div>
  );
}