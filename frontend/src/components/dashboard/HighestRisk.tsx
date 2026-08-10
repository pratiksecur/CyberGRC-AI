import type { Risk } from "@/api/risks";

import RiskScoreBadge from "@/components/risks/RiskScoreBadge";

interface Props {
  risks: Risk[];
}

export default function HighestRisk({
  risks,
}: Props) {

  if (risks.length === 0) {

    return (

      <div className="rounded-2xl border bg-white p-6 shadow-sm">

        <h2 className="text-lg font-semibold">
          Highest Risk
        </h2>

        <p className="mt-4 text-slate-500">
          No risks available.
        </p>

      </div>

    );

  }

  const highestRisk = [...risks].sort(
    (a, b) => b.risk_score - a.risk_score
  )[0];

  return (

    <div className="rounded-2xl border bg-white p-6 shadow-sm">

      <h2 className="mb-6 text-lg font-semibold">
        Highest Risk
      </h2>

      <h3 className="text-xl font-bold">
        {highestRisk.title}
      </h3>

      <p className="mt-3 text-sm text-slate-500">
        {highestRisk.description}
      </p>

      <div className="mt-6">

        <RiskScoreBadge
          score={highestRisk.risk_score}
        />

      </div>

    </div>

  );

}