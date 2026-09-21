import Can from "@/components/auth/Can";

interface Props {
  search: string;
  onSearchChange: (value: string) => void;
  status: string;
  onStatusChange: (value: string) => void;
  onCreate: () => void;
}

export default function AuditFilters({
  search,
  onSearchChange,
  status,
  onStatusChange,
  onCreate,
}: Props) {
  return (
    <div className="flex flex-col gap-4 rounded-2xl border bg-white p-6 lg:flex-row lg:items-center lg:justify-between">

      <div className="flex flex-1 gap-4">

        <input
          type="text"
          placeholder="Search audits..."
          className="flex-1 rounded-lg border p-3"
          value={search}
          onChange={(e) =>
            onSearchChange(e.target.value)
          }
        />

        <select
          className="rounded-lg border p-3"
          value={status}
          onChange={(e) =>
            onStatusChange(e.target.value)
          }
        >
          <option value="">
            All Status
          </option>

          <option value="Planned">
            Planned
          </option>

          <option value="In Progress">
            In Progress
          </option>

          <option value="Completed">
            Completed
          </option>
        </select>

      </div>

      <Can
        resource="audits"
        action="create"
      >
        <button
          type="button"
          onClick={onCreate}
          className="rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700"
        >
          New Audit
        </button>
      </Can>

    </div>
  );
}