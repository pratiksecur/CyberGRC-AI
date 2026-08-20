import {
  useMutation,
  useQueryClient,
} from "@tanstack/react-query";

import {
  updateAuditFinding,
} from "@/api/auditFindings";

import type {
  CreateAuditFindingRequest,
} from "@/api/auditFindings";


export function useUpdateAuditFinding() {

  const queryClient =
    useQueryClient();


  return useMutation({

    mutationFn: ({
      id,
      data,
    }: {
      id: number;
      data: Partial<CreateAuditFindingRequest>;
    }) =>
      updateAuditFinding(
        id,
        data
      ),


    onSuccess: (_, variables) => {

      queryClient.invalidateQueries({
        queryKey: ["audit-findings"],
      });


      queryClient.invalidateQueries({
        queryKey: [
          "audit-finding",
          variables.id,
        ],
      });

    },

  });

}