interface Audit {
  id: number;
  name: string;
  start_date: string;
  status: string;
}

interface Props {
  audits: Audit[];
}

export default function RecentAudits({
  audits,
}: Props) {
  return (
    <div className="rounded-2xl border bg-white p-6">

      <h2 className="mb-4 text-lg font-semibold">
        Recent Audits
      </h2>

      <div className="space-y-4">

        {audits
          .slice()
          .sort(
            (a, b) =>
              new Date(
                b.start_date
              ).getTime() -
              new Date(
                a.start_date
              ).getTime()
          )
          .slice(0, 5)
          .map((audit) => (

            <div
              key={audit.id}
              className="flex items-center justify-between border-b pb-3 last:border-0"
            >

              <div>

                <p className="font-medium">
                  {audit.name}
                </p>

                <p className="text-sm text-slate-500">
                  {new Date(
                    audit.start_date
                  ).toLocaleDateString()}
                </p>

              </div>

              <span className="text-sm font-medium">
                {audit.status}
              </span>

            </div>

          ))}

      </div>

    </div>
  );
}