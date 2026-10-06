import api from "@/api/axios";

export interface AIGRCAnalystResponse {
  question: string;
  category: string;
  analysis: string;
  recommendations: string[];
  supporting_signals: {
    risk_summary?: Record<string, unknown>;
    control_summary?: Record<string, unknown>;
    evidence_summary?: Record<string, unknown>;
    finding_summary?: Record<string, unknown>;
    corrective_action_summary?: Record<string, unknown>;
    regulatory_summary?: Record<string, unknown>;
    control_intelligence_summary?: Record<
      string,
      unknown
    >;
  };
  human_decision_required: boolean;
  generated_at: string;
}

export async function askAIGRCAnalyst(
  question: string
): Promise<AIGRCAnalystResponse> {
  const response = await api.post(
    "/ai/grc-analyst",
    {
      question,
    }
  );

  return response.data;
}