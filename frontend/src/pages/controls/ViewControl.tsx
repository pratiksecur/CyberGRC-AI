import { type ComponentType } from "react";
import { useNavigate, useParams } from "react-router-dom";

import {
  AlertTriangle,
  ArrowLeft,
  CheckCircle2,
  ClipboardCheck,
  FileCheck2,
  Pencil,
  ShieldAlert,
  Target,
} from "lucide-react";

import AppLayout from "@/layouts/AppLayout";

import { Button } from "@/components/ui/button";
import Can from "@/components/auth/Can";

import { useControl } from "@/hooks/useControl";
import { useEvidence } from "@/hooks/useEvidence";
import { useFrameworkControls } from "@/hooks/useFrameworkControls";
import { useFrameworks } from "@/hooks/useFrameworks";
import { useFrameworkControlsForControl } from "@/hooks/useFrameworkControlsForControl";
import { useCreateControlFrameworkMapping } from "@/hooks/useCreateControlFrameworkMapping";
import { useRisksForControl } from "@/hooks/useRisksForControl";


// ==========================================================
// Helpers
// ==========================================================

function effectivenessClass(
  effectiveness: number
) {
  if (effectiveness >= 80) {
    return "border-emerald-200 bg-emerald-50 text-emerald-700";
  }

  if (effectiveness >= 50) {
    return "border-orange-200 bg-orange-50 text-orange-700";
  }

  return "border-red-200 bg-red-50 text-red-700";
}


function statusClass(status: string) {
  const normalized = status.toLowerCase();

  if (
    normalized === "active" ||
    normalized === "effective"
  ) {
    return "border-emerald-200 bg-emerald-50 text-emerald-700";
  }

  if (
    normalized === "inactive" ||
    normalized === "ineffective"
  ) {
    return "border-red-200 bg-red-50 text-red-700";
  }

  return "border-slate-200 bg-slate-50 text-slate-700";
}


function riskScoreClass(score: number) {
  if (score >= 20) {
    return "border-red-200 bg-red-50 text-red-700";
  }

  if (score >= 15) {
    return "border-orange-200 bg-orange-50 text-orange-700";
  }

  if (score >= 8) {
    return "border-yellow-200 bg-yellow-50 text-yellow-700";
  }

  return "border-emerald-200 bg-emerald-50 text-emerald-700";
}


// ==========================================================
// Page
// ==========================================================

