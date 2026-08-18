interface Audit {
  id: number;
  name: string;
  status: string;
  framework_id: number;
}

interface Props {
  audits: Audit[];
}

export default function AuditCards({
  audits,
}: Props) {
  return (
    <div className="rounded-2xl border bg-white p-6">

      <h2 className="mb-4 text-lg font-semibold">
        Framework Coverage
      </h2>

      <div className="space-y-4">

        {audits.slice(0, 5).map((audit) => (

          <div
            key={audit.id}
            className="flex items-center justify-between"
          >

            <div>

              <p className="font-medium">
                {audit.name}
              </p>

              <p className="text-sm text-slate-500">
                Framework #{audit.framework_id}
              </p>

            </div>

            <span
              className={`rounded-full px-3 py-1 text-xs font-semibold ${
                audit.status === "Completed"
                  ? "bg-green-100 text-green-700"
                  : audit.status === "In Progress"
                  ? "bg-yellow-100 text-yellow-700"
                  : "bg-blue-100 text-blue-700"
              }`}
            >
              {audit.status}
            </span>

          </div>

        ))}

      </div>

    </div>
  );
}