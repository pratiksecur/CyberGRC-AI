import { Search, Filter } from "lucide-react";

interface Props {
  search: string;
  onSearchChange: (value: string) => void;

  priority: string;
  onPriorityChange: (value: string) => void;

  status: string;
  onStatusChange: (value: string) => void;

  sort: string;
  onSortChange: (value: string) => void;
}

export default function CorrectiveActionFilters({
  search,
  onSearchChange,
  priority,
  onPriorityChange,
  status,
  onStatusChange,
  sort,
  onSortChange,
}: Props) {
  return (
    <div className="space-y-3">
      {/* Search */}

      <div className="flex flex-col gap-3 lg:flex-row">
        <div className="relative flex-1">
          <Search
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
            size={18}
          />

          <input
            type="text"
            placeholder="Search corrective actions..."
            value={search}
            onChange={(e) =>
              onSearchChange(e.target.value)
            }
            className="w-full rounded-xl border border-slate-200 bg-white py-3 pl-10 pr-4 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
          />
        </div>
      </div>

      {/* Filters */}

      <div className="flex flex-col gap-3 rounded-xl border bg-white p-4 shadow-sm md:flex-row md:items-center">
        <div className="flex items-center gap-2 text-sm font-medium text-slate-600">
          <Filter size={16} />
          Filters
        </div>

        <select
          value={priority}
          onChange={(e) =>
            onPriorityChange(e.target.value)
          }
          className="rounded-lg border border-slate-200 px-4 py-2.5 outline-none focus:border-blue-500"
        >
          <option value="">
            All Priorities
          </option>

          <option value="Critical">
            Critical
          </option>

          <option value="High">
            High
          </option>

          <option value="Medium">
            Medium
          </option>

          <option value="Low">
            Low
          </option>
        </select>

        <select
          value={status}
          onChange={(e) =>
            onStatusChange(e.target.value)
          }
          className="rounded-lg border border-slate-200 px-4 py-2.5 outline-none focus:border-blue-500"
        >
          <option value="">
            All Statuses
          </option>

          <option value="Open">
            Open
          </option>

          <option value="In Progress">
            In Progress
          </option>

          <option value="Completed">
            Completed
          </option>

          <option value="Closed">
            Closed
          </option>
        </select>

        <select
          value={sort}
          onChange={(e) =>
            onSortChange(e.target.value)
          }
          className="rounded-lg border border-slate-200 px-4 py-2.5 outline-none focus:border-blue-500"
        >
          <option value="">
            Sort Due Date
          </option>

          <option value="soonest">
            Due Date: Soonest
          </option>

          <option value="latest">
            Due Date: Latest
          </option>
        </select>
      </div>
    </div>
  );
}