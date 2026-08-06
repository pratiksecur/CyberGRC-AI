import {
  LayoutDashboard,
  ShieldAlert,
  ShieldCheck,
  BookOpen,
  FileText,
  ClipboardList,
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