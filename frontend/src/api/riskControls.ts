import api from "./axios";

import type { Risk } from "./risks";
import type { Control } from "./controls";

export interface RiskControlMapping {
  id: number;
  risk_id: number;
  control_id: number;
  created_at: string;
}

export interface CreateRiskControlMappingRequest {
  risk_id: number;
  control_id: number;
}

export async function getRisksForControl(
  controlId: number
): Promise<Risk[]> {
  const response = await api.get(
    `/risk-controls/control/${controlId}`
  );

  return response.data;
}

export async function getControlsForRisk(
  riskId: number
): Promise<Control[]> {
  const response = await api.get(
    `/risk-controls/risk/${riskId}`
  );

  return response.data;
}

export async function createRiskControlMapping(
  data: CreateRiskControlMappingRequest
): Promise<RiskControlMapping> {
  const response = await api.post(
    "/risk-controls/",
    data
  );

  return response.data;
}

export async function deleteRiskControlMapping(
  mappingId: number
): Promise<void> {
  await api.delete(
    `/risk-controls/${mappingId}`
  );
}