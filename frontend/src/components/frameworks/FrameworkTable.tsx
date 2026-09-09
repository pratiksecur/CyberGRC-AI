import {
  Eye,
  Pencil,
  Trash2,
} from "lucide-react";

import Can from "@/components/auth/Can";

interface Framework {
  id: number;
  name: string;
  version: string;
  description: string;
  created_at: string;
}

interface Props {
  frameworks: Framework[];
  onView?: (id: number) => void;
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
}

export default function FrameworkTable({
  frameworks,
  onView,
  onEdit,
  onDelete,
}: Props) {
  return (
    <div className="overflow-hidden rounded-2xl border bg-white">

      <div className="border-b p-5">

        <h2 className="text-lg font-semibold">
          Frameworks
        </h2>

        <p className="text-sm text-slate-500">
          Manage compliance frameworks
        </p>

      </div>

      <div className="overflow-x-auto">

        <table className="min-w-full">

          <thead className="border-b bg-slate-50">

            <tr>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Name
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Version
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

            {frameworks.length === 0 ? (

              <tr>

                <td
                  colSpan={5}
                  className="py-10 text-center text-slate-500"
                >
                  No frameworks found.
                </td>

              </tr>

            ) : (

              frameworks.map((framework) => (

                <tr
                  key={framework.id}
                  className="border-b hover:bg-slate-50"
                >

                  {/* Name */}

                  <td className="px-6 py-5 font-medium">
                    {framework.name}
                  </td>

                  {/* Version */}

                  <td className="px-6 py-5">
                    {framework.version}
                  </td>

                  {/* Description */}

                  <td className="max-w-md truncate px-6 py-5">
                    {framework.description}
                  </td>

                  {/* Created */}

                  <td className="px-6 py-5">
                    {new Date(
                      framework.created_at
                    ).toLocaleDateString()}
                  </td>

                  {/* Actions */}

                  <td className="px-6 py-5">

                    <div className="flex justify-center gap-3">

                      {/* View */}

                      <Can
                        resource="frameworks"
                        action="view"
                      >
                        <button
                          onClick={() =>
                            onView?.(framework.id)
                          }
                          type="button"
                          title="View Framework"
                          className="text-slate-500 hover:text-blue-600"
                        >
                          <Eye size={18} />
                        </button>
                      </Can>

                      {/* Edit */}

                      <Can
                        resource="frameworks"
                        action="update"
                      >
                        <button
                          onClick={() =>
                            onEdit?.(framework.id)
                          }
                          type="button"
                          title="Edit Framework"
                          className="text-slate-500 hover:text-amber-600"
                        >
                          <Pencil size={18} />
                        </button>
                      </Can>

                      {/* Delete */}

                      <Can
                        resource="frameworks"
                        action="delete"
                      >
                        <button
                          onClick={() =>
                            onDelete?.(framework.id)
                          }
                          type="button"
                          title="Delete Framework"
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