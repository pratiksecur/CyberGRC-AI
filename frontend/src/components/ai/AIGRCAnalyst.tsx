import { useState } from "react";

import {
  AlertTriangle,
  Brain,
  CheckCircle2,
  Loader2,
  Send,
  ShieldAlert,
} from "lucide-react";

import {
  useAIGRCAnalyst,
} from "@/hooks/useAIGRCAnalyst";


const SUGGESTED_QUESTIONS = [
  "What are our biggest unresolved compliance risks?",
  "Which controls are ineffective?",
  "Where are we missing important evidence?",
  "Why has our compliance posture deteriorated?",
  "Which risks are affected by control failures?",
  "What are our most important regulatory gaps?",
];


function formatCategory(
  value: string
) {
  return value
    .replace(/_/g, " ")
    .toLowerCase()
    .replace(
      /\b\w/g,
      (character) =>
        character.toUpperCase()
    );
}


export default function AIGRCAnalyst() {
  const [question, setQuestion] =
    useState("");

  const analyst = useAIGRCAnalyst();

  function submit() {
    const trimmed = question.trim();

    if (!trimmed) {
      return;
    }

    analyst.mutate(trimmed);
  }

  return (
    <section className="space-y-6">
      <div className="rounded-2xl border bg-white p-6 shadow-sm">
        <div className="flex items-start gap-4">
          <div className="rounded-xl bg-indigo-50 p-3">
            <Brain className="h-6 w-6 text-indigo-600" />
          </div>

          <div>
            <h2 className="text-xl font-semibold text-slate-900">
              AI GRC Analyst
            </h2>

            <p className="mt-1 text-sm text-slate-500">
              Ask questions about risks, controls,
              evidence, findings, and regulatory
              posture.
            </p>
          </div>
        </div>

        <div className="mt-6 flex flex-wrap gap-2">
          {SUGGESTED_QUESTIONS.map(
            (suggestion) => (
              <button
                key={suggestion}
                type="button"
                onClick={() =>
                  setQuestion(suggestion)
                }
                className="rounded-full border px-3 py-2 text-xs text-slate-600 transition hover:bg-slate-50"
              >
                {suggestion}
              </button>
            )
          )}
        </div>

        <div className="mt-6 flex gap-3">
          <textarea
            value={question}
            onChange={(event) =>
              setQuestion(event.target.value)
            }
            onKeyDown={(event) => {
              if (
                event.key === "Enter" &&
                (event.ctrlKey ||
                  event.metaKey)
              ) {
                submit();
              }
            }}
            placeholder="Ask the AI GRC Analyst..."
            rows={4}
            className="min-h-[110px] flex-1 resize-y rounded-xl border border-slate-200 p-4 text-sm outline-none focus:border-indigo-400 focus:ring-2 focus:ring-indigo-100"
          />

          <button
            type="button"
            onClick={submit}
            disabled={
              analyst.isPending ||
              !question.trim()
            }
            className="flex h-fit items-center gap-2 rounded-xl bg-slate-900 px-4 py-3 text-sm font-medium text-white transition hover:bg-slate-800 disabled:cursor-not-allowed disabled:opacity-50"
          >
            {analyst.isPending ? (
              <Loader2 className="h-4 w-4 animate-spin" />
            ) : (
              <Send className="h-4 w-4" />
            )}

            Analyze
          </button>
        </div>

        {analyst.isError && (
          <div className="mt-4 rounded-xl border border-red-200 bg-red-50 p-4 text-sm text-red-700">
            {analyst.error.message ||
              "Unable to generate the GRC analysis."}
          </div>
        )}
      </div>

      {analyst.data && (
        <div className="space-y-6">
          <div className="rounded-2xl border bg-white p-6 shadow-sm">
            <div className="flex items-center justify-between gap-4">
              <div>
                <div className="text-xs font-medium uppercase tracking-wide text-slate-400">
                  Analysis Category
                </div>

                <div className="mt-1 text-sm font-semibold text-slate-900">
                  {formatCategory(
                    analyst.data.category
                  )}
                </div>
              </div>

              <div className="rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1 text-xs font-medium text-indigo-700">
                AI Analysis
              </div>
            </div>

            <div className="mt-6 whitespace-pre-wrap rounded-xl bg-slate-50 p-5 text-sm leading-7 text-slate-700">
              {analyst.data.analysis}
            </div>
          </div>

          <div className="grid gap-6 lg:grid-cols-2">
            <div className="rounded-2xl border bg-white p-6 shadow-sm">
              <div className="flex items-center gap-2">
                <ShieldAlert className="h-5 w-5 text-amber-600" />

                <h3 className="font-semibold text-slate-900">
                  Supporting GRC Signals
                </h3>
              </div>

              <div className="mt-5 space-y-3 text-sm">
                <Signal
                  label="Critical risks"
                  value={
                    analyst.data
                      .supporting_signals
                      .risk_summary
                      ?.critical
                  }
                />

                <Signal
                  label="High risks"
                  value={
                    analyst.data
                      .supporting_signals
                      .risk_summary
                      ?.high
                  }
                />

                <Signal
                  label="Ineffective controls"
                  value={
                    analyst.data
                      .supporting_signals
                      .control_summary
                      ?.ineffective
                  }
                />

                <Signal
                  label="Controls missing evidence"
                  value={
                    analyst.data
                      .supporting_signals
                      .control_summary
                      ?.missing_evidence
                  }
                />

                <Signal
                  label="Open findings"
                  value={
                    analyst.data
                      .supporting_signals
                      .finding_summary
                      ?.open
                  }
                />

                <Signal
                  label="Open corrective actions"
                  value={
                    analyst.data
                      .supporting_signals
                      .corrective_action_summary
                      ?.open
                  }
                />

                <Signal
                  label="Regulatory posture"
                  value={
                    analyst.data
                      .supporting_signals
                      .regulatory_summary
                      ?.overall_posture
                  }
                />
              </div>
            </div>

            <div className="rounded-2xl border bg-white p-6 shadow-sm">
              <div className="flex items-center gap-2">
                <CheckCircle2 className="h-5 w-5 text-emerald-600" />

                <h3 className="font-semibold text-slate-900">
                  Recommendations
                </h3>
              </div>

              {analyst.data.recommendations
                .length === 0 ? (
                <p className="mt-5 text-sm text-slate-500">
                  No explicit recommendations were
                  extracted from the analysis.
                </p>
              ) : (
                <div className="mt-5 space-y-3">
                  {analyst.data.recommendations.map(
                    (recommendation, index) => (
                      <div
                        key={`${index}-${recommendation}`}
                        className="rounded-xl border bg-slate-50 p-4 text-sm text-slate-700"
                      >
                        {recommendation}
                      </div>
                    )
                  )}
                </div>
              )}
            </div>
          </div>

          {analyst.data.human_decision_required && (
            <div className="flex items-start gap-3 rounded-2xl border border-amber-200 bg-amber-50 p-5">
              <AlertTriangle className="mt-0.5 h-5 w-5 shrink-0 text-amber-600" />

              <div>
                <div className="font-semibold text-amber-900">
                  Human decision required
                </div>

                <p className="mt-1 text-sm text-amber-800">
                  This analysis is advisory. The AI
                  does not perform remediation or
                  change GRC resources. Recommendations
                  must be reviewed and approved by an
                  authorized human.
                </p>
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  );
}


function Signal({
  label,
  value,
}: {
  label: string;
  value: unknown;
}) {
  return (
    <div className="flex items-center justify-between rounded-lg border bg-slate-50 px-4 py-3">
      <span className="text-slate-600">
        {label}
      </span>

      <span className="font-semibold text-slate-900">
        {value === null ||
        value === undefined
          ? "—"
          : String(value)}
      </span>
    </div>
  );
}