import { Eye, Pencil, Trash2 } from "lucide-react";

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
    <div className="flex items-center gap-2">

      <button
        onClick={onView}
        className="rounded-md p-2 text-slate-500 transition hover:bg-slate-100 hover:text-blue-600"
        title="View Risk"
      >
        <Eye size={18} />
      </button>

      <button
        onClick={onEdit}
        className="rounded-md p-2 text-slate-500 transition hover:bg-slate-100 hover:text-amber-600"
        title="Edit Risk"
      >
        <Pencil size={18} />
      </button>

      <button
        onClick={onDelete}
        className="rounded-md p-2 text-slate-500 transition hover:bg-slate-100 hover:text-red-600"
        title="Delete Risk"
      >
        <Trash2 size={18} />
      </button>

    </div>
  );
}