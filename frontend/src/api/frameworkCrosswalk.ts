import api from "./axios";

/*
 * Cross-framework crosswalk.
 *
 * These endpoints only read. They suggest requirements in other frameworks
 * that relate to a requirement or that a control may also support. A person
 * reviews each suggestion and applies it through the normal mapping call.
 */

export type CrosswalkConfidence = "direct" | "broad";

export interface CrosswalkTheme {
  key: string;
  label: string;
}

export interface CrosswalkRequirement {
  framework_control_id: number;
  control_code: string;
  title: string;
  framework_id: number;
  framework_name: string;
}

export interface CrosswalkRelatedRequirement
  extends CrosswalkRequirement {
  shared_themes: CrosswalkTheme[];
  confidence: CrosswalkConfidence;
  mapped_control_count: number;
}

export interface CrosswalkRelatedResponse {
  requirement: CrosswalkRequirement;
  themes: CrosswalkTheme[];
  in_crosswalk: boolean;
  is_umbrella: boolean;
  related: CrosswalkRelatedRequirement[];
}

export interface CrosswalkSuggestion extends CrosswalkRequirement {
  shared_themes: CrosswalkTheme[];
  confidence: CrosswalkConfidence;
  because_of: CrosswalkRequirement[];
}

export interface CrosswalkSuggestionsResponse {
  control_id: number;
  mapped_requirement_count: number;
  suggestions: CrosswalkSuggestion[];
}

export interface CrosswalkCandidateControl {
  control_id: number;
  control_title: string;
  confidence: CrosswalkConfidence;
  shared_themes: CrosswalkTheme[];
  via: CrosswalkRequirement[];
}

export interface CrosswalkOpportunity extends CrosswalkRequirement {
  best_confidence: CrosswalkConfidence;
  candidates: CrosswalkCandidateControl[];
}

export interface CrosswalkFrameworkSummary {
  framework_id: number;
  framework_name: string;
  requirement_count: number;
  unmapped_requirements: number;
  opportunities: number;
}

export interface CrosswalkOpportunitiesResponse {
  generated_at: string;
  total_requirements: number;
  unmapped_requirements: number;
  opportunity_count: number;
  direct_opportunity_count: number;
  frameworks: CrosswalkFrameworkSummary[];
  opportunities: CrosswalkOpportunity[];
  disclaimer: string;
}

export async function getRelatedRequirements(
  frameworkControlId: number
): Promise<CrosswalkRelatedResponse> {
  const response = await api.get(
    `/framework-crosswalk/framework-control/${frameworkControlId}/related`
  );

  return response.data;
}

export async function getCrosswalkSuggestions(
  controlId: number
): Promise<CrosswalkSuggestionsResponse> {
  const response = await api.get(
    `/framework-crosswalk/control/${controlId}/suggestions`
  );

  return response.data;
}

export async function getCrosswalkOpportunities(): Promise<CrosswalkOpportunitiesResponse> {
  const response = await api.get(
    "/framework-crosswalk/opportunities"
  );

  return response.data;
}
