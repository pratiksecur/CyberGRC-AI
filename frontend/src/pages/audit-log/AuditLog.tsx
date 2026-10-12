import { useState } from "react";
import { Navigate } from "react-router-dom";
import { useQuery } from "@tanstack/react-query";

import { ScrollText } from "lucide-react";

import AppLayout from "@/layouts/AppLayout";
import { useAuth } from "@/contexts/useAuth";
import { apiErrorMessage } from "@/lib/apiError";
import {
  getAuditLogFilters,
  getAuditLogs,
  type AuditLogEntry,
} from "@/api/auditLogs";

const PAGE_SIZE = 25;

const ALLOWED_ROLES = ["Admin", "Auditor"];

function formatValue(value: unknown): string {
  if (value === null || value === undefined) {
    return "—";
  }

  if (typeof value === "object") {
    return JSON.stringify(value);
  }

  return String(value);
}

function ChangeDetails({ entry }: { entry: AuditLogEntry }) {
  const changes = entry.details?.changes;
  const values = entry.details?.values;

  if (changes) {
    return (
      <ul className="space-y-1 text-xs text-slate-600">
        {Object.entries(changes).map(([field, change]) => (
          <li key={field}>
            <span className="font-medium text-slate-800">
              {field}
            </span>
            {": "}
            {"from" in change && (
              <>
                <span className="text-slate-500">
                  {formatValue(change.from)}
                </span>
                {" → "}
              </>
            )}
            <span>{formatValue(change.to)}</span>
          </li>
        ))}
      </ul>
    );
  }

  if (values) {
    return (
      <ul className="space-y-1 text-xs text-slate-600">
        {Object.entries(values)
          .slice(0, 8)
          .map(([field, value]) => (
            <li key={field}>
              <span className="font-medium text-slate-800">
                {field}
              </span>
              {": "}
              {formatValue(value)}
            </li>
          ))}
      </ul>
    );
  }

  return <span className="text-xs text-slate-400">—</span>;
}