export default function ViewControl() {
  const { id } = useParams();
  const navigate = useNavigate();

  const controlId = Number(id);

  const {
    data,
    isLoading,
    error,
  } = useControl(controlId);

  const {
    data: risks,
    isLoading: risksLoading,
    error: risksError,
  } = useRisksForControl(controlId);

  const {
    data: evidence,
    isLoading: evidenceLoading,
    error: evidenceError,
  } = useEvidence();

  const {
    data: frameworkControls,
    isLoading: frameworkControlsLoading,
  } = useFrameworkControls();

  const {
    data: frameworks,
    isLoading: frameworksLoading,
  } = useFrameworks();

  const {
    data: mappedFrameworkControls,
    isLoading: mappingsLoading,
  } = useFrameworkControlsForControl(
    controlId
  );

  const mappingMutation =
    useCreateControlFrameworkMapping();


  // ========================================================
  // Loading
  // ========================================================

  if (
    isLoading ||
    risksLoading ||
    evidenceLoading ||
    frameworkControlsLoading ||
    frameworksLoading ||
    mappingsLoading
  ) {
    return (
      <AppLayout>
        <div className="p-10 text-center">
          Loading control...
        </div>
      </AppLayout>
    );
  }


  // ========================================================
  // Error
  // ========================================================

  if (
    error ||
    !data ||
    !frameworkControls ||
    !frameworks ||
    !risks ||
    !evidence
  ) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Failed to load control.
        </div>
      </AppLayout>
    );
  }


  // ========================================================
  // Derived data
  // ========================================================

  const controlEvidence =
    evidence.filter(
      (item) =>
        item.control_id === controlId
    );

  const evidenceCoverage =
    controlEvidence.length > 0
      ? 100
      : 0;

  const mappedIds = new Set(
    (mappedFrameworkControls ?? []).map(
      (item) => item.id
    )
  );

  const availableFrameworkControls =
    frameworkControls.filter(
      (item) => !mappedIds.has(item.id)
    );

  const frameworkNameById =
    new Map(
      frameworks.map((framework) => [
        framework.id,
        `${framework.name} ${framework.version}`,
      ])
    );


  return (
    <AppLayout>

      <div className="mx-auto max-w-7xl space-y-6">

        {/* ==================================================
            Header
        ================================================== */}

        <div className="flex flex-col justify-between gap-4 md:flex-row md:items-center">

          <div>

            <div className="flex flex-wrap items-center gap-3">

              <h1 className="text-3xl font-bold text-slate-900">
                {data.title}
              </h1>

              <span
                className={`rounded-full border px-3 py-1 text-xs font-semibold ${effectivenessClass(
                  data.effectiveness
                )}`}
              >
                {data.effectiveness}% effective
              </span>

            </div>

            <p className="mt-2 text-slate-500">
              Control Details and GRC Posture
            </p>

          </div>


          <div className="flex flex-wrap gap-3">

            <Button
              variant="outline"
              onClick={() =>
                navigate("/controls")
              }
            >
              <ArrowLeft className="mr-2 h-4 w-4" />
              Back
            </Button>


            <Can
              resource="controls"
              action="update"
            >
              <Button
                onClick={() =>
                  navigate(
                    `/controls/${data.id}/edit`
                  )
                }
              >
                <Pencil className="mr-2 h-4 w-4" />
                Edit Control
              </Button>
            </Can>

          </div>

        </div>


        {/* ==================================================
            Control Information
        ================================================== */}

        <div className="grid gap-6 md:grid-cols-2">

          <div className="rounded-2xl border bg-white p-6 shadow-sm">

            <h2 className="mb-4 text-lg font-semibold">
              Control Information
            </h2>

            <div>

              <p className="mb-2 text-sm font-medium text-slate-500">
                Description
              </p>

              <p className="leading-7 text-slate-600">
                {data.description}
              </p>

            </div>

          </div>


          <div className="rounded-2xl border bg-white p-6 shadow-sm">

            <h2 className="mb-4 text-lg font-semibold">
              Assessment
            </h2>

            <div className="space-y-4">

              <DetailRow
                label="Control Type"
                value={data.control_type}
              />

              <div className="flex items-center justify-between gap-4">

                <span className="text-sm text-slate-500">
                  Status
                </span>

                <span
                  className={`rounded-full border px-2.5 py-1 text-xs font-semibold ${statusClass(
                    data.status
                  )}`}
                >
                  {data.status}
                </span>

              </div>

              <DetailRow
                label="Effectiveness"
                value={`${data.effectiveness}%`}
              />

              <DetailRow
                label="Owner"
                value={`User #${data.owner_id}`}
              />

              <DetailRow
                label="Created"
                value={new Date(
                  data.created_at
                ).toLocaleString()}
              />

              <DetailRow
                label="Updated"
                value={new Date(
                  data.updated_at
                ).toLocaleString()}
              />

            </div>

          </div>

        </div>


        {/* ==================================================
            GRC Posture
        ================================================== */}

        <section className="rounded-2xl border bg-white shadow-sm">

          <div className="border-b p-6">

            <div className="flex items-start gap-3">

              <div className="rounded-xl bg-indigo-50 p-3">
                <Target className="h-6 w-6 text-indigo-600" />
              </div>

              <div>

                <h2 className="text-lg font-semibold">
                  GRC Posture
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Connected risks, evidence, and compliance
                  requirements for this control.
                </p>

              </div>

            </div>

          </div>


          <div className="grid gap-4 p-6 sm:grid-cols-2 lg:grid-cols-4">

            <PostureMetric
              label="Associated Risks"
              value={risks.length}
              icon={ShieldAlert}
              emphasis={
                risks.some(
                  (risk) =>
                    risk.risk_score >= 20
                )
                  ? "critical"
                  : undefined
              }
            />

            <PostureMetric
              label="Evidence"
              value={controlEvidence.length}
              icon={FileCheck2}
            />

            <PostureMetric
              label="Evidence Coverage"
              value={`${evidenceCoverage}%`}
              icon={CheckCircle2}
              emphasis={
                evidenceCoverage === 0
                  ? "critical"
                  : undefined
              }
            />

            <PostureMetric
              label="Framework Requirements"
              value={
                mappedFrameworkControls?.length ?? 0
              }
              icon={ClipboardCheck}
            />

          </div>

        </section>


        {/* ==================================================
            Associated Risks
        ================================================== */}

        <section className="rounded-2xl border bg-white shadow-sm">

          <div className="border-b p-6">

            <div className="flex items-start gap-3">

              <div className="rounded-xl bg-red-50 p-3">
                <ShieldAlert className="h-6 w-6 text-red-600" />
              </div>

              <div>

                <h2 className="text-lg font-semibold">
                  Associated Risks
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Risks currently mapped to this control.
                </p>

              </div>

            </div>

          </div>


          <div className="p-6">

            {risksError ? (

              <div className="rounded-xl border border-red-200 bg-red-50 p-5">

                <div className="flex items-start gap-3">

                  <AlertTriangle className="mt-0.5 h-5 w-5 text-red-600" />

                  <div>

                    <h3 className="font-semibold text-red-700">
                      Risks unavailable
                    </h3>

                    <p className="mt-1 text-sm text-red-600">
                      The associated risks could not be loaded.
                    </p>

                  </div>

                </div>

              </div>

            ) : risks.length === 0 ? (

              <div className="rounded-xl border border-emerald-200 bg-emerald-50 p-5">

                <div className="flex items-start gap-3">

                  <CheckCircle2 className="mt-0.5 h-5 w-5 text-emerald-600" />

                  <div>

                    <h3 className="font-semibold text-emerald-700">
                      No risks mapped
                    </h3>

                    <p className="mt-1 text-sm text-emerald-600">
                      This control is not currently associated
                      with any visible risks.
                    </p>

                  </div>

                </div>

              </div>

            ) : (

              <div className="space-y-3">

                {risks.map((risk) => (

                  <button
                    key={risk.id}
                    type="button"
                    onClick={() =>
                      navigate(
                        `/risks/${risk.id}`
                      )
                    }
                    className="flex w-full items-center justify-between rounded-xl border p-4 text-left transition hover:bg-slate-50"
                  >

                    <div className="min-w-0">

                      <div className="flex flex-wrap items-center gap-2">

                        <span className="font-mono text-xs text-slate-400">
                          Risk #{risk.id}
                        </span>

                        <span
                          className={`rounded-full border px-2.5 py-0.5 text-xs font-semibold ${riskScoreClass(
                            risk.risk_score
                          )}`}
                        >
                          Score {risk.risk_score}
                        </span>

                      </div>

                      <p className="mt-1 font-medium text-slate-900">
                        {risk.title}
                      </p>

                      <p className="mt-1 text-sm text-slate-500">
                        {risk.status}
                      </p>

                    </div>

                    <span className="shrink-0 text-sm font-medium text-blue-600">
                      View Risk →
                    </span>

                  </button>

                ))}

              </div>

            )}

          </div>

        </section>


        {/* ==================================================
            Evidence
        ================================================== */}

        <section className="rounded-2xl border bg-white shadow-sm">

          <div className="border-b p-6">

            <div className="flex items-start gap-3">

              <div className="rounded-xl bg-emerald-50 p-3">
                <FileCheck2 className="h-6 w-6 text-emerald-600" />
              </div>

              <div>

                <h2 className="text-lg font-semibold">
                  Evidence
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Evidence currently associated with this control.
                </p>

              </div>

            </div>

          </div>


          <div className="p-6">

            {evidenceError ? (

              <div className="rounded-xl border border-red-200 bg-red-50 p-5">

                <div className="flex items-start gap-3">

                  <AlertTriangle className="mt-0.5 h-5 w-5 text-red-600" />

                  <div>

                    <h3 className="font-semibold text-red-700">
                      Evidence unavailable
                    </h3>

                    <p className="mt-1 text-sm text-red-600">
                      Evidence could not be loaded.
                    </p>

                  </div>

                </div>

              </div>

            ) : controlEvidence.length === 0 ? (

              <div className="rounded-xl border border-orange-200 bg-orange-50 p-5">

                <div className="flex items-start gap-3">

                  <AlertTriangle className="mt-0.5 h-5 w-5 text-orange-600" />

                  <div>

                    <h3 className="font-semibold text-orange-700">
                      No evidence available
                    </h3>

                    <p className="mt-1 text-sm text-orange-700">
                      This control currently has no visible evidence.
                    </p>

                  </div>

                </div>

              </div>

            ) : (

              <div className="space-y-3">

                {controlEvidence.map((item) => (

                  <button
                    key={item.id}
                    type="button"
                    onClick={() =>
                      navigate(
                        `/evidence/${item.id}`
                      )
                    }
                    className="flex w-full items-center justify-between rounded-xl border p-4 text-left transition hover:bg-slate-50"
                  >

                    <div className="min-w-0">

                      <p className="font-medium text-slate-900">
                        {item.title}
                      </p>

                      <p className="mt-1 text-sm text-slate-500">
                        {item.file_name}
                      </p>

                    </div>

                    <span className="shrink-0 text-sm font-medium text-blue-600">
                      View Evidence →
                    </span>

                  </button>

                ))}

              </div>

            )}

          </div>

        </section>


        {/* ==================================================
            Framework Requirements
        ================================================== */}

        <section className="rounded-2xl border bg-white shadow-sm">

          <div className="border-b p-6">

            <div className="flex items-start gap-3">

              <div className="rounded-xl bg-indigo-50 p-3">
                <ClipboardCheck className="h-6 w-6 text-indigo-600" />
              </div>

              <div>

                <h2 className="text-lg font-semibold">
                  Framework Requirements
                </h2>

                <p className="mt-1 text-sm text-slate-500">
                  Compliance requirements mapped to this control.
                </p>

              </div>

            </div>

          </div>


          <div className="space-y-4 p-6">

            {mappedFrameworkControls &&
            mappedFrameworkControls.length > 0 ? (

              mappedFrameworkControls.map(
                (frameworkControl) => (

                  <button
                    key={frameworkControl.id}
                    type="button"
                    onClick={() =>
                      navigate(
                        `/framework-controls/${frameworkControl.id}`
                      )
                    }
                    className="flex w-full items-center justify-between rounded-xl border p-4 text-left transition hover:bg-slate-50"
                  >

                    <div>

                      <p className="font-mono text-sm text-blue-600">
                        {frameworkControl.control_code}
                      </p>

                      <p className="font-medium text-slate-900">
                        {frameworkControl.title}
                      </p>

                      <p className="text-sm text-slate-500">
                        {frameworkNameById.get(
                          frameworkControl.framework_id
                        ) ??
                          `Framework #${frameworkControl.framework_id}`}
                      </p>

                    </div>

                    <span className="text-sm font-medium text-blue-600">
                      View →
                    </span>

                  </button>

                )
              )

            ) : (

              <p className="text-sm text-slate-500">
                No framework requirements are mapped to this control.
              </p>

            )}

          </div>


          {/* Create Mapping */}

          <Can
            resource="control_framework_mappings"
            action="create"
          >
            <div className="border-t p-6">

              <h3 className="mb-3 font-semibold">
                Map Framework Requirement
              </h3>

              <div className="flex flex-col gap-3 sm:flex-row">

                <select
                  id="framework-control"
                  defaultValue=""
                  className="flex-1 rounded-lg border px-4 py-2"
                >

                  <option value="">
                    Select framework requirement
                  </option>

                  {availableFrameworkControls.map(
                    (frameworkControl) => (

                      <option
                        key={frameworkControl.id}
                        value={frameworkControl.id}
                      >
                        {frameworkControl.control_code} —{" "}
                        {frameworkControl.title}
                      </option>

                    )
                  )}

                </select>


                <button
                  type="button"
                  disabled={
                    mappingMutation.isPending ||
                    availableFrameworkControls.length === 0
                  }
                  onClick={async () => {

                    const select =
                      document.getElementById(
                        "framework-control"
                      ) as HTMLSelectElement;

                    const frameworkControlId =
                      Number(select.value);

                    if (!frameworkControlId) {
                      alert(
                        "Please select a framework requirement."
                      );
                      return;
                    }

                    try {

                      await mappingMutation.mutateAsync({
                        control_id:
                          controlId,
                        framework_control_id:
                          frameworkControlId,
                      });

                      select.value = "";

                    } catch (error) {

                      console.error(error);

                      alert(
                        "Failed to create framework mapping."
                      );

                    }

                  }}
                  className="rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {mappingMutation.isPending
                    ? "Mapping..."
                    : "Map Control"}
                </button>

              </div>

            </div>
          </Can>

        </section>


        {/* ==================================================
            Connected GRC Lifecycle
        ================================================== */}

        <section className="rounded-2xl border border-slate-700 bg-slate-900 p-6">

          <div className="flex items-start gap-3">

            <div className="rounded-lg bg-slate-950 p-2">

              <Target className="h-5 w-5 text-indigo-400" />

            </div>

            <div>

              <h2 className="text-sm font-semibold text-white">
                Connected GRC Lifecycle
              </h2>

              <p className="mt-1 text-sm leading-6 text-slate-300">
                This control connects organizational risks with
                supporting evidence and compliance framework
                requirements. Relationship results are limited to
                resources within the current user's authorization scope.
              </p>

            </div>

          </div>

        </section>

      </div>

    </AppLayout>
  );
}


// ==========================================================
// Detail Row
// ==========================================================

interface DetailRowProps {
  label: string;
  value: string;
}

function DetailRow({
  label,
  value,
}: DetailRowProps) {
  return (
    <div className="flex items-center justify-between gap-4">

      <span className="text-sm text-slate-500">
        {label}
      </span>

      <span className="text-right font-medium text-slate-900">
        {value}
      </span>

    </div>
  );
}


// ==========================================================
// Posture Metric
// ==========================================================

interface PostureMetricProps {
  label: string;
  value: number | string;
  icon: ComponentType<{
    className?: string;
  }>;
  emphasis?: "critical";
}

function PostureMetric({
  label,
  value,
  icon: Icon,
  emphasis,
}: PostureMetricProps) {
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