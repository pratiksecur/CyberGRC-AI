import {
  Eye,
  Pencil,
  Trash2,
} from "lucide-react";

import Can from "@/components/auth/Can";

import type {
  FrameworkControl,
} from "@/api/frameworkControls";

interface Props {
  controls: FrameworkControl[];
  onView?: (id: number) => void;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
}

export default function FrameworkControlTable({
  controls,
  onView,
  onEdit,
  onDelete,
}: Props) {
  return (
    <div className="overflow-hidden rounded-2xl border bg-white">

      <div className="border-b p-5">

        <h2 className="text-lg font-semibold">
          Framework Controls
        </h2>

        <p className="text-sm text-slate-500">
          Manage controls defined by compliance frameworks.
        </p>

      </div>

      <div className="overflow-x-auto">

        <table className="min-w-full">

          <thead className="border-b bg-slate-50">

            <tr>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Code
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Title
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Framework
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Description
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
                  colSpan={6}
                  className="py-10 text-center text-slate-500"
                >
                  No framework controls found.
                </td>

              </tr>

            ) : (

              controls.map((control) => (

                <tr
                  key={control.id}
                  className="border-b hover:bg-slate-50"
                >

                  <td className="px-6 py-5 font-mono text-sm">
                    {control.control_code}
                  </td>

                  <td className="px-6 py-5 font-medium">
                    {control.title}
                  </td>

                  <td className="px-6 py-5">
                    Framework #{control.framework_id}
                  </td>

                  <td className="max-w-md truncate px-6 py-5 text-sm text-slate-600">
                    {control.description}
                  </td>

                  <td className="px-6 py-5">
                    {new Date(
                      control.created_at
                    ).toLocaleDateString()}
                  </td>

                  <td className="px-6 py-5">

                    <div className="flex justify-center gap-3">

                      <Can
                        resource="framework_controls"
                        action="view"
                      >
                        <button
                          type="button"
                          title="View Framework Control"
                          onClick={() =>
                            onView?.(control.id)
                          }
                          className="text-slate-500 hover:text-blue-600"
                        >
                          <Eye size={18} />
                        </button>
                      </Can>

                      <Can
                        resource="framework_controls"
                        action="update"
                      >
                        <button
                          type="button"
                          title="Edit Framework Control"
                          onClick={() =>
                            onEdit?.(control.id)
                          }
                          className="text-slate-500 hover:text-amber-600"
                        >
                          <Pencil size={18} />
                        </button>
                      </Can>

                      <Can
                        resource="framework_controls"
                        action="delete"
                      >
                        <button
                          type="button"
                          title="Delete Framework Control"
                          onClick={() =>
                            onDelete?.(control.id)
                          }
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