import api from "./axios";

export interface AuditLogEntry {
  id: number;
  actor_id: number | null;
  actor_email: string | null;
  action: string;
  entity_type: string;
  entity_id: string | null;
  summary: string;
  details: {
    values?: Record<string, unknown>;
    changes?: Record<
      string,
      { from?: unknown; to?: unknown }
    >;
  } | null;
  ip_address: string | null;
  created_at: string;
}

export interface AuditLogPage {
  items: AuditLogEntry[];
  total: number;
  limit: number;
  offset: number;
}

export interface AuditLogFilters {
  entity_types: string[];
  actions: string[];
}

export interface AuditLogQuery {
  limit: number;
  offset: number;
  entity_type?: string;
  action?: string;
}

export async function getAuditLogs(
  query: AuditLogQuery
): Promise<AuditLogPage> {
  const response = await api.get("/audit-logs/", {
    params: {
      limit: query.limit,
      offset: query.offset,
      entity_type: query.entity_type || undefined,
      action: query.action || undefined,
    },
  });

  return response.data;
}

export async function getAuditLogFilters(): Promise<AuditLogFilters> {
  const response = await api.get("/audit-logs/filters");

  return response.data;
}