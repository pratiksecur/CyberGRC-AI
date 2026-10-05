import api from "./axios";


export interface Evidence {
  id: number;
  control_id: number;
  title: string;
  description: string;
  file_name: string;
  file_path: string;
  uploaded_by: number;
  uploaded_at: string;
}


export interface CreateEvidenceRequest {
  control_id: number;
  title: string;
  description: string;
  file_name: string;
  file_path: string;
  uploaded_by: number;
}


export interface EvidenceIntelligenceItem {
  evidence_id: number;
  control_id: number;
  risk_ids: number[];

  age_days: number | null;

  freshness: string;
  freshness_score: number;

  completeness: string;
  completeness_score: number;

  quality: string;
  quality_score: number;

  quality_indicators: string[];

  evidence_to_control_mapped: boolean;
  evidence_to_risk_mapped: boolean;

  file_available: boolean;
}


export interface MissingEvidence {
  control_id: number;
  control_title: string;
  priority: string;
  reason: string;
  recommended_action: string;
}


export interface EvidenceCollectionWorkflow {
  control_id: number;
  control_title: string;
  priority: string;
  workflow_type: string;
  status: string;
  recommended_action: string;
}


export interface EvidenceCoverage {
  total_controls: number;
  controls_with_evidence: number;
  controls_without_evidence: number;
  coverage_percent: number;

  total_evidence: number;
  fresh_evidence: number;
  aging_evidence: number;
  stale_evidence: number;

  risk_mapped_evidence: number;

  average_quality_score: number;
  average_completeness_score: number;

  audit_readiness_score: number;
  audit_ready: boolean;
}


export interface EvidenceIntelligence {
  coverage: EvidenceCoverage;

  evidence: EvidenceIntelligenceItem[];

  missing_evidence: MissingEvidence[];

  collection_workflows: EvidenceCollectionWorkflow[];

  audit_package_evidence_ids: number[];
}


export async function getEvidence(): Promise<Evidence[]> {
  const response = await api.get(
    "/evidence/"
  );

  return response.data;
}


export async function getEvidenceById(
  id: number
): Promise<Evidence> {
  const response = await api.get(
    `/evidence/${id}`
  );

  return response.data;
}


export async function getEvidenceIntelligence(): Promise<EvidenceIntelligence> {
  const response = await api.get(
    "/evidence/intelligence"
  );

  return response.data;
}


export async function createEvidence(
  data: FormData
): Promise<Evidence> {
  const response = await api.post(
    "/evidence/",
    data
  );

  return response.data;
}


export async function updateEvidence(
  id: number,
  data: Partial<CreateEvidenceRequest>
): Promise<Evidence> {
  const response = await api.patch(
    `/evidence/${id}`,
    data
  );

  return response.data;
}


export async function deleteEvidence(
  id: number
): Promise<void> {
  await api.delete(
    `/evidence/${id}`
  );
}


export async function downloadEvidence(
  id: number
): Promise<Blob> {
  const response = await api.get(
    `/evidence/${id}/file`,
    {
      params: {
        download: true,
      },
      responseType: "blob",
    }
  );

  return response.data;
}


export async function openEvidence(
  id: number
): Promise<void> {
  const response = await api.get(
    `/evidence/${id}/file`,
    {
      params: {
        download: false,
      },
      responseType: "blob",
    }
  );

  const objectUrl =
    URL.createObjectURL(response.data);

  const newWindow = window.open(
    objectUrl,
    "_blank",
    "noopener,noreferrer"
  );

  if (!newWindow) {
    URL.revokeObjectURL(objectUrl);

    throw new Error(
      "Unable to open the evidence file. Please allow pop-ups for this site."
    );
  }

  setTimeout(() => {
    URL.revokeObjectURL(objectUrl);
  }, 60_000);
}