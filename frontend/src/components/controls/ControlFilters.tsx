import { Search, Plus } from "lucide-react";

import Can from "@/components/auth/Can";

interface ControlFiltersProps {
  search: string;
  onSearchChange: (value: string) => void;
  status: string;
  onStatusChange: (value: string) => void;
  framework: string;
  onFrameworkChange: (value: string) => void;
  onCreate: () => void;
}

export default function ControlFilters({
  search,
  onSearchChange,
  status,
  onStatusChange,
  framework,
  onFrameworkChange,
  onCreate,
}: ControlFiltersProps) {
  return (
    <div className="flex flex-col gap-4 rounded-xl border bg-white p-4 lg:flex-row lg:items-center lg:justify-between">

      {/* Search */}

      <div className="relative w-full lg:max-w-sm">

        <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />

        <input
          type="text"
          placeholder="Search controls..."
          value={search}
          onChange={(e) =>
            onSearchChange(e.target.value)
          }
          className="w-full rounded-lg border border-slate-200 py-2 pl-10 pr-4 focus:border-blue-500 focus:outline-none"
        />

      </div>

      {/* Filters */}

      <div className="flex flex-wrap items-center gap-3">

        <select
          value={status}
          onChange={(e) =>
            onStatusChange(e.target.value)
          }
          className="rounded-lg border border-slate-200 px-3 py-2"
        >
          <option value="">
            All Status
          </option>

          <option value="Active">
            Active
          </option>

          <option value="Inactive">
            Inactive
          </option>
        </select>

        <select
          value={framework}
          onChange={(e) =>
            onFrameworkChange(e.target.value)
          }
          className="rounded-lg border border-slate-200 px-3 py-2"
        >
          <option value="">
            All Types
          </option>

          <option value="Technical">
            Technical
          </option>

          <option value="Administrative">
            Administrative
          </option>

          <option value="Physical">
            Physical
          </option>

          <option value="Preventive">
            Preventive
          </option>

          <option value="Detective">
            Detective
          </option>

          <option value="Corrective">
            Corrective
          </option>
        </select>

        {/* Create Control */}

        <Can resource="controls" action="create">
          <button
            onClick={onCreate}
            type="button"
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white transition hover:bg-blue-700"
          >
            <Plus size={18} />

            New Control
          </button>
        </Can>

      </div>

    </div>
  );
}