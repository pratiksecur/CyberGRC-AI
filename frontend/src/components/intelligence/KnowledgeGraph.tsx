import {
  Activity,
  BookOpen,
  FileText,
  GitBranch,
  Network,
  ShieldAlert,
  ShieldCheck,
  Workflow,
} from "lucide-react";

import type {
  KnowledgeGraphResponse,
} from "@/api/intelligence";


interface Props {
  data: KnowledgeGraphResponse;
}


const NODE_ICONS: Record<
  string,
  React.ComponentType<{
    size?: number;
  }>
> = {
  RISK: ShieldAlert,
  CONTROL: ShieldCheck,
  EVIDENCE: FileText,
  FRAMEWORK: BookOpen,
  FRAMEWORK_REQUIREMENT: BookOpen,
  RESPONSE_WORKFLOW: Workflow,
  RESPONSE_DECISION: GitBranch,
  FINDING: Activity,
  CORRECTIVE_ACTION: Activity,
  RISK_TREATMENT: Network,
  AUDIT: FileText,
};


function formatNodeType(
  value: string
) {
  return value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(
      /\b\w/g,
      (char) =>
        char.toUpperCase()
    );
}


function formatRelation(
  value: string
) {
  return value
    .replaceAll("_", " ")
    .toLowerCase()
    .replace(
      /\b\w/g,
      (char) =>
        char.toUpperCase()
    );
}


export default function KnowledgeGraph({
  data,
}: Props) {
  const {
    summary,
    nodes,
    edges,
  } = data;

  return (
    <div className="space-y-6">

      {/* ================================================== */}
      {/* SUMMARY */}
      {/* ================================================== */}

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">

        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">
            Graph Nodes
          </p>

          <p className="mt-2 text-3xl font-bold">
            {summary.total_nodes}
          </p>
        </div>


        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">
            Relationships
          </p>

          <p className="mt-2 text-3xl font-bold">
            {summary.total_edges}
          </p>
        </div>


        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">
            Risks Connected to Controls
          </p>

          <p className="mt-2 text-3xl font-bold">
            {summary.risks_with_controls}
          </p>
        </div>


        <div className="rounded-xl border bg-white p-5 shadow-sm">
          <p className="text-sm text-slate-500">
            Disconnected Nodes
          </p>

          <p className="mt-2 text-3xl font-bold">
            {summary.disconnected_nodes}
          </p>
        </div>

      </div>


      {/* ================================================== */}
      {/* LIFECYCLE COVERAGE */}
      {/* ================================================== */}

      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <div className="mb-5">
          <h2 className="text-xl font-semibold">
            GRC Lifecycle Connectivity
          </h2>

          <p className="text-sm text-slate-500">
            Coverage across the connected GRC knowledge model.
          </p>
        </div>


        <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4">

          <Metric
            label="Controls with Evidence"
            value={
              summary.controls_with_evidence
            }
          />

          <Metric
            label="Controls with Frameworks"
            value={
              summary.controls_with_frameworks
            }
          />

          <Metric
            label="Findings with Actions"
            value={
              summary.findings_with_actions
            }
          />

          <Metric
            label="Risks with Treatments"
            value={
              summary.risks_with_treatments
            }
          />

          <Metric
            label="Risks with Decisions"
            value={
              summary.risks_with_decisions
            }

          />

          <Metric
            label="Risks with Workflows"
            value={
              summary.risks_with_workflows
            }
          />

        </div>

      </div>


      {/* ================================================== */}
      {/* NODE INVENTORY */}
      {/* ================================================== */}

      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <div className="mb-5 flex items-center gap-3">

          <Network size={20} />

          <div>
            <h2 className="text-xl font-semibold">
              Knowledge Graph Nodes
            </h2>

            <p className="text-sm text-slate-500">
              Visibility-filtered GRC entities.
            </p>
          </div>

        </div>


        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">

          {nodes.map((node) => {
            const Icon =
              NODE_ICONS[
                node.node_type
              ] ?? Network;

            return (
              <div
                key={`${node.node_type}-${node.id}`}
                className="rounded-lg border p-4"
              >

                <div className="flex items-start gap-3">

                  <div className="rounded-lg bg-slate-100 p-2">
                    <Icon size={18} />
                  </div>

                  <div className="min-w-0">

                    <p className="text-xs font-medium uppercase text-slate-500">
                      {formatNodeType(
                        node.node_type
                      )}
                    </p>

                    <p className="mt-1 truncate font-medium">
                      {node.label}
                    </p>

                    {node.status && (
                      <p className="mt-1 text-xs text-slate-500">
                        Status: {node.status}
                      </p>
                    )}

                  </div>

                </div>

              </div>
            );
          })}

        </div>

      </div>


      {/* ================================================== */}
      {/* RELATIONSHIPS */}
      {/* ================================================== */}

      <div className="rounded-xl border bg-white p-6 shadow-sm">

        <div className="mb-5">

          <h2 className="text-xl font-semibold">
            GRC Relationships
          </h2>

          <p className="text-sm text-slate-500">
            Deterministic relationships discovered from the GRC data model.
          </p>

        </div>


        <div className="space-y-3">

          {edges.map((edge, index) => (

            <div
              key={`${edge.source_type}-${edge.source_id}-${edge.target_type}-${edge.target_id}-${index}`}
              className="flex flex-col gap-2 rounded-lg border p-4 md:flex-row md:items-center"
            >

              <span className="font-medium">
                {formatNodeType(
                  edge.source_type
                )} #{edge.source_id}
              </span>

              <span className="text-xs font-semibold uppercase text-slate-500">
                {formatRelation(
                  edge.relation
                )}
              </span>

              <span className="font-medium">
                {formatNodeType(
                  edge.target_type
                )} #{edge.target_id}
              </span>

            </div>

          ))}

        </div>

      </div>

    </div>
  );
}


function Metric({
  label,
  value,
}: {
  label: string;
  value: number;
}) {
  return (
    <div className="rounded-lg border p-4">

      <p className="text-sm text-slate-500">
        {label}
      </p>

      <p className="mt-2 text-2xl font-bold">
        {value}
      </p>

    </div>
  );
}