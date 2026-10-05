import {
  AlertTriangle,
  CheckCircle2,
  FileCheck2,
  ShieldAlert,
  Workflow,
} from "lucide-react";

import type {
  EvidenceIntelligence as EvidenceIntelligenceData,
} from "@/api/evidence";


interface Props {
  intelligence: EvidenceIntelligenceData;
}


function getScoreClass(
  score: number
) {
  if (score >= 80) {
    return "text-green-600";
  }

  if (score >= 60) {
    return "text-amber-600";
  }

  return "text-red-600";
}


function getPriorityClass(
  priority: string
) {
  switch (
    priority.toUpperCase()
  ) {
    case "CRITICAL":
      return "bg-red-100 text-red-700";

    case "HIGH":
      return "bg-orange-100 text-orange-700";

    case "MEDIUM":
      return "bg-amber-100 text-amber-700";

    default:
      return "bg-slate-100 text-slate-700";
  }
}


export default function EvidenceIntelligence({
  intelligence,
}: Props) {
  const coverage =
    intelligence.coverage;

  return (
    <div className="space-y-6">

      {/* =====================================================
          Summary
      ===================================================== */}

      <div>
        <h2 className="text-2xl font-bold">
          Evidence Intelligence
        </h2>

        <p className="mt-1 text-sm text-slate-500">
          Continuous analysis of evidence freshness,
          completeness, quality and GRC coverage.
        </p>
      </div>


      {/* =====================================================
          Metrics
      ===================================================== */}

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-5">

        <div className="rounded-2xl border bg-white p-5">
          <p className="text-sm text-slate-500">
            Evidence Coverage
          </p>

          <p className="mt-2 text-3xl font-bold">
            {coverage.coverage_percent.toFixed(1)}%
          </p>

          <p className="mt-1 text-xs text-slate-400">
            {coverage.controls_with_evidence}
            {" / "}
            {coverage.total_controls}
            {" controls"}
          </p>
        </div>


        <div className="rounded-2xl border bg-white p-5">
          <p className="text-sm text-slate-500">
            Fresh Evidence
          </p>

          <p className="mt-2 text-3xl font-bold text-green-600">
            {coverage.fresh_evidence}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Current evidence
          </p>
        </div>


        <div className="rounded-2xl border bg-white p-5">
          <p className="text-sm text-slate-500">
            Stale Evidence
          </p>

          <p className="mt-2 text-3xl font-bold text-red-600">
            {coverage.stale_evidence}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Requires review
          </p>
        </div>


        <div className="rounded-2xl border bg-white p-5">
          <p className="text-sm text-slate-500">
            Average Quality
          </p>

          <p
            className={`mt-2 text-3xl font-bold ${getScoreClass(
              coverage.average_quality_score
            )}`}
          >
            {coverage.average_quality_score.toFixed(1)}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            Out of 100
          </p>
        </div>


        <div className="rounded-2xl border bg-white p-5">
          <p className="text-sm text-slate-500">
            Audit Readiness
          </p>

          <p
            className={`mt-2 text-3xl font-bold ${getScoreClass(
              coverage.audit_readiness_score
            )}`}
          >
            {coverage.audit_readiness_score.toFixed(1)}
          </p>

          <p className="mt-1 text-xs text-slate-400">
            {coverage.audit_ready
              ? "Audit-ready"
              : "Attention required"}
          </p>
        </div>

      </div>


      {/* =====================================================
          Freshness / Coverage
      ===================================================== */}

      <div className="grid gap-6 lg:grid-cols-2">

        <div className="rounded-2xl border bg-white p-6">

          <div className="mb-5 flex items-center gap-3">

            <div className="rounded-xl bg-blue-100 p-3">
              <FileCheck2 className="h-5 w-5 text-blue-600" />
            </div>

            <div>
              <h3 className="font-semibold">
                Evidence Health
              </h3>

              <p className="text-sm text-slate-500">
                Freshness and completeness
              </p>
            </div>

          </div>


          <div className="space-y-4">

            <div className="flex items-center justify-between">
              <span className="text-sm">
                Fresh
              </span>

              <span className="font-semibold text-green-600">
                {coverage.fresh_evidence}
              </span>
            </div>


            <div className="flex items-center justify-between">
              <span className="text-sm">
                Ageing
              </span>

              <span className="font-semibold text-amber-600">
                {coverage.aging_evidence}
              </span>
            </div>


            <div className="flex items-center justify-between">
              <span className="text-sm">
                Stale
              </span>

              <span className="font-semibold text-red-600">
                {coverage.stale_evidence}
              </span>
            </div>


            <div className="flex items-center justify-between">
              <span className="text-sm">
                Average completeness
              </span>

              <span
                className={`font-semibold ${getScoreClass(
                  coverage.average_completeness_score
                )}`}
              >
                {coverage.average_completeness_score.toFixed(1)}
              </span>
            </div>

          </div>

        </div>


        <div className="rounded-2xl border bg-white p-6">

          <div className="mb-5 flex items-center gap-3">

            <div className="rounded-xl bg-purple-100 p-3">
              <ShieldAlert className="h-5 w-5 text-purple-600" />
            </div>

            <div>
              <h3 className="font-semibold">
                Risk Traceability
              </h3>

              <p className="text-sm text-slate-500">
                Evidence connected to risk records
              </p>
            </div>

          </div>


          <div className="space-y-4">

            <div className="flex items-center justify-between">
              <span className="text-sm">
                Total evidence
              </span>

              <span className="font-semibold">
                {coverage.total_evidence}
              </span>
            </div>


            <div className="flex items-center justify-between">
              <span className="text-sm">
                Risk-mapped evidence
              </span>

              <span className="font-semibold">
                {coverage.risk_mapped_evidence}
              </span>
            </div>


            <div className="flex items-center justify-between">
              <span className="text-sm">
                Controls without evidence
              </span>

              <span className="font-semibold text-red-600">
                {coverage.controls_without_evidence}
              </span>
            </div>

          </div>

        </div>

      </div>


      {/* =====================================================
          Missing Evidence
      ===================================================== */}

      <div className="rounded-2xl border bg-white">

        <div className="border-b p-6">

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-red-100 p-3">
              <AlertTriangle className="h-5 w-5 text-red-600" />
            </div>

            <div>
              <h3 className="font-semibold">
                Missing Evidence
              </h3>

              <p className="text-sm text-slate-500">
                Controls requiring evidence collection
              </p>
            </div>

          </div>

        </div>


        {intelligence.missing_evidence.length === 0 ? (

          <div className="flex items-center gap-3 p-6 text-green-600">

            <CheckCircle2 className="h-5 w-5" />

            <span className="font-medium">
              All visible controls have supporting evidence.
            </span>

          </div>

        ) : (

          <div className="divide-y">

            {intelligence.missing_evidence
              .slice(0, 10)
              .map((item) => (

                <div
                  key={item.control_id}
                  className="flex flex-col gap-3 p-5 md:flex-row md:items-center md:justify-between"
                >

                  <div>
                    <p className="font-medium">
                      {item.control_title}
                    </p>

                    <p className="mt-1 text-sm text-slate-500">
                      {item.reason}
                    </p>

                    <p className="mt-1 text-sm text-slate-600">
                      {item.recommended_action}
                    </p>
                  </div>


                  <span
                    className={`w-fit rounded-full px-3 py-1 text-xs font-semibold ${getPriorityClass(
                      item.priority
                    )}`}
                  >
                    {item.priority}
                  </span>

                </div>

              ))}

          </div>

        )}

      </div>


      {/* =====================================================
          Collection Workflows
      ===================================================== */}

      <div className="rounded-2xl border bg-white">

        <div className="border-b p-6">

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-indigo-100 p-3">
              <Workflow className="h-5 w-5 text-indigo-600" />
            </div>

            <div>
              <h3 className="font-semibold">
                Evidence Collection Workflows
              </h3>

              <p className="text-sm text-slate-500">
                Governed recommendations for evidence collection
              </p>
            </div>

          </div>

        </div>


        {intelligence.collection_workflows.length === 0 ? (

          <div className="p-6 text-sm text-green-600">
            No evidence collection workflows are currently required.
          </div>

        ) : (

          <div className="divide-y">

            {intelligence.collection_workflows
              .slice(0, 10)
              .map((workflow) => (

                <div
                  key={workflow.control_id}
                  className="flex flex-col gap-2 p-5 md:flex-row md:items-center md:justify-between"
                >

                  <div>
                    <p className="font-medium">
                      {workflow.control_title}
                    </p>

                    <p className="text-sm text-slate-500">
                      {workflow.recommended_action}
                    </p>
                  </div>

                  <span
                    className={`w-fit rounded-full px-3 py-1 text-xs font-semibold ${getPriorityClass(
                      workflow.priority
                    )}`}
                  >
                    {workflow.priority}
                  </span>

                </div>

              ))}

          </div>

        )}

      </div>

    </div>
  );
}