import {
  Activity,
  Brain,
  LayoutDashboard,
  ShieldAlert,
  ShieldCheck,
  BookOpen,
  FileText,
  ClipboardList,
  ClipboardCheck,
  ListChecks,
  Bot,
  FileBarChart,
  Settings,
} from "lucide-react";

import type {
  PermissionAction,
  PermissionResource,
} from "@/auth/permissions";


export interface NavigationItem {
  label: string;
  path: string;

  icon: React.ComponentType<{
    size?: number;
    className?: string;
  }>;

  resource?: PermissionResource;
  action?: PermissionAction;
}


export const navigation: NavigationItem[] = [

  {
    label: "Command Center",
    path: "/dashboard",
    icon: LayoutDashboard,
  },

  {
    label: "Risks",
    path: "/risks",
    icon: ShieldAlert,
    resource: "risks",
    action: "view",
  },

  {
    label: "Controls",
    path: "/controls",
    icon: ShieldCheck,
    resource: "controls",
    action: "view",
  },

  {
    label: "Frameworks",
    path: "/frameworks",
    icon: BookOpen,
    resource: "frameworks",
    action: "view",
  },

  {
    label: "Evidence",
    path: "/evidence",
    icon: FileText,
    resource: "evidence",
    action: "view",
  },

  {
    label: "Audits",
    path: "/audits",
    icon: ClipboardList,
    resource: "audits",
    action: "view",
  },

  {
    label: "Audit Findings",
    path: "/audit-findings",
    icon: ClipboardCheck,
    resource: "audit_findings",
    action: "view",
  },

  {
    label: "Corrective Actions",
    path: "/corrective-actions",
    icon: ListChecks,
    resource: "corrective_actions",
    action: "view",
  },

  {
    label: "GRC Intelligence",
    path: "/intelligence",
    icon: Brain,
    resource: "risks",
    action: "view",
  },

  {
    label: "Continuous Monitoring",
    path: "/monitoring",
    icon: Activity,
    resource: "risks",
    action: "view",
  },

  {
    label: "Reports",
    path: "/reports",
    icon: FileBarChart,
    resource: "reports",
    action: "view",
  },

  {
    label: "AI Intelligence",
    path: "/ai",
    icon: Bot,
    resource: "ai",
    action: "view",
  },

  {
    label: "Settings",
    path: "/settings",
    icon: Settings,
  },
];