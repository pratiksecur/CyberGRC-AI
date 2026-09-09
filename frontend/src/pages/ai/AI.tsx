import { useState } from "react";

import AppLayout from "@/layouts/AppLayout";

import { useExecutiveSummary } from "@/hooks/useExecutiveSummary";
import { useRisks } from "@/hooks/useRisks";
import { useAudits } from "@/hooks/useAudits";
import { useAnalyzeRisk } from "@/hooks/useAnalyzeRisk";
import { useRecommendControls } from "@/hooks/useRecommendControls";
import { useAuditAISummary } from "@/hooks/useAuditAISummary";

import { useAuth } from "@/contexts/AuthContext";

import {
  hasPermission,
  type UserRole,
} from "@/auth/permissions";

import {
  Brain,
  ShieldAlert,
  ShieldCheck,
  ClipboardCheck,
  Sparkles,
  Loader2,
  CheckCircle2,
} from "lucide-react";


export default function AI() {

  const { user } = useAuth();

  const role =
    user?.role as UserRole | undefined;


  // ==================================================
  // PERMISSIONS
  // ==================================================

  const canViewExecutiveSummary =
    hasPermission(
      role,
      "ai_executive_summary",
      "view"
    );


  // ==================================================
  // EXECUTIVE SUMMARY
  // ==================================================

  const {
    data: executiveSummary,
    isLoading: summaryLoading,
    error: summaryError,
  } = useExecutiveSummary(
    canViewExecutiveSummary
  );


  // ==================================================
  // RISKS
  // ==================================================

  const {
    data: risks,
    isLoading: risksLoading,
  } = useRisks();


  // ==================================================
  // AUDITS
  // ==================================================

  const {
    data: audits,
    isLoading: auditsLoading,
  } = useAudits();


  // ==================================================
  // SELECTION STATE
  // ==================================================

  const [selectedRisk, setSelectedRisk] =
    useState("");

  const [selectedAudit, setSelectedAudit] =
    useState("");


  // ==================================================
  // RISK AI ANALYSIS
  // ==================================================

  const {
    mutate: analyzeRiskMutation,
    data: riskAnalysis,
    isPending: riskAnalysisLoading,
    error: riskAnalysisError,
    reset: resetRiskAnalysis,
  } = useAnalyzeRisk();


  // ==================================================
  // CONTROL AI RECOMMENDATIONS
  // ==================================================

  const {
    mutate: recommendControlsMutation,
    data: controlRecommendations,
    isPending: controlRecommendationsLoading,
    error: controlRecommendationsError,
    reset: resetControlRecommendations,
  } = useRecommendControls();


  // ==================================================
  // AUDIT AI SUMMARY
  // ==================================================

  const {
    mutate: summarizeAuditMutation,
    data: auditSummary,
    isPending: auditSummaryLoading,
    error: auditSummaryError,
    reset: resetAuditSummary,
  } = useAuditAISummary();


  // ==================================================
  // RENDER
  // ==================================================

  return (
    <AppLayout>

      <div className="space-y-8">


        {/* ==================================================
            HEADER
        ================================================== */}

        <div>

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-purple-100 p-3">

              <Brain className="h-7 w-7 text-purple-600" />

            </div>

            <div>

              <h1 className="text-3xl font-bold text-slate-900">
                AI Intelligence
              </h1>

              <p className="mt-1 text-slate-500">
                AI-powered cybersecurity intelligence and decision support.
              </p>

            </div>

          </div>

        </div>


        {/* ==================================================
            EXECUTIVE INTELLIGENCE

            ONLY GRC MANAGER / USERS WITH THE DEDICATED
            PERMISSION SEE THIS SECTION.
        ================================================== */}

        {canViewExecutiveSummary && (

          <section className="rounded-2xl border bg-white shadow-sm">

            <div className="border-b p-6">

              <div className="flex items-center gap-3">

                <div className="rounded-lg bg-purple-50 p-2">

                  <Sparkles className="h-5 w-5 text-purple-600" />

                </div>

                <div>

                  <h2 className="font-semibold text-slate-900">
                    Executive Intelligence
                  </h2>

                  <p className="text-sm text-slate-500">
                    AI-generated assessment of the organization's current cybersecurity posture.
                  </p>

                </div>

              </div>

            </div>


            <div className="p-6">

              {summaryLoading ? (

                <div className="space-y-4">

                  <div className="h-6 w-40 animate-pulse rounded bg-slate-200" />

                  <div className="h-20 animate-pulse rounded-lg bg-slate-100" />

                  <div className="grid gap-4 md:grid-cols-2">

                    <div className="h-24 animate-pulse rounded-lg bg-slate-100" />

                    <div className="h-24 animate-pulse rounded-lg bg-slate-100" />

                  </div>

                </div>

              ) : summaryError || !executiveSummary ? (

                <div className="rounded-lg border border-red-200 bg-red-50 p-5">

                  <p className="font-medium text-red-700">
                    Failed to generate executive intelligence.
                  </p>

                  <p className="mt-1 text-sm text-red-600">
                    Please try again later.
                  </p>

                </div>

              ) : (

                <div className="space-y-6">


                  {/* Risk Level */}

                  <div>

                    <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                      Organization Risk Level
                    </p>

                    <span className="mt-2 inline-flex rounded-full bg-red-100 px-4 py-2 text-sm font-semibold text-red-700">
                      {executiveSummary.organization_risk_level}
                    </span>

                  </div>


                  {/* Executive Summary */}

                  <div className="rounded-xl bg-slate-50 p-5">

                    <p className="mb-2 text-sm font-semibold text-slate-900">
                      Executive Summary
                    </p>

                    <p className="leading-7 text-slate-600">
                      {executiveSummary.executive_summary}
                    </p>

                  </div>


                  {/* Priorities + Next Steps */}

                  <div className="grid gap-6 md:grid-cols-2">


                    <div>

                      <h3 className="mb-3 text-sm font-semibold text-slate-900">
                        Top Priorities
                      </h3>

                      <ul className="space-y-2">

                        {executiveSummary.top_priorities.map(
                          (priority, index) => (

                            <li
                              key={index}
                              className="flex gap-3 rounded-lg border p-3 text-sm text-slate-600"
                            >

                              <span className="font-semibold text-purple-600">
                                {index + 1}.
                              </span>

                              <span>
                                {priority}
                              </span>

                            </li>

                          )
                        )}

                      </ul>

                    </div>


                    <div>

                      <h3 className="mb-3 text-sm font-semibold text-slate-900">
                        Recommended Next Steps
                      </h3>

                      <ul className="space-y-2">

                        {executiveSummary.recommended_next_steps.map(
                          (step, index) => (

                            <li
                              key={index}
                              className="flex gap-3 rounded-lg border p-3 text-sm text-slate-600"
                            >

                              <span className="font-semibold text-blue-600">
                                {index + 1}.
                              </span>

                              <span>
                                {step}
                              </span>

                            </li>

                          )
                        )}

                      </ul>

                    </div>

                  </div>

                </div>

              )}

            </div>

          </section>

        )}


        {/* ==================================================
            AI WORKSPACES
        ================================================== */}

        <div className="grid gap-6 lg:grid-cols-2">


          {/* ==================================================
              RISK INTELLIGENCE
          ================================================== */}

          <section className="rounded-2xl border bg-white p-6 shadow-sm">

            <div className="flex items-center gap-3">

              <div className="rounded-lg bg-red-50 p-2">

                <ShieldAlert className="h-5 w-5 text-red-600" />

              </div>

              <div>

                <h2 className="font-semibold text-slate-900">
                  Risk Intelligence
                </h2>

                <p className="text-sm text-slate-500">
                  Analyze an existing risk using AI.
                </p>

              </div>

            </div>


            <div className="mt-6">

              <label className="mb-2 block text-sm font-medium text-slate-700">
                Select Risk
              </label>


              <select
                value={selectedRisk}
                onChange={(e) => {

                  setSelectedRisk(e.target.value);

                  resetRiskAnalysis();

                  resetControlRecommendations();

                }}
                disabled={risksLoading}
                className="w-full rounded-lg border border-slate-200 bg-white p-3 outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 disabled:bg-slate-50"
              >

                <option value="">
                  {risksLoading
                    ? "Loading risks..."
                    : "Select a risk"}
                </option>

                {risks?.map((risk) => (

                  <option
                    key={risk.id}
                    value={risk.id}
                  >
                    {risk.title}
                  </option>

                ))}

              </select>


              {/* Analyze Button */}

              <button
                type="button"
                disabled={
                  !selectedRisk ||
                  riskAnalysisLoading
                }
                onClick={() => {

                  if (!selectedRisk) {
                    return;
                  }

                  analyzeRiskMutation(
                    Number(selectedRisk)
                  );

                }}
                className="mt-4 inline-flex items-center gap-2 rounded-lg bg-purple-600 px-5 py-3 font-medium text-white transition hover:bg-purple-700 disabled:cursor-not-allowed disabled:opacity-50"
              >

                {riskAnalysisLoading ? (

                  <Loader2
                    size={16}
                    className="animate-spin"
                  />

                ) : (

                  <Sparkles size={16} />

                )}

                {riskAnalysisLoading
                  ? "Analyzing..."
                  : "Analyze Risk"}

              </button>


              {/* Risk AI Loading */}

              {riskAnalysisLoading && (

                <div className="mt-6 rounded-xl border border-purple-200 bg-purple-50 p-5">

                  <div className="flex items-center gap-3">

                    <Sparkles className="h-5 w-5 animate-pulse text-purple-600" />

                    <div>

                      <p className="font-medium text-purple-700">
                        AI is analyzing this risk...
                      </p>

                      <p className="mt-1 text-sm text-purple-600">
                        This may take a few seconds.
                      </p>

                    </div>

                  </div>

                </div>

              )}


              {/* Risk AI Error */}

              {riskAnalysisError &&
                !riskAnalysisLoading && (

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
                      onClick={() => {

                        if (selectedRisk) {

                          analyzeRiskMutation(
                            Number(selectedRisk)
                          );

                        }

                      }}
                      className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
                    >
                      Retry Analysis
                    </button>

                  </div>

                )}


              {/* Risk AI Result */}

              {riskAnalysis &&
                !riskAnalysisLoading && (

                  <div className="mt-6 space-y-5 rounded-xl border bg-slate-50 p-5">

                    <div>

                      <div className="flex items-center gap-2">

                        <Sparkles className="h-5 w-5 text-purple-600" />

                        <h3 className="font-semibold text-slate-900">
                          AI Risk Analysis
                        </h3>

                      </div>

                      <p className="mt-1 text-sm text-slate-500">
                        AI-generated assessment of the selected risk.
                      </p>

                    </div>


                    {/* Risk Metrics */}

                    <div className="grid gap-4 sm:grid-cols-3">

                      <div className="rounded-lg border bg-white p-4">

                        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                          Likelihood
                        </p>

                        <p className="mt-1 font-semibold text-slate-900">
                          {riskAnalysis.likelihood}
                        </p>

                      </div>


                      <div className="rounded-lg border bg-white p-4">

                        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                          Impact
                        </p>

                        <p className="mt-1 font-semibold text-slate-900">
                          {riskAnalysis.impact}
                        </p>

                      </div>


                      <div className="rounded-lg border bg-white p-4">

                        <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                          Risk Score
                        </p>

                        <p className="mt-1 text-2xl font-bold text-red-600">
                          {riskAnalysis.risk_score}
                        </p>

                      </div>

                    </div>


                    {/* AI Assessment */}

                    <div className="rounded-lg border bg-white p-4">

                      <p className="text-sm font-semibold text-slate-900">
                        AI Assessment
                      </p>

                      <p className="mt-2 leading-7 text-slate-600">
                        {riskAnalysis.summary}
                      </p>

                    </div>


                    {/* Recommended Controls */}

                    <div>

                      <p className="mb-3 text-sm font-semibold text-slate-900">
                        Recommended Controls
                      </p>

                      {riskAnalysis.recommended_controls.length > 0 ? (

                        <ul className="space-y-2">

                          {riskAnalysis.recommended_controls.map(
                            (control, index) => (

                              <li
                                key={index}
                                className="flex gap-3 rounded-lg border bg-white p-3 text-sm text-slate-600"
                              >

                                <span className="font-semibold text-emerald-600">
                                  ✓
                                </span>

                                <span>
                                  {control}
                                </span>

                              </li>

                            )
                          )}

                        </ul>

                      ) : (

                        <div className="rounded-lg border bg-white p-4 text-sm text-slate-500">
                          No additional controls were recommended.
                        </div>

                      )}

                    </div>

                  </div>

                )}

            </div>

          </section>


          {/* ==================================================
              CONTROL INTELLIGENCE
          ================================================== */}

          <section className="rounded-2xl border bg-white p-6 shadow-sm">

            <div className="flex items-center gap-3">

              <div className="rounded-lg bg-emerald-50 p-2">

                <ShieldCheck className="h-5 w-5 text-emerald-600" />

              </div>

              <div>

                <h2 className="font-semibold text-slate-900">
                  Control Intelligence
                </h2>

                <p className="text-sm text-slate-500">
                  Discover controls recommended for a risk.
                </p>

              </div>

            </div>


            <div className="mt-6">

              <label className="mb-2 block text-sm font-medium text-slate-700">
                Select Risk
              </label>


              <select
                value={selectedRisk}
                onChange={(e) => {

                  setSelectedRisk(e.target.value);

                  resetControlRecommendations();

                }}
                disabled={risksLoading}
                className="w-full rounded-lg border border-slate-200 bg-white p-3 outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 disabled:bg-slate-50"
              >

                <option value="">
                  {risksLoading
                    ? "Loading risks..."
                    : "Select a risk"}
                </option>

                {risks?.map((risk) => (

                  <option
                    key={risk.id}
                    value={risk.id}
                  >
                    {risk.title}
                  </option>

                ))}

              </select>


              {/* Recommend Controls Button */}

              <button
                type="button"
                disabled={
                  !selectedRisk ||
                  controlRecommendationsLoading
                }
                onClick={() => {

                  if (!selectedRisk) {
                    return;
                  }

                  recommendControlsMutation(
                    Number(selectedRisk)
                  );

                }}
                className="mt-4 inline-flex items-center gap-2 rounded-lg bg-emerald-600 px-5 py-3 font-medium text-white transition hover:bg-emerald-700 disabled:cursor-not-allowed disabled:opacity-50"
              >

                {controlRecommendationsLoading ? (

                  <Loader2
                    size={16}
                    className="animate-spin"
                  />

                ) : (

                  <ShieldCheck size={16} />

                )}

                {controlRecommendationsLoading
                  ? "Analyzing Controls..."
                  : "Recommend Controls"}

              </button>


              {/* Control AI Loading */}

              {controlRecommendationsLoading && (

                <div className="mt-6 rounded-xl border border-emerald-200 bg-emerald-50 p-5">

                  <div className="flex items-center gap-3">

                    <Sparkles className="h-5 w-5 animate-pulse text-emerald-600" />

                    <div>

                      <p className="font-medium text-emerald-700">
                        AI is analyzing available controls...
                      </p>

                      <p className="mt-1 text-sm text-emerald-600">
                        Comparing the selected risk against your control library.
                      </p>

                    </div>

                  </div>

                </div>

              )}


              {/* Control AI Error */}

              {controlRecommendationsError &&
                !controlRecommendationsLoading && (

                  <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-5">

                    <p className="font-medium text-red-700">
                      Control recommendation failed.
                    </p>

                    <p className="mt-1 text-sm text-red-600">
                      The AI service could not generate control recommendations.
                    </p>

                    <button
                      type="button"
                      onClick={() => {

                        if (selectedRisk) {

                          recommendControlsMutation(
                            Number(selectedRisk)
                          );

                        }

                      }}
                      className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
                    >
                      Try Again
                    </button>

                  </div>

                )}


              {/* Control AI Results */}

              {controlRecommendations &&
                !controlRecommendationsLoading && (

                  <div className="mt-6 space-y-5">


                    {/* Overall Assessment */}

                    <div className="rounded-xl border bg-slate-50 p-5">

                      <div className="mb-2 flex items-center gap-2">

                        <Sparkles
                          size={18}
                          className="text-emerald-600"
                        />

                        <h3 className="font-semibold text-slate-900">
                          AI Control Assessment
                        </h3>

                      </div>

                      <p className="text-sm leading-6 text-slate-600">
                        {
                          controlRecommendations
                            .overall_assessment
                        }
                      </p>

                    </div>


                    {/* Existing Controls Assessment */}

                    <div className="rounded-xl border bg-white p-5">

                      <h3 className="mb-2 font-semibold text-slate-900">
                        Existing Controls Assessment
                      </h3>

                      <p className="text-sm leading-6 text-slate-600">
                        {
                          controlRecommendations
                            .existing_controls_assessment
                        }
                      </p>

                    </div>


                    {/* Recommended Existing Controls */}

                    {controlRecommendations
                      .recommended_existing_controls
                      .length > 0 && (

                      <div>

                        <h3 className="mb-3 text-sm font-semibold text-slate-900">
                          Recommended Existing Controls
                        </h3>

                        <div className="space-y-3">

                          {controlRecommendations
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

                                  <span className="shrink-0 rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-700">
                                    {control.priority}
                                  </span>

                                </div>


                                <div className="mt-3 flex flex-wrap gap-2 text-xs">

                                  {control.control_id !== null && (

                                    <span className="rounded bg-slate-100 px-2 py-1 text-slate-600">

                                      Control #{control.control_id}

                                    </span>

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


                    {/* Recommended New Controls */}

                    {controlRecommendations
                      .recommended_new_controls
                      .length > 0 && (

                      <div>

                        <h3 className="mb-3 text-sm font-semibold text-slate-900">
                          Recommended New Controls
                        </h3>

                        <div className="space-y-3">

                          {controlRecommendations
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

                                  <span className="shrink-0 rounded-full bg-orange-100 px-3 py-1 text-xs font-semibold text-orange-700">
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

                                  {!control.already_exists && (

                                    <span className="rounded bg-orange-100 px-2 py-1 font-medium text-orange-700">

                                      New Control

                                    </span>

                                  )}

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

        </div>


        {/* ==================================================
            AUDIT INTELLIGENCE
        ================================================== */}

        <section className="rounded-2xl border bg-white p-6 shadow-sm">

          <div className="flex items-center gap-3">

            <div className="rounded-lg bg-blue-50 p-2">

              <ClipboardCheck className="h-5 w-5 text-blue-600" />

            </div>

            <div>

              <h2 className="font-semibold text-slate-900">
                Audit Intelligence
              </h2>

              <p className="text-sm text-slate-500">
                Generate an AI-powered executive summary for an audit.
              </p>

            </div>

          </div>


          <div className="mt-6 max-w-2xl">

            <label className="mb-2 block text-sm font-medium text-slate-700">
              Select Audit
            </label>


            <select
              value={selectedAudit}
              onChange={(e) => {

                setSelectedAudit(e.target.value);

                resetAuditSummary();

              }}
              disabled={auditsLoading}
              className="w-full rounded-lg border border-slate-200 bg-white p-3 outline-none focus:border-purple-500 focus:ring-2 focus:ring-purple-100 disabled:bg-slate-50"
            >

              <option value="">
                {auditsLoading
                  ? "Loading audits..."
                  : "Select an audit"}
              </option>

              {audits?.map((audit) => (

                <option
                  key={audit.id}
                  value={audit.id}
                >
                  {audit.name}
                </option>

              ))}

            </select>


            {/* Generate Audit Summary */}

            <button
              type="button"
              disabled={
                !selectedAudit ||
                auditSummaryLoading
              }
              onClick={() => {

                if (!selectedAudit) {
                  return;
                }

                summarizeAuditMutation(
                  Number(selectedAudit)
                );

              }}
              className="mt-4 inline-flex items-center gap-2 rounded-lg bg-blue-600 px-5 py-3 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >

              {auditSummaryLoading ? (

                <Loader2
                  size={16}
                  className="animate-spin"
                />

              ) : (

                <ClipboardCheck size={16} />

              )}

              {auditSummaryLoading
                ? "Generating Summary..."
                : "Generate Audit Summary"}

            </button>


            {/* Audit AI Loading */}

            {auditSummaryLoading && (

              <div className="mt-6 rounded-xl border border-blue-200 bg-blue-50 p-5">

                <div className="flex items-center gap-3">

                  <Sparkles className="h-5 w-5 animate-pulse text-blue-600" />

                  <div>

                    <p className="font-medium text-blue-700">
                      AI is analyzing this audit...
                    </p>

                    <p className="mt-1 text-sm text-blue-600">
                      Reviewing audit findings and corrective actions.
                    </p>

                  </div>

                </div>

              </div>

            )}


            {/* Audit AI Error */}

            {auditSummaryError &&
              !auditSummaryLoading && (

                <div className="mt-6 rounded-xl border border-red-200 bg-red-50 p-5">

                  <p className="font-medium text-red-700">
                    Audit summary failed.
                  </p>

                  <p className="mt-1 text-sm text-red-600">
                    The AI service could not generate the audit summary.
                    Please try again.
                  </p>

                  <button
                    type="button"
                    onClick={() => {

                      if (selectedAudit) {

                        summarizeAuditMutation(
                          Number(selectedAudit)
                        );

                      }

                    }}
                    className="mt-3 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
                  >
                    Try Again
                  </button>

                </div>

              )}


            {/* Audit AI Result */}

            {auditSummary &&
              !auditSummaryLoading && (

                <div className="mt-6 space-y-5">


                  {/* Overall Assessment */}

                  <div className="rounded-xl border bg-slate-50 p-5">

                    <div className="mb-2 flex items-center gap-2">

                      <Sparkles
                        size={18}
                        className="text-blue-600"
                      />

                      <h3 className="font-semibold text-slate-900">
                        AI Audit Assessment
                      </h3>

                    </div>

                    <p className="text-sm leading-6 text-slate-600">
                      {auditSummary.overall_assessment}
                    </p>

                  </div>


                  {/* Audit Metrics */}

                  <div className="grid gap-4 sm:grid-cols-4">

                    <div className="rounded-lg border bg-white p-4">

                      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                        Critical Findings
                      </p>

                      <p className="mt-1 text-2xl font-bold text-red-600">
                        {auditSummary.critical_findings}
                      </p>

                    </div>


                    <div className="rounded-lg border bg-white p-4">

                      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                        Open Findings
                      </p>

                      <p className="mt-1 text-2xl font-bold text-orange-600">
                        {auditSummary.open_findings}
                      </p>

                    </div>


                    <div className="rounded-lg border bg-white p-4">

                      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                        Completed Actions
                      </p>

                      <p className="mt-1 text-2xl font-bold text-emerald-600">
                        {auditSummary.completed_actions}
                      </p>

                    </div>


                    <div className="rounded-lg border bg-white p-4">

                      <p className="text-xs font-medium uppercase tracking-wide text-slate-400">
                        Pending Actions
                      </p>

                      <p className="mt-1 text-2xl font-bold text-blue-600">
                        {auditSummary.pending_actions}
                      </p>

                    </div>

                  </div>


                  {/* Executive Summary */}

                  <div className="rounded-xl border bg-white p-5">

                    <h3 className="mb-2 font-semibold text-slate-900">
                      Executive Summary
                    </h3>

                    <p className="text-sm leading-7 text-slate-600">
                      {auditSummary.executive_summary}
                    </p>

                  </div>


                  {/* Priority Recommendations */}

                  {auditSummary.priority_recommendations.length > 0 && (

                    <div>

                      <h3 className="mb-3 text-sm font-semibold text-slate-900">
                        Priority Recommendations
                      </h3>

                      <ul className="space-y-2">

                        {auditSummary.priority_recommendations.map(
                          (recommendation, index) => (

                            <li
                              key={index}
                              className="flex gap-3 rounded-lg border bg-white p-3 text-sm text-slate-600"
                            >

                              <span className="font-semibold text-blue-600">
                                {index + 1}.
                              </span>

                              <span>
                                {recommendation}
                              </span>

                            </li>

                          )
                        )}

                      </ul>

                    </div>

                  )}

                </div>

              )}

          </div>

        </section>

      </div>

    </AppLayout>
  );
}