export default function AuditLog() {
  const { user } = useAuth();

  const [offset, setOffset] = useState(0);
  const [entityType, setEntityType] = useState("");
  const [action, setAction] = useState("");
  const [openId, setOpenId] = useState<number | null>(null);

  const allowed =
    !!user && ALLOWED_ROLES.includes(user.role);

  const filters = useQuery({
    queryKey: ["audit-log-filters"],
    queryFn: getAuditLogFilters,
    enabled: allowed,
  });

  const logs = useQuery({
    queryKey: [
      "audit-logs",
      offset,
      entityType,
      action,
    ],
    queryFn: () =>
      getAuditLogs({
        limit: PAGE_SIZE,
        offset,
        entity_type: entityType,
        action,
      }),
    enabled: allowed,
  });

  if (user && !allowed) {
    return <Navigate to="/dashboard" replace />;
  }

  const total = logs.data?.total ?? 0;
  const from = total === 0 ? 0 : offset + 1;
  const to = Math.min(offset + PAGE_SIZE, total);

  function changeFilter(
    setter: (value: string) => void,
    value: string
  ) {
    setter(value);
    setOffset(0);
    setOpenId(null);
  }

  return (
    <AppLayout>
      <div className="mx-auto max-w-6xl space-y-6">

        <div className="flex items-start gap-4">
          <div className="rounded-xl bg-slate-100 p-3">
            <ScrollText className="h-6 w-6 text-slate-700" />
          </div>

          <div>
            <h1 className="text-3xl font-bold text-slate-900">
              Audit Trail
            </h1>

            <p className="mt-1 text-slate-500">
              Who created, changed or deleted what, and when.
              Entries cannot be edited or removed.
            </p>
          </div>
        </div>

        <div className="flex flex-wrap items-end gap-4 rounded-2xl border bg-white p-4 shadow-sm">

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-600">
              Record type
            </label>

            <select
              value={entityType}
              onChange={(e) =>
                changeFilter(setEntityType, e.target.value)
              }
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
            >
              <option value="">All</option>
              {filters.data?.entity_types.map((type) => (
                <option key={type} value={type}>
                  {type.replaceAll("_", " ")}
                </option>
              ))}
            </select>
          </div>

          <div>
            <label className="mb-1 block text-sm font-medium text-slate-600">
              Action
            </label>

            <select
              value={action}
              onChange={(e) =>
                changeFilter(setAction, e.target.value)
              }
              className="rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm"
            >
              <option value="">All</option>
              {filters.data?.actions.map((item) => (
                <option key={item} value={item}>
                  {item.replaceAll("_", " ")}
                </option>
              ))}
            </select>
          </div>

        </div>

        {logs.isError && (
          <div className="rounded-lg bg-red-100 p-3 text-sm text-red-700">
            {apiErrorMessage(
              logs.error,
              "Could not load the audit trail."
            )}
          </div>
        )}

        <div className="overflow-x-auto rounded-2xl border bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-slate-50 text-slate-500">
              <tr>
                <th className="px-5 py-3 font-medium">When</th>
                <th className="px-5 py-3 font-medium">Who</th>
                <th className="px-5 py-3 font-medium">What</th>
                <th className="px-5 py-3 font-medium">Details</th>
              </tr>
            </thead>

            <tbody className="divide-y">
              {logs.isLoading && (
                <tr>
                  <td colSpan={4} className="px-5 py-6 text-slate-400">
                    Loading...
                  </td>
                </tr>
              )}

              {logs.data?.items.length === 0 && (
                <tr>
                  <td colSpan={4} className="px-5 py-6 text-slate-400">
                    No entries yet.
                  </td>
                </tr>
              )}

              {logs.data?.items.map((entry) => (
                <tr key={entry.id} className="align-top">
                  <td className="whitespace-nowrap px-5 py-4 text-slate-600">
                    {new Date(entry.created_at).toLocaleString()}
                  </td>

                  <td className="px-5 py-4 text-slate-700">
                    {entry.actor_email ?? (
                      <span className="text-slate-400">
                        System
                      </span>
                    )}
                    {entry.ip_address && (
                      <div className="text-xs text-slate-400">
                        {entry.ip_address}
                      </div>
                    )}
                  </td>

                  <td className="px-5 py-4">
                    <span className="mr-2 rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium capitalize text-slate-700">
                      {entry.action.replaceAll("_", " ")}
                    </span>
                    <span className="text-slate-900">
                      {entry.summary}
                    </span>
                  </td>

                  <td className="px-5 py-4">
                    {openId === entry.id ? (
                      <div className="space-y-2">
                        <ChangeDetails entry={entry} />
                        <button
                          type="button"
                          onClick={() => setOpenId(null)}
                          className="text-xs font-medium text-blue-600 hover:text-blue-700"
                        >
                          Hide
                        </button>
                      </div>
                    ) : (
                      <button
                        type="button"
                        onClick={() => setOpenId(entry.id)}
                        className="text-xs font-medium text-blue-600 hover:text-blue-700"
                      >
                        Show
                      </button>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="flex items-center justify-between text-sm text-slate-600">
          <span>
            {total === 0
              ? "0 entries"
              : `${from}–${to} of ${total}`}
          </span>

          <div className="flex gap-2">
            <button
              type="button"
              disabled={offset === 0}
              onClick={() =>
                setOffset(Math.max(0, offset - PAGE_SIZE))
              }
              className="rounded-lg border px-4 py-2 font-medium hover:bg-slate-50 disabled:opacity-40"
            >
              Previous
            </button>

            <button
              type="button"
              disabled={offset + PAGE_SIZE >= total}
              onClick={() => setOffset(offset + PAGE_SIZE)}
              className="rounded-lg border px-4 py-2 font-medium hover:bg-slate-50 disabled:opacity-40"
            >
              Next
            </button>
          </div>
        </div>

      </div>
    </AppLayout>
  );
}