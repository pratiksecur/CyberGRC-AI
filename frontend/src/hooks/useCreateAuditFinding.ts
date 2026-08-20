import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  createAuditFinding,
} from "@/api/auditFindings";

import type {
  CreateAuditFindingRequest,
} from "@/api/auditFindings";


export function useCreateAuditFinding() {

  const queryClient =
    useQueryClient();


  return useMutation({

    mutationFn: (
      data: CreateAuditFindingRequest
    ) =>
      createAuditFinding(data),


    onSuccess: () => {

      queryClient.invalidateQueries({
        queryKey: ["audit-findings"],
      });

    },

  });

}