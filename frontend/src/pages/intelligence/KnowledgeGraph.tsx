import { useState } from "react";

import AppLayout from "@/layouts/AppLayout";

import KnowledgeGraphComponent from "@/components/intelligence/KnowledgeGraph";

import { useKnowledgeGraph } from "@/hooks/useKnowledgeGraph";


export default function KnowledgeGraph() {
  const [
    riskInput,
    setRiskInput,
  ] = useState("");

  const [
    selectedRiskId,
    setSelectedRiskId,
  ] = useState<number | undefined>(
    undefined
  );

  const {
    data,
    isLoading,
    error,
  } = useKnowledgeGraph(
    selectedRiskId
  );


  const applyRiskFilter = () => {
    const normalized =
      riskInput.trim();

    if (!normalized) {
      setSelectedRiskId(
        undefined
      );

      return;
    }

    const riskId =
      Number(normalized);

    if (
      Number.isInteger(riskId) &&
      riskId > 0
    ) {
      setSelectedRiskId(
        riskId
      );
    }
  };


  return (
    <AppLayout>

      <div className="space-y-6">

        {/* HEADER */}

        <div>

          <h1 className="text-3xl font-bold">
            GRC Knowledge Graph
          </h1>

          <p className="mt-1 text-slate-500">
            Connected visibility across risks, controls,
            evidence, compliance, remediation and governed response.
          </p>

        </div>


        {/* FILTER */}

        <div className="rounded-xl border bg-white p-5 shadow-sm">

          <div className="flex flex-col gap-3 md:flex-row md:items-end">

            <div className="flex-1">

              <label className="text-sm font-medium">
                Focus on Risk ID
              </label>

              <input
                value={riskInput}
                onChange={(event) =>
                  setRiskInput(
                    event.target.value
                  )
                }
                placeholder="Leave empty for enterprise graph"
                className="mt-2 w-full rounded-lg border px-3 py-2 outline-none focus:ring-2"
              />

            </div>


            <button
              type="button"
              onClick={applyRiskFilter}
              className="rounded-lg border px-4 py-2 font-medium"
            >
              Apply
            </button>


            <button
              type="button"
              onClick={() => {
                setRiskInput("");
                setSelectedRiskId(
                  undefined
                );
              }}
              className="rounded-lg border px-4 py-2 font-medium"
            >
              Enterprise Graph
            </button>

          </div>

        </div>


        {/* CONTENT */}

        {isLoading && (
          <div className="rounded-xl border bg-white p-10 text-center text-slate-500">
            Building GRC knowledge graph...
          </div>
        )}


        {error && (
          <div className="rounded-xl border bg-white p-10 text-center text-red-500">
            Failed to load the GRC knowledge graph.
          </div>
        )}


        {data && (
          <KnowledgeGraphComponent
            data={data}
          />
        )}

      </div>

    </AppLayout>
  );
}