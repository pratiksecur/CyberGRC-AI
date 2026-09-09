export type UserRole =
  | "Admin"
  | "Employee"
  | "GRC Manager"
  | "Risk Analyst"
  | "Auditor";

export type PermissionAction =
  | "view"
  | "create"
  | "update"
  | "delete"
  | "use";

export type PermissionResource =
  | "users"
  | "risks"
  | "controls"
  | "frameworks"
  | "framework_controls"
  | "control_framework_mappings"
  | "evidence"
  | "audits"
  | "audit_findings"
  | "corrective_actions"
  | "reports"
  | "ai";

type PermissionMap = Partial<
  Record<
    PermissionResource,
    PermissionAction[]
  >
>;

export const ROLE_PERMISSIONS: Record<
  UserRole,
  PermissionMap
> = {
  Admin: {
    users: [
      "view",
      "create",
      "update",
      "delete",
    ],
    risks: [
      "view",
      "create",
      "update",
      "delete",
    ],
    controls: [
      "view",
      "create",
      "update",
      "delete",
    ],
    frameworks: [
      "view",
      "create",
      "update",
      "delete",
    ],
    framework_controls: [
      "view",
      "create",
      "update",
      "delete",
    ],
    control_framework_mappings: [
      "view",
      "create",
      "delete",
    ],
    evidence: [
      "view",
      "create",
      "update",
      "delete",
    ],
    audits: [
      "view",
      "create",
      "update",
      "delete",
    ],
    audit_findings: [
      "view",
      "create",
      "update",
      "delete",
    ],
    corrective_actions: [
      "view",
      "create",
      "update",
      "delete",
    ],
    reports: [
      "view",
      "create",
    ],
    ai: [
      "view",
      "use",
    ],
  },

  "GRC Manager": {
    users: [
      "view",
    ],
    risks: [
      "view",
      "create",
      "update",
    ],
    controls: [
      "view",
      "create",
      "update",
    ],
    frameworks: [
      "view",
      "create",
      "update",
      "delete",
    ],
    framework_controls: [
      "view",
      "create",
      "update",
      "delete",
    ],
    control_framework_mappings: [
      "view",
      "create",
      "delete",
    ],
    evidence: [
      "view",
      "create",
      "update",
    ],
    audits: [
      "view",
      "create",
      "update",
    ],
    audit_findings: [
      "view",
      "create",
      "update",
    ],
    corrective_actions: [
      "view",
      "create",
      "update",
    ],
    reports: [
      "view",
      "create",
    ],
    ai: [
      "view",
      "use",
    ],
  },

  "Risk Analyst": {
    risks: [
      "view",
      "create",
      "update",
    ],
    controls: [
      "view",
      "create",
      "update",
    ],
    frameworks: [
      "view",
    ],
    framework_controls: [
      "view",
    ],
    control_framework_mappings: [
      "view",
      "create",
    ],
    evidence: [
      "view",
      "create",
      "update",
    ],
    audits: [
      "view",
    ],
    audit_findings: [
      "view",
    ],
    corrective_actions: [
      "view",
    ],
    reports: [
      "view",
    ],
  },

  Auditor: {
    risks: [
      "view",
    ],
    controls: [
      "view",
    ],
    frameworks: [
      "view",
    ],
    framework_controls: [
      "view",
    ],
    control_framework_mappings: [
      "view",
    ],
    evidence: [
      "view",
      "create",
      "update",
    ],
    audits: [
      "view",
      "create",
      "update",
    ],
    audit_findings: [
      "view",
      "create",
      "update",
    ],
    corrective_actions: [
      "view",
      "create",
      "update",
    ],
    reports: [
      "view",
    ],
    ai: [
      "view",
      "use",
    ],
  },

  Employee: {
    risks: [
      "view",
      "create",
      "update",
    ],
    controls: [
      "view",
    ],
    frameworks: [
      "view",
    ],
    framework_controls: [
      "view",
    ],
    control_framework_mappings: [
      "view",
    ],
    evidence: [
      "view",
      "create",
      "update",
    ],
    audits: [
      "view",
    ],
    audit_findings: [
      "view",
    ],
    corrective_actions: [
      "view",
      "update",
    ],
  },
};

export function hasPermission(
  role: string | undefined,
  resource: PermissionResource,
  action: PermissionAction
): boolean {
  if (!role) {
    return false;
  }

  const permissions =
    ROLE_PERMISSIONS[
      role as UserRole
    ];

  if (!permissions) {
    return false;
  }

  return (
    permissions[resource]?.includes(
      action
    ) ?? false
  );
}