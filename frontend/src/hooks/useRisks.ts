import { useQuery } from "@tanstack/react-query";
import { getRisks } from "@/api/risks";

export function useRisks() {
  return useQuery({
    queryKey: ["risks"],
    queryFn: getRisks,
  });
}