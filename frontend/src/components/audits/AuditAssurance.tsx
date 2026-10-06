import {
  AlertTriangle,
  CheckCircle2,
  ClipboardCheck,
  Clock3,
  FileCheck2,
  RefreshCw,
  ShieldAlert,
} from "lucide-react";

import {
  useAuditAssurance,
} from "@/hooks/useAuditAssurance";


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


function signalClass(
  severity: string,
) {
  switch (
    severity.toUpperCase()
  ) {
    case "CRITICAL":
      return (
        "border-red-200 bg-red-50 text-red-700"
      );

    case "HIGH":
      return (
        "border-orange-200 bg-orange-50 text-orange-700"
      );

    case "MEDIUM":
      return (
        "border-yellow-200 bg-yellow-50 text-yellow-700"
      );

    default:
      return (
        "border-slate-200 bg-slate-50 text-slate-700"
      );
  }
}


export default function AuditAssurance() {

  const {
    data,
    isLoading,
    error,
    refetch,
    isFetching,
  } = useAuditAssurance();


  if (isLoading) {
    return (
      <section className="rounded-xl border bg-white p-6 shadow-sm">

        <div className="animate-pulse space-y-4">

          <div className="h-6 w-72 rounded bg-slate-200" />

          <div className="h-4 w-96 rounded bg-slate-200" />

          <div className="grid gap-4 md:grid-cols-4">

            {Array.from({
              length: 8,
            }).map(
              (_, index) => (
                <div
                  key={index}
                  className="h-28 rounded bg-slate-200"
                />
              ),
            )}

          </div>

        </div>

      </section>
    );
  }


  if (error || !data) {
    return (
      <section className="rounded-xl border bg-white p-6 shadow-sm">

        <div className="flex items-center gap-3">

          <AlertTriangle className="h-5 w-5 text-orange-500" />

          <div>

            <h2 className="font-semibold text-slate-900">
              Audit assurance unavailable
            </h2>

            <p className="text-sm text-slate-500">
              Audit assurance intelligence could not be loaded.
            </p>

            <button
              type="button"
              onClick={() => refetch()}
              className="mt-3 inline-flex items-center rounded-lg border px-3 py-2 text-sm font-medium hover:bg-slate-50"
            >

              <RefreshCw className="mr-2 h-4 w-4" />

              Try Again

            </button>

          </div>

        </div>

      </section>
    );
  }


  return (
    <section className="space-y-6">

      {/* ==================================================
          Header
      ================================================== */}

      <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

        <div>

          <div className="flex items-center gap-2">

            <ClipboardCheck className="h-6 w-6 text-indigo-600" />

            <h2 className="text-xl font-semibold text-slate-900">
              Audit & Assurance Intelligence
            </h2>

          </div>

          <p className="mt-1 text-sm text-slate-500">
            Deterministic assurance intelligence across
            planning, findings, evidence, remediation,
            and closure readiness.
          </p>

        </div>


        <button
          type="button"
          onClick={() => refetch()}
          disabled={isFetching}
          className="inline-flex items-center justify-center rounded-lg border border-slate-200 bg-white px-4 py-2 text-sm font-medium text-slate-700 shadow-sm hover:bg-slate-50 disabled:opacity-50"
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


      {/* ==================================================
          Metrics
      ================================================== */}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">

        <MetricCard
          icon={ClipboardCheck}
          label="Total audits"
          value={
            data.portfolio.total_audits
          }
          detail={`${data.portfolio.completed} completed`}
        />

        <MetricCard
          icon={Clock3}
          label="Overdue audits"
          value={
            data.portfolio.overdue
          }
          detail="Past planned end date"
        />

        <MetricCard
          icon={CheckCircle2}
          label="Closure ready"
          value={
            data.portfolio.closure_ready
          }
          detail="No deterministic blockers"
        />

        <MetricCard
          icon={ShieldAlert}
          label="Blocked audits"
          value={
            data.portfolio.blocked
          }
          detail="Require attention"
        />

        <MetricCard
          icon={AlertTriangle}
          label="Open findings"
          value={
            data.testing.open_findings
          }
          detail={`${data.testing.critical_findings} critical`}
        />

        <MetricCard
          icon={Clock3}
          label="Open actions"
          value={
            data.remediation.open_actions
          }
          detail={`${data.remediation.overdue_actions} overdue`}
        />

        <MetricCard
          icon={FileCheck2}
          label="Evidence coverage"
          value={`${data.evidence.coverage_percent}%`}
          detail={`${data.evidence.controls_without_evidence} controls without evidence`}
        />

        <MetricCard
          icon={ClipboardCheck}
          label="Planning completion"
          value={`${data.planning.completion_percent}%`}
          detail={`${data.planning.incomplete} incomplete`}
        />

      </div>


      {/* ==================================================
          Assurance Signals
      ================================================== */}

      {data.assurance_signals.length > 0 && (

        <div className="rounded-xl border bg-white p-6 shadow-sm">

          <div className="mb-4">

            <h3 className="font-semibold text-slate-900">
              Assurance Signals
            </h3>

            <p className="mt-1 text-sm text-slate-500">
              Deterministic conditions requiring review.
            </p>

          </div>


          <div className="space-y-3">

            {data.assurance_signals.map(
              (signal) => (

                <div
                  key={signal.signal}
                  className={`rounded-lg border p-4 ${signalClass(
                    signal.severity,
                  )}`}
                >

                  <div className="flex items-start justify-between gap-4">

                    <div>

                      <p className="font-semibold">
                        {signal.signal.replace(
                          /_/g,
                          " ",
                        )}
                      </p>

                      <p className="mt-1 text-sm">
                        {signal.why}
                      </p>

                    </div>


                    <span className="rounded-full bg-white/70 px-2.5 py-1 text-xs font-semibold">
                      {signal.count}
                    </span>

                  </div>

                </div>

              ),
            )}

          </div>

        </div>

      )}


      {/* ==================================================
          Audit Assurance Table
      ================================================== */}

      <div className="overflow-hidden rounded-xl border bg-white shadow-sm">

        <div className="border-b p-6">

          <h3 className="font-semibold text-slate-900">
            Audit Assurance Status
          </h3>

          <p className="mt-1 text-sm text-slate-500">
            Assurance state for audits visible to the current user.
          </p>

        </div>


        <div className="overflow-x-auto">

          <table className="w-full min-w-[1100px]">

            <thead className="border-b bg-slate-50">

              <tr>

                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Audit
                </th>

                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Status
                </th>

                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Findings
                </th>

                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Evidence
                </th>

                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Remediation
                </th>

                <th className="px-6 py-4 text-left text-xs font-semibold uppercase tracking-wide text-slate-500">
                  Assurance
                </th>

              </tr>

            </thead>


            <tbody className="divide-y">

              {data.audits.map(
                (audit) => (

                  <tr
                    key={audit.id}
                    className="hover:bg-slate-50"
                  >

                    <td className="px-6 py-4">

                      <p className="font-medium text-slate-900">
                        {audit.name}
                      </p>

                      <p className="text-xs text-slate-500">
                        {audit.start_date}
                        {" → "}
                        {audit.end_date}
                      </p>

                    </td>


                    <td className="px-6 py-4">

                      <span className="rounded-full bg-slate-100 px-3 py-1 text-xs font-medium text-slate-700">
                        {audit.status}
                      </span>

                      {audit.overdue && (
                        <p className="mt-1 text-xs font-medium text-red-600">
                          Overdue
                        </p>
                      )}

                    </td>


                    <td className="px-6 py-4">

                      <p className="text-sm text-slate-700">
                        {audit.finding_count}
                        {" total"}
                      </p>

                      <p className="text-xs text-slate-500">
                        {audit.open_findings}
                        {" open"}
                      </p>

                      {audit.critical_findings > 0 && (
                        <p className="text-xs font-medium text-red-600">
                          {audit.critical_findings}
                          {" critical"}
                        </p>
                      )}

                    </td>


                    <td className="px-6 py-4">

                      <p className="text-sm text-slate-700">
                        {audit.controls_with_evidence}
                        {" / "}
                        {audit.control_count}
                      </p>

                      <p className="text-xs text-slate-500">
                        controls with evidence
                      </p>

                    </td>


                    <td className="px-6 py-4">

                      <p className="text-sm text-slate-700">
                        {audit.open_corrective_actions}
                        {" open"}
                      </p>

                      {audit.overdue_corrective_actions > 0 && (
                        <p className="text-xs font-medium text-red-600">
                          {audit.overdue_corrective_actions}
                          {" overdue"}
                        </p>
                      )}

                    </td>


                    <td className="px-6 py-4">

                      {audit.closure_ready ? (

                        <span className="inline-flex items-center rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-700">

                          <CheckCircle2 className="mr-1 h-3.5 w-3.5" />

                          Closure Ready

                        </span>

                      ) : (

                        <div>

                          <span className="inline-flex items-center rounded-full bg-orange-100 px-3 py-1 text-xs font-semibold text-orange-700">

                            <AlertTriangle className="mr-1 h-3.5 w-3.5" />

                            Attention Required

                          </span>

                          {audit.closure_blockers.length > 0 && (

                            <p className="mt-1 max-w-xs text-xs text-slate-500">
                              {audit.closure_blockers
                                .map(
                                  (blocker) =>
                                    blocker.replace(
                                      /_/g,
                                      " ",
                                    ),
                                )
                                .join(
                                  ", ",
                                )}
                            </p>

                          )}

                        </div>

                      )}

                    </td>

                  </tr>

                ),
              )}

            </tbody>

          </table>

        </div>

      </div>

    </section>
  );
}