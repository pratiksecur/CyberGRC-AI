import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { ArrowLeft, GitMerge } from "lucide-react";

import AppLayout from "@/layouts/AppLayout";

import type {
  CrosswalkCandidateControl,
  CrosswalkOpportunity,
} from "@/api/frameworkCrosswalk";

import { useCrosswalkOpportunities } from "@/hooks/useFrameworkCrosswalk";
import { useCreateControlFrameworkMapping } from "@/hooks/useCreateControlFrameworkMapping";

import Can from "@/components/auth/Can";
import {
  ConfidenceBadge,
  ThemeChips,
} from "@/components/frameworks/CrosswalkParts";

import { notify } from "@/lib/notify";
import { apiErrorMessage } from "@/lib/apiError";

const PAGE_SIZE = 25;

function StatTile({
  label,
  value,
  hint,
}: {
  label: string;
  value: number;
  hint: string;
}) {
  return (
    <div className="rounded-2xl border bg-white p-5 shadow-sm">
      <p className="text-sm font-medium text-slate-500">{label}</p>

      <p className="mt-1 text-3xl font-bold text-slate-900">{value}</p>

      <p className="mt-1 text-xs text-slate-500">{hint}</p>
    </div>
  );
}

/*
 * Unmapped requirements that controls you already have may support,
 * because those controls are mapped to a related requirement in another
 * framework. Each one is applied by a person, one at a time.
 */
