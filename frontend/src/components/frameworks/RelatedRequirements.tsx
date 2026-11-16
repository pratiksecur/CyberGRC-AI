import { useNavigate } from "react-router-dom";

import { useRelatedRequirements } from "@/hooks/useFrameworkCrosswalk";

import {
  ConfidenceBadge,
  CrosswalkDisclaimer,
  ThemeChips,
} from "@/components/frameworks/CrosswalkParts";

interface Props {
  frameworkControlId: number;
}

/*
 * Requirements in other frameworks that share a theme with this one, and
 * whether each already has a control mapped to it.
 */
export default function RelatedRequirements({ frameworkControlId }: Props) {
  const navigate = useNavigate();

  const { data, isLoading, error } =
    useRelatedRequirements(frameworkControlId);

  return (
    <div className="rounded-2xl border bg-white">
      <div className="border-b p-6">
        <h2 className="text-lg font-semibold">
          Related Requirements in Other Frameworks
        </h2>

        <p className="text-sm text-slate-500">
          Requirements that share a security theme with this one.
        </p>

        {data && data.themes.length > 0 && (
          <div className="mt-3">
            <ThemeChips themes={data.themes} />
          </div>
        )}
      </div>

      <div className="space-y-3 p-6">
        {isLoading && (
          <p className="text-sm text-slate-500">
            Loading related requirements…
          </p>
        )}

        {!isLoading && error && (
          <p className="text-sm text-slate-500">
            Related requirements are unavailable right now.
          </p>
        )}

        {!isLoading && !error && data && !data.in_crosswalk && (
          <p className="text-sm text-slate-500">
            This requirement is not part of the built-in crosswalk, so no
            related requirements are suggested for it.
          </p>
        )}

        {!isLoading &&
          !error &&
          data &&
          data.in_crosswalk &&
          data.related.length === 0 && (
            <p className="text-sm text-slate-500">
              No related requirements were found in your other frameworks.
            </p>
          )}

        {data?.related.map((related) => (
          <button
            key={related.framework_control_id}
            type="button"
            onClick={() =>
              navigate(
                `/framework-controls/${related.framework_control_id}`
              )
            }
            className="flex w-full flex-col gap-2 rounded-lg border p-4 text-left transition hover:bg-slate-50 sm:flex-row sm:items-center sm:justify-between"
          >
            <div className="min-w-0 space-y-1.5">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-sm text-blue-600">
                  {related.control_code}
                </span>

                <ConfidenceBadge confidence={related.confidence} />
              </div>

              <p className="font-medium text-slate-900">{related.title}</p>

              <p className="text-sm text-slate-500">
                {related.framework_name}
              </p>

              <ThemeChips themes={related.shared_themes} />
            </div>

            <span
              className={
                related.mapped_control_count > 0
                  ? "shrink-0 text-sm font-medium text-emerald-700"
                  : "shrink-0 text-sm text-slate-500"
              }
            >
              {related.mapped_control_count > 0
                ? `${related.mapped_control_count} ${
                    related.mapped_control_count === 1
                      ? "control"
                      : "controls"
                  } mapped`
                : "No control mapped"}
            </span>
          </button>
        ))}

        {data && data.related.length > 0 && <CrosswalkDisclaimer />}
      </div>
    </div>
  );
}
