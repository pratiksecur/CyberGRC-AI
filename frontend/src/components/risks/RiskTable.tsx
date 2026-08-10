import { useNavigate } from "react-router-dom";

import type { Risk } from "@/api/risks";

import RiskActions from "./RiskActions";
import RiskScoreBadge from "./RiskScoreBadge";
import RiskStatusBadge from "./RiskStatusBadge";

interface Props {
  risks: Risk[];
}

export default function RiskTable({ risks }: Props) {

  const navigate = useNavigate();

  return (
    <div className="overflow-hidden rounded-xl border bg-white shadow-sm">

      <table className="min-w-full">

        <thead className="border-b bg-slate-50">

          <tr>

            <th className="px-6 py-4 text-left text-sm font-semibold">
              Risk
            </th>

            <th className="px-6 py-4 text-left text-sm font-semibold">
              Risk Score
            </th>

            <th className="px-6 py-4 text-left text-sm font-semibold">
              Status
            </th>

            <th className="px-6 py-4 text-left text-sm font-semibold">
              Owner
            </th>

            <th className="px-6 py-4 text-left text-sm font-semibold">
              Created
            </th>

            <th className="px-6 py-4 text-right text-sm font-semibold">
              Actions
            </th>

          </tr>

        </thead>

        <tbody>

          {risks.map((risk) => (

            <tr
              key={risk.id}
              className="border-b transition hover:bg-slate-50"
            >

              {/* Risk */}

              <td className="px-6 py-5">

                <div className="font-semibold text-slate-900">
                  {risk.title}
                </div>

                <div className="mt-1 max-w-md truncate text-sm text-slate-500">
                  {risk.description}
                </div>

              </td>

              {/* Risk Score */}

              <td className="px-6 py-5">
                <RiskScoreBadge score={risk.risk_score} />
              </td>

              {/* Status */}

              <td className="px-6 py-5">
                <RiskStatusBadge status={risk.status} />
              </td>

              {/* Owner */}

              <td className="px-6 py-5">
                User #{risk.owner_id}
              </td>

              {/* Created */}

              <td className="px-6 py-5">
                {new Date(risk.created_at).toLocaleDateString()}
              </td>

              {/* Actions */}

              <td className="px-6 py-5 text-right">

                <RiskActions
                  onView={() => navigate(`/risks/${risk.id}`)}
                  onEdit={() => {}}
                  onDelete={() => {}}
                />

              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}