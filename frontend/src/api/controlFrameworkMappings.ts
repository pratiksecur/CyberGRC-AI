import api from "./axios";

import type { Control } from "./controls";
import type { FrameworkControl } from "./frameworkControls";

export interface ControlFrameworkMapping {
  id: number;
  control_id: number;
  framework_control_id: number;
  created_at: string;
}

export interface CreateControlFrameworkMappingRequest {
  control_id: number;
  framework_control_id: number;
}

export async function getFrameworkControlsForControl(
  controlId: number
): Promise<FrameworkControl[]> {
  const response = await api.get(
    `/control-framework-controls/control/${controlId}`
  );

  return response.data;
}

export async function getControlsForFrameworkControl(
  frameworkControlId: number
): Promise<Control[]> {
  const response = await api.get(
    `/control-framework-controls/framework-control/${frameworkControlId}`
  );

  return response.data;
}

export async function createControlFrameworkMapping(
  data: CreateControlFrameworkMappingRequest
): Promise<ControlFrameworkMapping> {
  const response = await api.post(
    "/control-framework-controls/",
    data
  );

  return response.data;
}

export async function deleteControlFrameworkMapping(
  mappingId: number
): Promise<void> {
  await api.delete(
    `/control-framework-controls/${mappingId}`
  );
}