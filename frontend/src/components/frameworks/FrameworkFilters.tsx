import { Search, Plus } from "lucide-react";

interface Props {
  search: string;
  onSearchChange: (value: string) => void;
  version: string;
  onVersionChange: (value: string) => void;
  onCreate: () => void;
}

export default function FrameworkFilters({
  search,
  onSearchChange,
  version,
  onVersionChange,
  onCreate,
}: Props) {
  return (
    <div className="flex flex-col gap-4 rounded-2xl border bg-white p-5 lg:flex-row lg:items-center lg:justify-between">

      <div className="relative w-full lg:max-w-sm">

        <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />

        <input
          type="text"
          placeholder="Search frameworks..."
          value={search}
          onChange={(e) =>
            onSearchChange(e.target.value)
          }
          className="w-full rounded-lg border py-2 pl-10 pr-4"
        />

      </div>

      <div className="flex gap-3">

        <select
          value={version}
          onChange={(e) =>
            onVersionChange(e.target.value)
          }
          className="rounded-lg border px-4 py-2"
        >
          <option value="">All Versions</option>
          <option value="Latest">
            Latest
          </option>
          <option value="Old">
            Old
          </option>
        </select>

        <button
          onClick={onCreate}
          className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
        >
          <Plus size={18} />
          New Framework
        </button>

      </div>
    </div>
  );
}