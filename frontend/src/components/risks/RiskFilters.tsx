import { Search } from "lucide-react";

interface Props {
  search: string;
  onSearchChange: (value: string) => void;

  status: string;
  onStatusChange: (value: string) => void;

  sort: string;
  onSortChange: (value: string) => void;
}

export default function RiskFilters({
  search,
  onSearchChange,
  status,
  onStatusChange,
  sort,
  onSortChange,
}: Props) {
  return (
    <div className="flex flex-col gap-4 rounded-xl border bg-white p-4 shadow-sm lg:flex-row lg:items-center lg:justify-between">

      {/* Search */}

      <div className="relative w-full lg:max-w-md">

        <Search
          className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          size={18}
        />

        <input
          type="text"
          placeholder="Search risks..."
          value={search}
          onChange={(e) => onSearchChange(e.target.value)}
          className="w-full rounded-lg border border-slate-200 py-2 pl-10 pr-4 outline-none focus:border-blue-500"
        />

      </div>

      {/* Filters */}

      <div className="flex gap-3">

        <select
          value={status}
          onChange={(e) => onStatusChange(e.target.value)}
          className="rounded-lg border border-slate-200 px-4 py-2"
        >
          <option value="">All Status</option>
          <option value="Open">Open</option>
          <option value="In Progress">In Progress</option>
          <option value="Mitigated">Mitigated</option>
          <option value="Closed">Closed</option>
        </select>

        <select
          value={sort}
          onChange={(e) => onSortChange(e.target.value)}
          className="rounded-lg border border-slate-200 px-4 py-2"
        >
          <option value="">Sort Score</option>
          <option value="high">Highest First</option>
          <option value="low">Lowest First</option>
        </select>

      </div>

    </div>
  );
}