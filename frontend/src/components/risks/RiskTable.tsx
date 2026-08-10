import type { Risk } from "@/api/risks";

interface Props {
  risks: Risk[];
}

export default function RiskTable({ risks }: Props) {
  return (
    <div className="overflow-hidden rounded-xl border bg-white shadow-sm">

      <table className="min-w-full">

        <thead className="bg-slate-50">

          <tr>

            <th className="px-6 py-4 text-left text-sm font-semibold">
              Title
            </th>

            <th className="px-6 py-4 text-left text-sm font-semibold">
              Risk Score
            </th>

            <th className="px-6 py-4 text-left text-sm font-semibold">
              Likelihood
            </th>

            <th className="px-6 py-4 text-left text-sm font-semibold">
              Impact
            </th>

            <th className="px-6 py-4 text-left text-sm font-semibold">
              Status
            </th>

            <th className="px-6 py-4 text-left text-sm font-semibold">
              Created
            </th>

          </tr>

        </thead>

        <tbody>

          {risks.map((risk) => (

            <tr
              key={risk.id}
              className="border-t hover:bg-slate-50"
            >

              <td className="px-6 py-4 font-medium">
                {risk.title}
              </td>

              <td className="px-6 py-4">
                {risk.risk_score}
              </td>

              <td className="px-6 py-4">
                {risk.likelihood}
              </td>

              <td className="px-6 py-4">
                {risk.impact}
              </td>

              <td className="px-6 py-4">

                <span className="rounded-full bg-blue-100 px-3 py-1 text-sm text-blue-700">

                  {risk.status}

                </span>

              </td>

              <td className="px-6 py-4">
                {new Date(risk.created_at).toLocaleDateString()}
              </td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}