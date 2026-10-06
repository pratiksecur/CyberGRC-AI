import api from "./axios";


// ==========================================================
// INTELLIGENCE EVIDENCE
// ==========================================================

export interface IntelligenceEvidence {
  id: number;
  control_id: number;
  title: string;
  file_name: string;
}


// ==========================================================
// INTELLIGENCE FRAMEWORK
// ==========================================================

export interface IntelligenceFramework {
  id: number;
  name: string;
  version: string;
  control_code: string;
}


// ==========================================================
// INTELLIGENCE ACTION
// ==========================================================

export interface IntelligenceAction {
  id: number;
  finding_id: number;
  title: string;
  priority: string;
  status: string | null;
  assigned_to: number;
  due_date: string;
  overdue: boolean;
}


// ==========================================================
// INTELLIGENCE FINDING
// ==========================================================

export interface IntelligenceFinding {
  id: number;
  audit_id: number;
  control_id: number;
  title: string;
  severity: string;
  status: string | null;
  actions: IntelligenceAction[];
}


// ==========================================================
// INTELLIGENCE CONTROL
// ==========================================================

export interface IntelligenceControl {
  id: number;
  title: string;
  status: string | null;
  effectiveness: number;
  evidence: IntelligenceEvidence[];
  frameworks: IntelligenceFramework[];
  findings: IntelligenceFinding[];
}


// ==========================================================
// RISK INTELLIGENCE METRICS
// ==========================================================

export interface RiskIntelligenceMetrics {
  control_count: number;

  controls_with_evidence: number;
  evidence_coverage_percent: number;

  average_control_effectiveness: number;

  framework_count: number;

  finding_count: number;
  open_findings: number;
  critical_findings: number;

  action_count: number;
  open_actions: number;
  overdue_actions: number;

  remediation_completion_percent: number;

  estimated_residual_risk: number;
}


// ==========================================================
// RISK INTELLIGENCE RESPONSE
// ==========================================================

export interface RiskIntelligenceResponse {
  risk_id: number;
  risk_title: string;
  risk_score: number;
  risk_status: string | null;
  owner_id: number;

  metrics: RiskIntelligenceMetrics;

  controls: IntelligenceControl[];
}


// ==========================================================
// OVERVIEW METRICS
// ==========================================================

export interface GRCIntelligenceOverviewMetrics {
  total_risks: number;
  critical_risks: number;

  risks_with_controls: number;
  risks_with_evidence: number;

  total_findings: number;
  open_findings: number;
  critical_findings: number;

  total_actions: number;
  open_actions: number;
  overdue_actions: number;

  remediation_completion_percent: number;
}


// ==========================================================
// OVERVIEW RESPONSE
// ==========================================================

export interface GRCIntelligenceOverviewResponse {
  metrics: GRCIntelligenceOverviewMetrics;
  risks: RiskIntelligenceResponse[];
}


// ==========================================================
// API
// ==========================================================

export async function getGRCIntelligenceOverview(): Promise<GRCIntelligenceOverviewResponse> {
  const response = await api.get(
    "/intelligence/overview"
  );

  return response.data;
}


export async function getRiskIntelligence(
  riskId: number
): Promise<RiskIntelligenceResponse> {
  const response = await api.get(
    `/intelligence/risk/${riskId}`
  );

  return response.data;
}

// ==========================================================
// GRC KNOWLEDGE GRAPH
// ==========================================================

export interface KnowledgeGraphNode {
  id: number;

  node_type: string;

  label: string;

  status: string | null;

  metadata: Record<
    string,
    unknown
  >;
}


export interface KnowledgeGraphEdge {
  source_id: number;

  source_type: string;

  target_id: number;

  target_type: string;

  relation: string;
}


export interface KnowledgeGraphSummary {
  total_nodes: number;

  total_edges: number;

  node_counts: Record<
    string,
    number
  >;

  edge_counts: Record<
    string,
    number
  >;

  risks_with_controls: number;

  controls_with_evidence: number;

  controls_with_frameworks: number;

  findings_with_actions: number;

  risks_with_treatments: number;

  risks_with_decisions: number;

  risks_with_workflows: number;

  disconnected_nodes: number;
}


export interface KnowledgeGraphResponse {
  focus_risk_id: number | null;

  nodes: KnowledgeGraphNode[];

  edges: KnowledgeGraphEdge[];

  summary: KnowledgeGraphSummary;

  generated_at: string;
}


export async function getKnowledgeGraph(
  riskId?: number
): Promise<KnowledgeGraphResponse> {
  const response = await api.get(
    "/intelligence/knowledge-graph",
    {
      params:
        riskId !== undefined
          ? {
              risk_id: riskId,
            }
          : undefined,
    }
  );

  return response.data;
}