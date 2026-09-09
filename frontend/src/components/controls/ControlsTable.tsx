import {
  Eye,
  Pencil,
  Trash2,
} from "lucide-react";

import Can from "@/components/auth/Can";

interface Control {
  id: number;
  title: string;
  control_type: string;
  status: string;
  effectiveness: number;
  owner_id: number;
  created_at: string;
}

interface Props {
  controls: Control[];
  onView?: (id: number) => void;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
}

export default function ControlsTable({
  controls,
  onView,
  onEdit,
  onDelete,
}: Props) {
  return (
    <div className="overflow-hidden rounded-2xl border bg-white">

      <div className="border-b p-5">

        <h2 className="text-lg font-semibold">
          Controls
        </h2>

        <p className="text-sm text-slate-500">
          Manage cybersecurity controls
        </p>

      </div>

      <div className="overflow-x-auto">

        <table className="min-w-full">

          <thead className="border-b bg-slate-50">

            <tr>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Control
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Type
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Status
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Effectiveness
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Owner
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Created
              </th>

              <th className="px-6 py-4 text-center text-sm font-semibold">
                Actions
              </th>

            </tr>

          </thead>

          <tbody>

            {controls.length === 0 ? (

              <tr>

                <td
                  colSpan={7}
                  className="py-10 text-center text-slate-500"
                >
                  No controls found.
                </td>

              </tr>

            ) : (

              controls.map((control) => (

                <tr
                  key={control.id}
                  className="border-b hover:bg-slate-50"
                >

                  {/* Control */}

                  <td className="px-6 py-5">

                    <div className="font-medium">
                      {control.title}
                    </div>

                    <div className="text-sm text-slate-500">
                      {control.control_type}
                    </div>

                  </td>

                  {/* Type */}

                  <td className="px-6 py-5">
                    {control.control_type}
                  </td>

                  {/* Status */}

                  <td className="px-6 py-5">

                    <span
                      className={`rounded-full px-3 py-1 text-xs font-semibold ${
                        control.status === "Active"
                          ? "bg-green-100 text-green-700"
                          : "bg-red-100 text-red-700"
                      }`}
                    >
                      {control.status}
                    </span>

                  </td>

                  {/* Effectiveness */}

                  <td className="px-6 py-5">
                    {control.effectiveness}%
                  </td>

                  {/* Owner */}

                  <td className="px-6 py-5">
                    User #{control.owner_id}
                  </td>

                  {/* Created */}

                  <td className="px-6 py-5">
                    {new Date(
                      control.created_at
                    ).toLocaleDateString()}
                  </td>

                  {/* Actions */}

                  <td className="px-6 py-5">

                    <div className="flex justify-center gap-3">

                      {/* View */}

                      <Can
                        resource="controls"
                        action="view"
                      >
                        <button
                          onClick={() =>
                            onView?.(control.id)
                          }
                          type="button"
                          title="View Control"
                          className="text-slate-500 hover:text-blue-600"
                        >
                          <Eye size={18} />
                        </button>
                      </Can>

                      {/* Edit */}

                      <Can
                        resource="controls"
                        action="update"
                      >
                        <button
                          onClick={() =>
                            onEdit?.(control.id)
                          }
                          type="button"
                          title="Edit Control"
                          className="text-slate-500 hover:text-amber-600"
                        >
                          <Pencil size={18} />
                        </button>
                      </Can>

                      {/* Delete */}

                      <Can
                        resource="controls"
                        action="delete"
                      >
                        <button
                          onClick={() =>
                            onDelete?.(control.id)
                          }
                          type="button"
                          title="Delete Control"
                          className="text-slate-500 hover:text-red-600"
                        >
                          <Trash2 size={18} />
                        </button>
                      </Can>

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