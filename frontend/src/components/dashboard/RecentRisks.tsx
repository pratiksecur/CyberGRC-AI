import type { Risk } from "@/api/risks";

interface Props {
  risks: Risk[];
}

export default function RecentRisks({
  risks,
}: Props) {

  const recentRisks = [...risks]
    .sort(
      (a, b) =>
        new Date(b.created_at).getTime() -
        new Date(a.created_at).getTime()
    )
    .slice(0, 5);

  return (

    <div className="rounded-2xl border bg-white p-6 shadow-sm">

      <h2 className="mb-6 text-lg font-semibold">
        Recent Risks
      </h2>

      <div className="space-y-4">

        {recentRisks.length === 0 ? (

          <p className="text-sm text-slate-500">
            No risks found.
          </p>

        ) : (

          recentRisks.map((risk) => (

            <div
              key={risk.id}
              className="flex items-center justify-between border-b pb-3 last:border-0"
            >

              <div>

                <p className="font-medium">
                  {risk.title}
                </p>

                <p className="text-sm text-slate-500">
                  {new Date(
                    risk.created_at
                  ).toLocaleDateString()}
                </p>

              </div>

              <span className="rounded-full bg-slate-100 px-3 py-1 text-sm">
                {risk.risk_score}
              </span>

            </div>

          ))

        )}

      </div>

    </div>

  );

}