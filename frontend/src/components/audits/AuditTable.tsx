import {
  Eye,
  Pencil,
  Trash2,
} from "lucide-react";

interface Audit {
  id: number;
  name: string;
  framework_id: number;
  auditor_id: number;
  status: string;
  start_date: string;
  end_date: string;
}

interface Props {
  audits: Audit[];
  onView?: (id: number) => void;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
}

export default function AuditTable({
  audits,
  onView,
  onEdit,
  onDelete,
}: Props) {
  return (
    <div className="overflow-hidden rounded-2xl border bg-white">

      <div className="border-b p-5">

        <h2 className="text-lg font-semibold">
          Audits
        </h2>

        <p className="text-sm text-slate-500">
          Manage cybersecurity audits
        </p>

      </div>

      <div className="overflow-x-auto">

        <table className="min-w-full">

          <thead className="border-b bg-slate-50">

            <tr>

              <th className="px-6 py-4 text-left">
                Audit
              </th>

              <th className="px-6 py-4 text-left">
                Framework
              </th>

              <th className="px-6 py-4 text-left">
                Auditor
              </th>

              <th className="px-6 py-4 text-left">
                Status
              </th>

              <th className="px-6 py-4 text-left">
                Start
              </th>

              <th className="px-6 py-4 text-left">
                End
              </th>

              <th className="px-6 py-4 text-center">
                Actions
              </th>

            </tr>

          </thead>

          <tbody>

            {audits.length === 0 ? (

              <tr>

                <td
                  colSpan={7}
                  className="py-10 text-center text-slate-500"
                >
                  No audits found.
                </td>

              </tr>

            ) : (

              audits.map((audit) => (

                <tr
                  key={audit.id}
                  className="border-b hover:bg-slate-50"
                >

                  <td className="px-6 py-5 font-medium">
                    {audit.name}
                  </td>

                  <td className="px-6 py-5">
                    Framework #{audit.framework_id}
                  </td>

                  <td className="px-6 py-5">
                    User #{audit.auditor_id}
                  </td>

                  <td className="px-6 py-5">

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

                  </td>

                  <td className="px-6 py-5">
                    {new Date(
                      audit.start_date
                    ).toLocaleDateString()}
                  </td>

                  <td className="px-6 py-5">
                    {new Date(
                      audit.end_date
                    ).toLocaleDateString()}
                  </td>

                  <td className="px-6 py-5">

                    <div className="flex justify-center gap-3">

                      <button
                        onClick={() =>
                          onView?.(audit.id)
                        }
                        className="text-slate-500 hover:text-blue-600"
                      >
                        <Eye size={18} />
                      </button>

                      <button
                        onClick={() =>
                          onEdit?.(audit.id)
                        }
                        className="text-slate-500 hover:text-amber-600"
                      >
                        <Pencil size={18} />
                      </button>

                      <button
                        onClick={() =>
                          onDelete?.(audit.id)
                        }
                        className="text-slate-500 hover:text-red-600"
                      >
                        <Trash2 size={18} />
                      </button>

                    </div>

                  </td>

                </tr>

              ))

            )}

          </tbody>

        </table>

      </div>

    </div>
  );
}