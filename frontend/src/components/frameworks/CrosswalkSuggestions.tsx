import { useState } from "react";
import { useNavigate } from "react-router-dom";
import { GitMerge } from "lucide-react";

import type { CrosswalkSuggestion } from "@/api/frameworkCrosswalk";

import { useCrosswalkSuggestions } from "@/hooks/useFrameworkCrosswalk";
import { useCreateControlFrameworkMapping } from "@/hooks/useCreateControlFrameworkMapping";

import Can from "@/components/auth/Can";
import {
  ConfidenceBadge,
  CrosswalkDisclaimer,
  ThemeChips,
} from "@/components/frameworks/CrosswalkParts";

import { notify } from "@/lib/notify";
import { apiErrorMessage } from "@/lib/apiError";

interface Props {
  controlId: number;
}

/*
 * Requirements in other frameworks that this control may also support,
 * worked out from the requirements it is already mapped to. Nothing is
 * mapped automatically: each suggestion has its own Map button.
 */
export default function CrosswalkSuggestions({ controlId }: Props) {
  const navigate = useNavigate();

  const { data, isLoading, error } = useCrosswalkSuggestions(controlId);

  const mappingMutation = useCreateControlFrameworkMapping();

  const [showBroad, setShowBroad] = useState(false);
  const [pendingId, setPendingId] = useState<number | null>(null);

  async function handleMap(suggestion: CrosswalkSuggestion) {
    setPendingId(suggestion.framework_control_id);

    try {
      await mappingMutation.mutateAsync({
        control_id: controlId,
        framework_control_id: suggestion.framework_control_id,
      });

      notify.success(
        `Mapped to ${suggestion.control_code} (${suggestion.framework_name}).`
      );
    } catch (mappingError) {
      notify.error(
        apiErrorMessage(mappingError, "Failed to create framework mapping.")
      );
    } finally {
      setPendingId(null);
    }
  }

  const suggestions = data?.suggestions ?? [];

  const direct = suggestions.filter(
    (suggestion) => suggestion.confidence === "direct"
  );

  const broad = suggestions.filter(
    (suggestion) => suggestion.confidence === "broad"
  );

  const visible = showBroad ? [...direct, ...broad] : direct;

  return (
    <div className="border-t p-6">
      <div className="flex items-start gap-3">
        <div className="rounded-xl bg-emerald-50 p-2.5">
          <GitMerge className="h-5 w-5 text-emerald-600" />
        </div>

        <div>
          <h3 className="font-semibold">
            Suggested from other frameworks
          </h3>

          <p className="mt-0.5 text-sm text-slate-500">
            Requirements related to the ones this control is already mapped
            to. Map once, reuse the control across frameworks.
          </p>
        </div>
      </div>

      <div className="mt-4 space-y-3">
        {isLoading && (
          <p className="text-sm text-slate-500">Loading suggestions…</p>
        )}

        {!isLoading && error && (
          <p className="text-sm text-slate-500">
            Suggestions are unavailable right now.
          </p>
        )}

        {!isLoading && !error && data && suggestions.length === 0 && (
          <p className="text-sm text-slate-500">
            {data.mapped_requirement_count === 0
              ? "Map this control to a requirement first. Related requirements in other frameworks will then be suggested here."
              : "No further related requirements were found for this control."}
          </p>
        )}

        {visible.map((suggestion) => (
          <div
            key={suggestion.framework_control_id}
            className="flex flex-col gap-3 rounded-xl border p-4 sm:flex-row sm:items-center sm:justify-between"
          >
            <div className="min-w-0 space-y-1.5">
              <div className="flex flex-wrap items-center gap-2">
                <span className="font-mono text-sm text-blue-600">
                  {suggestion.control_code}
                </span>

                <ConfidenceBadge confidence={suggestion.confidence} />
              </div>

              <p className="font-medium text-slate-900">
                {suggestion.title}
              </p>

              <p className="text-sm text-slate-500">
                {suggestion.framework_name}
              </p>

              <ThemeChips themes={suggestion.shared_themes} />

              <p className="text-xs text-slate-500">
                Because this control is mapped to{" "}
                {suggestion.because_of
                  .map(
                    (source) =>
                      `${source.control_code} (${source.framework_name})`
                  )
                  .join(", ")}
                .
              </p>
            </div>

            <div className="flex shrink-0 gap-2">
              <button
                type="button"
                onClick={() =>
                  navigate(
                    `/framework-controls/${suggestion.framework_control_id}`
                  )
                }
                className="rounded-lg border px-3 py-1.5 text-sm font-medium text-slate-700 hover:bg-slate-50"
              >
                View
              </button>

              <Can resource="control_framework_mappings" action="create">
                <button
                  type="button"
                  disabled={pendingId !== null}
                  onClick={() => handleMap(suggestion)}
                  className="rounded-lg bg-blue-600 px-3 py-1.5 text-sm font-medium text-white hover:bg-blue-700 disabled:opacity-50"
                >
                  {pendingId === suggestion.framework_control_id
                    ? "Mapping…"
                    : "Map"}
                </button>
              </Can>
            </div>
          </div>
        ))}

        {broad.length > 0 && (
          <button
            type="button"
            onClick={() => setShowBroad((current) => !current)}
            className="text-sm font-medium text-blue-600 hover:underline"
          >
            {showBroad
              ? "Hide broad matches"
              : `Show ${broad.length} broad ${
                  broad.length === 1 ? "match" : "matches"
                }`}
          </button>
        )}

        {suggestions.length > 0 && <CrosswalkDisclaimer />}
      </div>
    </div>
  );
}
