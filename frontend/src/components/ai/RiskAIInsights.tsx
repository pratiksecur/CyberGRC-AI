import { useNavigate } from "react-router-dom";
import {
  Brain,
  CheckCircle2,
  Loader2,
  Sparkles,
  ShieldCheck,
} from "lucide-react";

import Can from "@/components/auth/Can";

import { Button } from "@/components/ui/button";

import { useAnalyzeRisk } from "@/hooks/useAnalyzeRisk";
import { useRecommendControls } from "@/hooks/useRecommendControls";


interface RiskAIInsightsProps {
  riskId: number;
}


function priorityClass(priority: string) {
  switch (priority) {
    case "Critical":
      return "bg-red-100 text-red-700";

    case "High":
      return "bg-orange-100 text-orange-700";

    case "Medium":
      return "bg-yellow-100 text-yellow-700";

    case "Low":
      return "bg-green-100 text-green-700";

    default:
      return "bg-slate-100 text-slate-700";
  }
}


export default function RiskAIInsights({
  riskId,
}: RiskAIInsightsProps) {
  const navigate = useNavigate();

  const {
    mutate: analyzeRisk,
    data: analysis,
    isPending: analysisLoading,
    error: analysisError,
    reset: resetAnalysis,
  } = useAnalyzeRisk();

  const {
    mutate: recommendControls,
    data: recommendations,
    isPending: recommendationsLoading,
    error: recommendationsError,
    reset: resetRecommendations,
  } = useRecommendControls();


  const handleAnalyze = () => {
    resetAnalysis();

    analyzeRisk(riskId);
  };


  const handleRecommendControls = () => {
    resetRecommendations();

    recommendControls(riskId);
  };


  return (
    <Can
      resource="ai"
      action="use"
    >
      <section className="rounded-2xl border bg-white shadow-sm">

        {/* Header */}
        <div className="border-b p-6">

          <div className="flex items-start gap-3">

            <div className="rounded-xl bg-purple-50 p-3">
              <Brain className="h-6 w-6 text-purple-600" />
            </div>

            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                AI Risk Intelligence
              </h2>

              <p className="mt-1 text-sm leading-6 text-slate-500">
                Use governed AI to analyze this risk and identify
                relevant control recommendations.
              </p>

              <p className="mt-2 text-xs text-slate-400">
                AI output is advisory and does not automatically change
                GRC records.
              </p>
            </div>

          </div>

        </div>


        <div className="p-6">

          {/* Actions */}
          <div className="flex flex-wrap gap-3">

            <Button
              type="button"
              onClick={handleAnalyze}
              disabled={
                analysisLoading ||
                recommendationsLoading
              }
            >
              {analysisLoading ? (
                <Loader2
                  className="mr-2 h-4 w-4 animate-spin"
                />
              ) : (
                <Sparkles className="mr-2 h-4 w-4" />
              )}

              {analysisLoading
                ? "Analyzing Risk..."
                : "Analyze This Risk"}
            </Button>


            <Button
              type="button"
              variant="outline"
              onClick={handleRecommendControls}
              disabled={
                analysisLoading ||
                recommendationsLoading
              }
            >
              {recommendationsLoading ? (
                <Loader2
                  className="mr-2 h-4 w-4 animate-spin"
                />
              ) : (
                <ShieldCheck className="mr-2 h-4 w-4" />
              )}

              {recommendationsLoading
                ? "Analyzing Controls..."
                : "Recommend Controls"}
            </Button>

          </div>


          {/* Risk Analysis Loading */}
          {analysisLoading && (
            <div className="mt-6 rounded-xl border border-purple-200 bg-purple-50 p-5">

              <div className="flex items-center gap-3">

                <Sparkles className="h-5 w-5 animate-pulse text-purple-600" />

                <div>
                  <p className="font-medium text-purple-700">
                    AI is analyzing this risk...
                  </p>

                  <p className="mt-1 text-sm text-purple-600">
                    Evaluating likelihood, impact, and risk context.
                  </p>
                </div>

              </div>

            </div>
          )}


          {/* Risk Analysis Error */}
          {analysisError &&
            !analysisLoading && (
              <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-5">

                <p className="font-medium text-red-700">
                  Risk analysis failed.
                </p>

                <p className="mt-1 text-sm text-red-600">
                  The AI service could not analyze this risk.
                  Please try again.
                </p>

                <button
                  type="button"
                  onClick={handleAnalyze}
                  className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
                >
                  Retry Analysis
                </button>

              </div>
            )}


          {/* Risk Analysis Result */}
          {analysis &&
            !analysisLoading && (
              <div className="mt-6 space-y-5 rounded-xl border bg-slate-50 p-5">

                <div className="flex items-center gap-2">
                  <Sparkles
                    size={18}
                    className="text-purple-600"
                  />

                  <h3 className="font-semibold text-slate-900">
                    AI Risk Assessment
                  </h3>
                </div>


                {/* Metrics */}
                <div className="grid gap-4 sm:grid-cols-3">

                  <div className="rounded-lg border bg-white p-4">
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                      Likelihood
                    </p>

                    <p className="mt-1 font-semibold text-slate-900">
                      {analysis.likelihood}
                    </p>
                  </div>


                  <div className="rounded-lg border bg-white p-4">
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                      Impact
                    </p>

                    <p className="mt-1 font-semibold text-slate-900">
                      {analysis.impact}
                    </p>
                  </div>


                  <div className="rounded-lg border bg-white p-4">
                    <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                      AI Risk Score
                    </p>

                    <p className="mt-1 text-2xl font-bold text-red-600">
                      {analysis.risk_score}
                    </p>
                  </div>

                </div>


                {/* Assessment */}
                <div className="rounded-lg border bg-white p-5">

                  <h4 className="font-semibold text-slate-900">
                    Assessment
                  </h4>

                  <p className="mt-2 leading-7 text-slate-600">
                    {analysis.summary}
                  </p>

                </div>


                {/* Recommended Controls */}
                <div>

                  <h4 className="mb-3 font-semibold text-slate-900">
                    Recommended Controls
                  </h4>

                  <div className="space-y-2">

                    {analysis.recommended_controls.map(
                      (control, index) => (
                        <div
                          key={`${control}-${index}`}
                          className="flex gap-3 rounded-lg border bg-white p-3"
                        >
                          <CheckCircle2
                            size={17}
                            className="mt-0.5 shrink-0 text-emerald-600"
                          />

                          <span className="text-sm leading-6 text-slate-600">
                            {control}
                          </span>
                        </div>
                      )
                    )}

                  </div>

                </div>

              </div>
            )}


          {/* Control Recommendation Loading */}
          {recommendationsLoading && (
            <div className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 p-5">

              <div className="flex items-center gap-3">

                <ShieldCheck className="h-5 w-5 animate-pulse text-emerald-600" />

                <div>
                  <p className="font-medium text-emerald-700">
                    AI is evaluating available controls...
                  </p>

                  <p className="mt-1 text-sm text-emerald-600">
                    Comparing this risk against your authorized control library.
                  </p>
                </div>

              </div>

            </div>
          )}


          {/* Control Recommendation Error */}
          {recommendationsError &&
            !recommendationsLoading && (
              <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-5">

                <p className="font-medium text-red-700">
                  Control recommendation failed.
                </p>

                <p className="mt-1 text-sm text-red-600">
                  The AI service could not generate control recommendations.
                </p>

                <button
                  type="button"
                  onClick={handleRecommendControls}
                  className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
                >
                  Retry Recommendations
                </button>

              </div>
            )}


          {/* Control Recommendations */}
          {recommendations &&
            !recommendationsLoading && (
              <div className="mt-6 space-y-5">

                <div className="rounded-xl border bg-slate-50 p-5">

                  <div className="flex items-center gap-2">
                    <Sparkles
                      size={18}
                      className="text-emerald-600"
                    />

                    <h3 className="font-semibold text-slate-900">
                      AI Control Assessment
                    </h3>
                  </div>

                  <p className="mt-2 leading-7 text-slate-600">
                    {recommendations.overall_assessment}
                  </p>

                </div>


                <div className="rounded-xl border bg-white p-5">

                  <h3 className="font-semibold text-slate-900">
                    Existing Controls Assessment
                  </h3>

                  <p className="mt-2 leading-7 text-slate-600">
                    {recommendations.existing_controls_assessment}
                  </p>

                </div>


                {/* Existing Controls */}
                {recommendations
                  .recommended_existing_controls
                  .length > 0 && (
                    <div>

                      <h3 className="mb-3 text-sm font-semibold text-slate-900">
                        Recommended Existing Controls
                      </h3>

                      <div className="space-y-3">

                        {recommendations
                          .recommended_existing_controls
                          .map((control, index) => (
                            <div
                              key={`${control.control_name}-${index}`}
                              className="rounded-xl border bg-white p-4"
                            >

                              <div className="flex items-start justify-between gap-4">

                                <div className="min-w-0">

                                  <div className="flex items-start gap-2">

                                    <CheckCircle2
                                      size={17}
                                      className="mt-0.5 shrink-0 text-emerald-600"
                                    />

                                    <p className="font-medium text-slate-900">
                                      {control.control_name}
                                    </p>

                                  </div>

                                  <p className="mt-2 text-sm leading-6 text-slate-600">
                                    {control.reason}
                                  </p>

                                </div>

                                <span
                                  className={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold ${priorityClass(
                                    control.priority
                                  )}`}
                                >
                                  {control.priority}
                                </span>

                              </div>


                              <div className="mt-3 flex flex-wrap items-center gap-2 text-xs">

                                {control.control_id !== null && (
                                  <>
                                    <span className="rounded bg-slate-100 px-2 py-1 text-slate-600">
                                      Control #{control.control_id}
                                    </span>

                                    <button
                                      type="button"
                                      onClick={() =>
                                        navigate(
                                          `/controls/${control.control_id}`
                                        )
                                      }
                                      className="rounded bg-indigo-50 px-2 py-1 font-medium text-indigo-700 transition hover:bg-indigo-100"
                                    >
                                      View Control
                                    </button>
                                  </>
                                )}

                                <span className="rounded bg-slate-100 px-2 py-1 text-slate-600">
                                  Confidence{" "}
                                  {Math.round(
                                    control.confidence * 100
                                  )}
                                  %
                                </span>

                                {control.already_exists && (
                                  <span className="rounded bg-emerald-100 px-2 py-1 font-medium text-emerald-700">
                                    Already Exists
                                  </span>
                                )}

                              </div>

                            </div>
                          ))}

                      </div>

                    </div>
                  )}


                {/* New Controls */}
                {recommendations
                  .recommended_new_controls
                  .length > 0 && (
                    <div>

                      <h3 className="mb-3 text-sm font-semibold text-slate-900">
                        Recommended New Controls
                      </h3>

                      <div className="space-y-3">

                        {recommendations
                          .recommended_new_controls
                          .map((control, index) => (
                            <div
                              key={`${control.control_name}-${index}`}
                              className="rounded-xl border bg-white p-4"
                            >

                              <div className="flex items-start justify-between gap-4">

                                <div className="min-w-0">

                                  <div className="flex items-start gap-2">

                                    <ShieldCheck
                                      size={17}
                                      className="mt-0.5 shrink-0 text-blue-600"
                                    />

                                    <p className="font-medium text-slate-900">
                                      {control.control_name}
                                    </p>

                                  </div>

                                  <p className="mt-2 text-sm leading-6 text-slate-600">
                                    {control.reason}
                                  </p>

                                </div>

                                <span
                                  className={`shrink-0 rounded-full px-3 py-1 text-xs font-semibold ${priorityClass(
                                    control.priority
                                  )}`}
                                >
                                  {control.priority}
                                </span>

                              </div>


                              <div className="mt-3 flex flex-wrap gap-2 text-xs">

                                <span className="rounded bg-slate-100 px-2 py-1 text-slate-600">
                                  Confidence{" "}
                                  {Math.round(
                                    control.confidence * 100
                                  )}
                                  %
                                </span>

                                <span className="rounded bg-blue-100 px-2 py-1 font-medium text-blue-700">
                                  New Control Recommendation
                                </span>

                              </div>

                            </div>
                          ))}

                      </div>

                    </div>
                  )}

              </div>
            )}

        </div>

      </section>
    </Can>
  );
}