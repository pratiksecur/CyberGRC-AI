import { Eye, Pencil, Trash2 } from "lucide-react";

import Can from "@/components/auth/Can";

interface Props {
  onView?: () => void;
  onEdit?: () => void;
  onDelete?: () => void;
}

export default function RiskActions({
  onView,
  onEdit,
  onDelete,
}: Props) {
  return (
    <div className="flex items-center justify-end gap-2">

      {/* View */}

      <Can resource="risks" action="view">
        <button
          onClick={onView}
          className="rounded-md p-2 text-slate-500 transition hover:bg-slate-100 hover:text-blue-600"
          title="View Risk"
          type="button"
        >
          <Eye size={18} />
        </button>
      </Can>

      {/* Edit */}

      <Can resource="risks" action="update">
        <button
          onClick={onEdit}
          className="rounded-md p-2 text-slate-500 transition hover:bg-slate-100 hover:text-amber-600"
          title="Edit Risk"
          type="button"
        >
          <Pencil size={18} />
        </button>
      </Can>

      {/* Delete */}

      <Can resource="risks" action="delete">
        <button
          onClick={onDelete}
          className="rounded-md p-2 text-slate-500 transition hover:bg-slate-100 hover:text-red-600"
          title="Delete Risk"
          type="button"
        >
          <Trash2 size={18} />
        </button>
      </Can>

    </div>
  );
}