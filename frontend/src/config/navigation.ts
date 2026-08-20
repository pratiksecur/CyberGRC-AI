import {
  LayoutDashboard,
  ShieldAlert,
  ShieldCheck,
  BookOpen,
  FileText,
  ClipboardList,
  ClipboardCheck,
  ListChecks,
  Bot,
  Settings,
} from "lucide-react";

export const navigation = [
  {
    label: "Command Center",
    path: "/dashboard",
    icon: LayoutDashboard,
  },

  {
    label: "Risks",
    path: "/risks",
    icon: ShieldAlert,
  },

  {
    label: "Controls",
    path: "/controls",
    icon: ShieldCheck,
  },

  {
    label: "Frameworks",
    path: "/frameworks",
    icon: BookOpen,
  },

  {
    label: "Evidence",
    path: "/evidence",
    icon: FileText,
  },

  {
    label: "Audits",
    path: "/audits",
    icon: ClipboardList,
  },

  {
    label: "Audit Findings",
    path: "/audit-findings",
    icon: ClipboardCheck,
  },

  {
    label: "Corrective Actions",
    path: "/corrective-actions",
    icon: ListChecks,
  },

  {
    label: "AI Intelligence",
    path: "/ai",
    icon: Bot,
  },

  {
    label: "Settings",
    path: "/settings",
    icon: Settings,
  },
];