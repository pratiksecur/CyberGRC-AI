import { useMutation } from "@tanstack/react-query";

import {
  summarizeAudit,
} from "@/api/ai";

export function useAuditAISummary() {
  return useMutation({
    mutationFn: (auditId: number) =>
      summarizeAudit(auditId),
  });
}