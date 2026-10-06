import {
  AlertTriangle,
  Activity,
  CheckCircle2,
  FileWarning,
  GitBranch,
  ShieldAlert,
  ShieldCheck,
} from "lucide-react";

import type {
  RegulatoryIntelligence,
} from "@/api/frameworks";


interface Props {
  intelligence: RegulatoryIntelligence;
}


function postureClass(
  posture: string
) {
  if (posture === "CRITICAL") {
    return "bg-red-100 text-red-700";
  }

  if (posture === "EXPOSED") {
    return "bg-orange-100 text-orange-700";
  }

  if (posture === "DEGRADED") {
    return "bg-amber-100 text-amber-700";
  }

  return "bg-emerald-100 text-emerald-700";
}


function stateClass(
  state: string
) {
  if (
    state === "GAP" ||
    state === "CRITICAL"
  ) {
    return "bg-red-100 text-red-700";
  }

  if (
    state === "PARTIAL" ||
    state === "HIGH" ||
    state === "MEDIUM"
  ) {
    return "bg-amber-100 text-amber-700";
  }

  return "bg-emerald-100 text-emerald-700";
}


export default function RegulatoryIntelligence({
  intelligence,
}: Props) {

  return (
    <div className="space-y-6">

      {/* Header */}

      <div className="rounded-2xl border bg-white p-6 shadow-sm">

        <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

          <div>

            <div className="flex items-center gap-2">

              <ShieldCheck
                size={22}
                className="text-blue-600"
              />

              <h2 className="text-xl font-semibold">
                Regulatory Intelligence
              </h2>

            </div>

            <p className="mt-1 text-sm text-slate-500">
              Continuous analysis of regulatory
              requirements, controls, evidence
              and risk exposure.
            </p>

          </div>

          <span
            className={`rounded-full px-4 py-2 text-sm font-semibold ${postureClass(
              intelligence.overall_posture
            )}`}
          >
            {intelligence.overall_posture}
          </span>

        </div>

      </div>


      {/* Summary */}

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">

        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <p className="text-sm text-slate-500">
            Frameworks
          </p>

          <p className="mt-2 text-3xl font-bold">
            {intelligence.framework_count}
          </p>

        </div>


        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <p className="text-sm text-slate-500">
            Requirements
          </p>

          <p className="mt-2 text-3xl font-bold">
            {intelligence.total_requirements}
          </p>

        </div>


        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <div className="flex items-center justify-between">

            <div>

              <p className="text-sm text-slate-500">
                Coverage
              </p>

              <p className="mt-2 text-3xl font-bold">
                {intelligence.overall_coverage_percent}%
              </p>

            </div>

            <Activity
              size={28}
              className="text-blue-600"
            />

          </div>

        </div>


        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <div className="flex items-center justify-between">

            <div>

              <p className="text-sm text-slate-500">
                Regulatory Gaps
              </p>

              <p className="mt-2 text-3xl font-bold">
                {intelligence.gap_requirements}
              </p>

            </div>

            <AlertTriangle
              size={28}
              className="text-red-600"
            />

          </div>

        </div>


        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <div className="flex items-center justify-between">

            <div>

              <p className="text-sm text-slate-500">
                Framework Overlap
              </p>

              <p className="mt-2 text-3xl font-bold">
                {intelligence.overlapping_controls}
              </p>

            </div>

            <GitBranch
              size={28}
              className="text-purple-600"
            />

          </div>

        </div>

      </div>


      {/* Requirement summary */}

      <div className="grid gap-4 md:grid-cols-3">

        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <div className="flex items-center gap-3">

            <CheckCircle2
              size={22}
              className="text-emerald-600"
            />

            <div>

              <p className="text-sm text-slate-500">
                Covered
              </p>

              <p className="text-2xl font-bold">
                {intelligence.covered_requirements}
              </p>

            </div>

          </div>

        </div>


        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <div className="flex items-center gap-3">

            <FileWarning
              size={22}
              className="text-amber-600"
            />

            <div>

              <p className="text-sm text-slate-500">
                Partial
              </p>

              <p className="text-2xl font-bold">
                {intelligence.partial_requirements}
              </p>

            </div>

          </div>

        </div>


        <div className="rounded-2xl border bg-white p-5 shadow-sm">

          <div className="flex items-center gap-3">

            <ShieldAlert
              size={22}
              className="text-red-600"
            />

            <div>

              <p className="text-sm text-slate-500">
                Critical
              </p>

              <p className="text-2xl font-bold">
                {intelligence.critical_requirements}
              </p>

            </div>

          </div>

        </div>

      </div>


      {/* Frameworks */}

      <div className="space-y-4">

        {intelligence.frameworks.map(
          (framework) => (

            <div
              key={framework.framework_id}
              className="rounded-2xl border bg-white p-6 shadow-sm"
            >

              <div className="flex flex-col gap-4 md:flex-row md:items-center md:justify-between">

                <div>

                  <h3 className="text-lg font-semibold">
                    {framework.framework_name}
                  </h3>

                  <p className="text-sm text-slate-500">
                    Version{" "}
                    {framework.framework_version}
                  </p>

                </div>

                <div className="flex items-center gap-3">

                  <span
                    className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      framework.gap_requirements > 0
                        ? "bg-red-100 text-red-700"
                        : "bg-emerald-100 text-emerald-700"
                    }`}
                  >
                    {framework.coverage_percent}%
                    {" "}coverage
                  </span>

                </div>

              </div>


              <div className="mt-5 grid gap-3 sm:grid-cols-4">

                <div className="rounded-xl bg-slate-50 p-4">

                  <p className="text-xs text-slate-500">
                    Requirements
                  </p>

                  <p className="mt-1 text-xl font-bold">
                    {framework.requirement_count}
                  </p>

                </div>

                <div className="rounded-xl bg-emerald-50 p-4">

                  <p className="text-xs text-slate-500">
                    Covered
                  </p>

                  <p className="mt-1 text-xl font-bold">
                    {framework.covered_requirements}
                  </p>

                </div>

                <div className="rounded-xl bg-amber-50 p-4">

                  <p className="text-xs text-slate-500">
                    Partial
                  </p>

                  <p className="mt-1 text-xl font-bold">
                    {framework.partial_requirements}
                  </p>

                </div>

                <div className="rounded-xl bg-red-50 p-4">

                  <p className="text-xs text-slate-500">
                    Gaps
                  </p>

                  <p className="mt-1 text-xl font-bold">
                    {framework.gap_requirements}
                  </p>

                </div>

              </div>


              {/* Requirements */}

              <div className="mt-6 overflow-x-auto">

                <table className="w-full text-sm">

                  <thead>

                    <tr className="border-b text-left text-slate-500">

                      <th className="px-3 py-3">
                        Requirement
                      </th>

                      <th className="px-3 py-3">
                        Controls
                      </th>

                      <th className="px-3 py-3">
                        State
                      </th>

                      <th className="px-3 py-3">
                        Exposure
                      </th>

                    </tr>

                  </thead>

                  <tbody>

                    {framework.requirements.map(
                      (requirement) => (

                        <tr
                          key={
                            requirement.requirement_id
                          }
                          className="border-b last:border-0"
                        >

                          <td className="px-3 py-4">

                            <div className="font-medium">
                              {
                                requirement.requirement_code
                              }
                            </div>

                            <div className="text-xs text-slate-500">
                              {
                                requirement.requirement_title
                              }
                            </div>

                          </td>

                          <td className="px-3 py-4">
                            {
                              requirement.mapped_control_count
                            }
                          </td>

                          <td className="px-3 py-4">

                            <span
                              className={`rounded-full px-2.5 py-1 text-xs font-semibold ${stateClass(
                                requirement.state
                              )}`}
                            >
                              {requirement.state}
                            </span>

                          </td>

                          <td className="px-3 py-4">

                            <span
                              className={`rounded-full px-2.5 py-1 text-xs font-semibold ${stateClass(
                                requirement.exposure
                              )}`}
                            >
                              {requirement.exposure}
                            </span>

                          </td>

                        </tr>

                      )
                    )}

                  </tbody>

                </table>

              </div>

            </div>

          )
        )}

      </div>

    </div>
  );
}