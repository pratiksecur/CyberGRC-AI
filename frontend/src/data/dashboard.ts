export const dashboardStats = [
  {
    title: "Total Risks",
    value: 18,
    subtitle: "+2 this week",
    icon: "risk",
    color: "bg-red-500",
  },
  {
    title: "Controls",
    value: 42,
    subtitle: "38 Active",
    icon: "control",
    color: "bg-emerald-500",
  },
  {
    title: "Audits",
    value: 5,
    subtitle: "2 In Progress",
    icon: "audit",
    color: "bg-blue-600",
  },
  {
    title: "Compliance",
    value: "87%",
    subtitle: "ISO 27001",
    icon: "compliance",
    color: "bg-amber-500",
  },
];

export const aiSummary = {
  organizationRiskLevel: "Medium",

  executiveSummary:
    "The organization's cybersecurity posture is stable overall. However, several high-risk items require attention, particularly around privileged access management and audit follow-up.",

  topPriorities: [
    "Enable Multi-Factor Authentication",
    "Review High Risk Findings",
    "Complete Internal Audit",
  ],

  recommendedNextSteps: [
    "Assign corrective actions",
    "Review outstanding risks",
    "Schedule management review",
  ],
};