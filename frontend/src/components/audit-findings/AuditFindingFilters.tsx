import { Filter, Plus, Search, X } from "lucide-react";

interface AuditOption {
  id: number;
  name: string;
}

interface Props {
  search: string;
  severity: string;
  status: string;
  auditId: string;

  audits: AuditOption[];

  onSearchChange: (value: string) => void;
  onSeverityChange: (value: string) => void;
  onStatusChange: (value: string) => void;
  onAuditChange: (value: string) => void;

  onCreate: () => void;
}

export default function AuditFindingFilters({
  search,
  severity,
  status,
  auditId,
  audits,
  onSearchChange,
  onSeverityChange,
  onStatusChange,
  onAuditChange,
  onCreate,
}: Props) {
  const hasFilters =
    search !== "" ||
    severity !== "" ||
    status !== "" ||
    auditId !== "";

  function clearFilters() {
    onSearchChange("");
    onSeverityChange("");
    onStatusChange("");
    onAuditChange("");
  }

  return (
    <div className="space-y-4">

      {/* Search + Create */}
      <div className="flex flex-col gap-3 lg:flex-row">

        <div className="relative flex-1">

          <Search
            size={18}
            className="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
          />

          <input
            value={search}
            onChange={(e) =>
              onSearchChange(e.target.value)
            }
            placeholder="Search findings..."
            className="w-full rounded-xl border bg-white py-3 pl-10 pr-4 outline-none transition focus:border-indigo-500 focus:ring-2 focus:ring-indigo-100"
          />

        </div>

        <button
          onClick={onCreate}
          className="flex items-center justify-center gap-2 rounded-xl bg-indigo-600 px-5 py-3 font-medium text-white transition hover:bg-indigo-700"
        >
          <Plus size={18} />
          New Finding
        </button>

      </div>

      {/* Filters */}
      <div className="flex flex-col gap-3 rounded-xl border bg-white p-4 shadow-sm lg:flex-row lg:items-center">

        <div className="flex items-center gap-2 text-sm font-medium text-slate-600">
          <Filter size={17} />
          Filters
        </div>

        <select
          value={severity}
          onChange={(e) =>
            onSeverityChange(e.target.value)
          }
          className="rounded-lg border px-4 py-2.5 text-sm outline-none focus:border-indigo-500"
        >
          <option value="">
            All Severities
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
          className="rounded-lg border px-4 py-2.5 text-sm outline-none focus:border-indigo-500"
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

          <option value="Closed">
            Closed
          </option>
        </select>

        <select
          value={auditId}
          onChange={(e) =>
            onAuditChange(e.target.value)
          }
          className="rounded-lg border px-4 py-2.5 text-sm outline-none focus:border-indigo-500"
        >
          <option value="">
            All Audits
          </option>

          {audits.map((audit) => (
            <option
              key={audit.id}
              value={audit.id}
            >
              {audit.name}
            </option>
          ))}
        </select>

        {hasFilters && (
          <button
            onClick={clearFilters}
            className="flex items-center justify-center gap-1 rounded-lg px-3 py-2.5 text-sm font-medium text-slate-600 transition hover:bg-slate-100"
          >
            <X size={16} />
            Clear
          </button>
        )}

      </div>

    </div>
  );
}