export default function FrameworkCrosswalk() {
  const navigate = useNavigate();

  const { data, isLoading, error } = useCrosswalkOpportunities();

  const mappingMutation = useCreateControlFrameworkMapping();

  const [frameworkId, setFrameworkId] = useState<number | "all">("all");
  const [directOnly, setDirectOnly] = useState(false);
  const [visibleCount, setVisibleCount] = useState(PAGE_SIZE);
  const [pendingKey, setPendingKey] = useState<string | null>(null);

  const filtered = useMemo(() => {
    const opportunities = data?.opportunities ?? [];

    return opportunities.filter(
      (opportunity) =>
        (frameworkId === "all" ||
          opportunity.framework_id === frameworkId) &&
        (!directOnly || opportunity.best_confidence === "direct")
    );
  }, [data, frameworkId, directOnly]);

  async function handleMap(
    opportunity: CrosswalkOpportunity,
    candidate: CrosswalkCandidateControl
  ) {
    const key = `${opportunity.framework_control_id}:${candidate.control_id}`;

    setPendingKey(key);

    try {
      await mappingMutation.mutateAsync({
        control_id: candidate.control_id,
        framework_control_id: opportunity.framework_control_id,
      });

      notify.success(
        `Mapped "${candidate.control_title}" to ${opportunity.control_code}.`
      );
    } catch (mappingError) {
      notify.error(
        apiErrorMessage(mappingError, "Failed to create framework mapping.")
      );
    } finally {
      setPendingKey(null);
    }
  }

  if (isLoading) {
    return (
      <AppLayout>
        <div className="mx-auto max-w-6xl space-y-4">
          <div className="h-10 w-80 animate-pulse rounded bg-slate-200" />
          <div className="h-28 animate-pulse rounded-2xl bg-slate-100" />
          <div className="h-72 animate-pulse rounded-2xl bg-slate-100" />
        </div>
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="mx-auto max-w-4xl rounded-xl border border-red-200 bg-red-50 p-6">
          <h2 className="font-semibold text-red-700">
            Crosswalk unavailable
          </h2>

          <p className="mt-1 text-sm text-red-600">
            {apiErrorMessage(error, "The crosswalk could not be loaded.")}
          </p>
        </div>
      </AppLayout>
    );
  }

  const visible = filtered.slice(0, visibleCount);

  return (
    <AppLayout>
      <div className="mx-auto max-w-6xl space-y-6">
        {/* Header */}
        <div>
          <button
            type="button"
            onClick={() => navigate("/frameworks")}
            className="mb-4 flex items-center gap-2 text-sm text-slate-500 transition hover:text-slate-900"
          >
            <ArrowLeft size={16} />
            Back to Frameworks
          </button>

          <div className="flex items-start gap-3">
            <div className="rounded-xl bg-emerald-100 p-3">
              <GitMerge size={22} className="text-emerald-600" />
            </div>

            <div>
              <h1 className="text-3xl font-bold text-slate-900">
                Framework Crosswalk
              </h1>

              <p className="mt-1 text-slate-500">
                Requirements with no control mapped that your existing
                controls may already support.
              </p>
            </div>
          </div>
        </div>

        {/* Summary */}
        <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
          <StatTile
            label="Requirements"
            value={data.total_requirements}
            hint="Across all your frameworks"
          />

          <StatTile
            label="Unmapped"
            value={data.unmapped_requirements}
            hint="No control mapped yet"
          />

          <StatTile
            label="Opportunities"
            value={data.opportunity_count}
            hint="An existing control may apply"
          />

          <StatTile
            label="Direct matches"
            value={data.direct_opportunity_count}
            hint="Same focused theme on both sides"
          />
        </div>

        {/* Per framework */}
        <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="bg-slate-50 text-slate-500">
              <tr>
                <th className="px-6 py-3 font-semibold">Framework</th>
                <th className="px-6 py-3 text-right font-semibold">
                  Requirements
                </th>
                <th className="px-6 py-3 text-right font-semibold">
                  Unmapped
                </th>
                <th className="px-6 py-3 text-right font-semibold">
                  Opportunities
                </th>
              </tr>
            </thead>

            <tbody className="divide-y">
              {data.frameworks.map((framework) => (
                <tr key={framework.framework_id}>
                  <td className="px-6 py-3 font-medium text-slate-900">
                    {framework.framework_name}
                  </td>
                  <td className="px-6 py-3 text-right tabular-nums">
                    {framework.requirement_count}
                  </td>
                  <td className="px-6 py-3 text-right tabular-nums">
                    {framework.unmapped_requirements}
                  </td>
                  <td className="px-6 py-3 text-right tabular-nums">
                    {framework.opportunities}
                  </td>
                </tr>
              ))}

              {data.frameworks.length === 0 && (
                <tr>
                  <td
                    colSpan={4}
                    className="px-6 py-4 text-slate-500"
                  >
                    No frameworks yet.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>

        {/* Opportunities */}
        <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b bg-slate-50 p-6">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                Opportunities
              </h2>

              <p className="text-sm text-slate-500">
                {filtered.length} shown
                {data.opportunity_count > data.opportunities.length
                  ? ` (first ${data.opportunities.length} of ${data.opportunity_count} loaded)`
                  : ""}
              </p>
            </div>

            <div className="flex flex-wrap items-center gap-3">
              <select
                value={frameworkId}
                aria-label="Filter by framework"
                onChange={(event) => {
                  setFrameworkId(
                    event.target.value === "all"
                      ? "all"
                      : Number(event.target.value)
                  );
                  setVisibleCount(PAGE_SIZE);
                }}
                className="rounded-lg border border-slate-300 px-3 py-2 text-sm"
              >
                <option value="all">All frameworks</option>

                {data.frameworks.map((framework) => (
                  <option
                    key={framework.framework_id}
                    value={framework.framework_id}
                  >
                    {framework.framework_name}
                  </option>
                ))}
              </select>

              <label className="flex items-center gap-2 text-sm text-slate-700">
                <input
                  type="checkbox"
                  checked={directOnly}
                  onChange={(event) => {
                    setDirectOnly(event.target.checked);
                    setVisibleCount(PAGE_SIZE);
                  }}
                />
                Direct matches only
              </label>
            </div>
          </div>

          {filtered.length === 0 ? (
            <p className="p-6 text-sm text-slate-500">
              {data.opportunity_count === 0
                ? "No opportunities yet. Map a control to a requirement in any framework, and related requirements in the other frameworks will appear here."
                : "No opportunities match these filters."}
            </p>
          ) : (
            <ul className="divide-y">
              {visible.map((opportunity) => (
                <li
                  key={opportunity.framework_control_id}
                  className="space-y-3 p-6"
                >
                  <div className="flex flex-wrap items-start justify-between gap-3">
                    <div className="min-w-0">
                      <p className="font-mono text-sm text-blue-600">
                        {opportunity.control_code}
                      </p>

                      <p className="font-medium text-slate-900">
                        {opportunity.title}
                      </p>

                      <p className="text-sm text-slate-500">
                        {opportunity.framework_name}
                      </p>
                    </div>

                    <button
                      type="button"
                      onClick={() =>
                        navigate(
                          `/framework-controls/${opportunity.framework_control_id}`
                        )
                      }
                      className="shrink-0 rounded-lg border px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
                    >
                      View requirement
                    </button>
                  </div>

                  <div className="space-y-2">
                    {opportunity.candidates.map((candidate) => {
                      const key = `${opportunity.framework_control_id}:${candidate.control_id}`;

                      return (
                        <div
                          key={candidate.control_id}
                          className="flex flex-col gap-3 rounded-xl bg-slate-50 p-4 sm:flex-row sm:items-center sm:justify-between"
                        >
                          <div className="min-w-0 space-y-1.5">
                            <div className="flex flex-wrap items-center gap-2">
                              <button
                                type="button"
                                onClick={() =>
                                  navigate(
                                    `/controls/${candidate.control_id}`
                                  )
                                }
                                className="text-left font-medium text-slate-900 hover:underline"
                              >
                                {candidate.control_title}
                              </button>

                              <ConfidenceBadge
                                confidence={candidate.confidence}
                              />
                            </div>

                            <ThemeChips themes={candidate.shared_themes} />

                            <p className="text-xs text-slate-500">
                              Already mapped to{" "}
                              {candidate.via
                                .map(
                                  (source) =>
                                    `${source.control_code} (${source.framework_name})`
                                )
                                .join(", ")}
                              .
                            </p>
                          </div>

                          <Can
                            resource="control_framework_mappings"
                            action="create"
                          >
                            <button
                              type="button"
                              disabled={pendingKey !== null}
                              onClick={() =>
                                handleMap(opportunity, candidate)
                              }
                              className="shrink-0 rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                            >
                              {pendingKey === key
                                ? "Mapping…"
                                : "Map this control"}
                            </button>
                          </Can>
                        </div>
                      );
                    })}
                  </div>
                </li>
              ))}
            </ul>
          )}

          {filtered.length > visibleCount && (
            <div className="border-t p-4 text-center">
              <button
                type="button"
                onClick={() =>
                  setVisibleCount((current) => current + PAGE_SIZE)
                }
                className="text-sm font-medium text-blue-600 hover:underline"
              >
                Show {Math.min(PAGE_SIZE, filtered.length - visibleCount)} more
              </button>
            </div>
          )}
        </div>

        <p className="text-xs text-slate-500">{data.disclaimer}</p>
      </div>
    </AppLayout>
  );
}
