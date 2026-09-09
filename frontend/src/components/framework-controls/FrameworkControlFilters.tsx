import { Search, Plus } from "lucide-react";

import Can from "@/components/auth/Can";

interface Props {
  search: string;
  onSearchChange: (value: string) => void;
  frameworkId: string;
  onFrameworkChange: (value: string) => void;
  frameworks: {
    id: number;
    name: string;
    version: string;
  }[];
  onCreate: () => void;
}

export default function FrameworkControlFilters({
  search,
  onSearchChange,
  frameworkId,
  onFrameworkChange,
  frameworks,
  onCreate,
}: Props) {
  return (
    <div className="flex flex-col gap-4 rounded-2xl border bg-white p-5 lg:flex-row lg:items-center lg:justify-between">

      <div className="relative w-full lg:max-w-sm">

        <Search className="absolute left-3 top-3 h-4 w-4 text-slate-400" />

        <input
          type="text"
          placeholder="Search framework controls..."
          value={search}
          onChange={(e) =>
            onSearchChange(e.target.value)
          }
          className="w-full rounded-lg border py-2 pl-10 pr-4 focus:border-blue-500 focus:outline-none"
        />

      </div>

      <div className="flex flex-wrap gap-3">

        <select
          value={frameworkId}
          onChange={(e) =>
            onFrameworkChange(e.target.value)
          }
          className="rounded-lg border px-4 py-2"
        >
          <option value="">
            All Frameworks
          </option>

          {frameworks.map((framework) => (
            <option
              key={framework.id}
              value={framework.id}
            >
              {framework.name} {framework.version}
            </option>
          ))}

        </select>

        <Can
          resource="framework_controls"
          action="create"
        >
          <button
            type="button"
            onClick={onCreate}
            className="flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-white hover:bg-blue-700"
          >
            <Plus size={18} />
            New Framework Control
          </button>
        </Can>

      </div>

    </div>
  );
}