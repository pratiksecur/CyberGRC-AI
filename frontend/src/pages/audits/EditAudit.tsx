import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useFrameworks } from "@/hooks/useFrameworks";
import { useAudit } from "@/hooks/useAudit";
import { useUpdateAudit } from "@/hooks/useUpdateAudit";

export default function EditAudit() {
  const { id } = useParams();

  const auditId = Number(id);

  const navigate = useNavigate();

  const { data: audit, isLoading } =
    useAudit(auditId);

  const { data: frameworks } =
    useFrameworks();

  const updateMutation =
    useUpdateAudit(auditId);

  const [name, setName] = useState("");

  const [frameworkId, setFrameworkId] =
    useState(0);

  const [auditorId, setAuditorId] =
    useState(1);

  const [scope, setScope] = useState("");

  const [status, setStatus] =
    useState("Planned");

  const [startDate, setStartDate] =
    useState("");

  const [endDate, setEndDate] =
    useState("");

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (!audit) return;

    setName(audit.name);
    setFrameworkId(audit.framework_id);
    setAuditorId(audit.auditor_id);
    setScope(audit.scope);
    setStatus(audit.status);
    setStartDate(audit.start_date);
    setEndDate(audit.end_date);
  }, [audit]);
  /* eslint-enable react-hooks/set-state-in-effect */

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading...
        </div>
      </AppLayout>
    );
  }

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    await updateMutation.mutateAsync({
      name,
      framework_id: frameworkId,
      auditor_id: auditorId,
      scope,
      status,
      start_date: startDate,
      end_date: endDate,
    });

    navigate("/audits");
  };

  return (
    <AppLayout>
      <div className="mx-auto max-w-3xl">

        <h1 className="mb-2 text-3xl font-bold">
          Edit Audit
        </h1>

        <p className="mb-8 text-slate-500">
          Update audit details.
        </p>

        <form
          onSubmit={handleSubmit}
          className="space-y-6 rounded-2xl border bg-white p-8"
        >

          <div>

            <label className="mb-2 block font-medium">
              Audit Name
            </label>

            <input
              className="w-full rounded-lg border p-3"
              value={name}
              onChange={(e) =>
                setName(e.target.value)
              }
            />

          </div>

          <div>

            <label className="mb-2 block font-medium">
              Framework
            </label>

            <select
              className="w-full rounded-lg border p-3"
              value={frameworkId}
              onChange={(e) =>
                setFrameworkId(
                  Number(e.target.value)
                )
              }
            >

              <option value={0}>
                Select Framework
              </option>

              {frameworks?.map(
                (framework) => (
                  <option
                    key={framework.id}
                    value={framework.id}
                  >
                    {framework.name}
                  </option>
                )
              )}

            </select>

          </div>

          <div>

            <label className="mb-2 block font-medium">
              Scope
            </label>

            <textarea
              rows={5}
              className="w-full rounded-lg border p-3"
              value={scope}
              onChange={(e) =>
                setScope(e.target.value)
              }
            />

          </div>

          <div className="grid grid-cols-2 gap-4">

            <div>

              <label className="mb-2 block font-medium">
                Status
              </label>

              <select
                className="w-full rounded-lg border p-3"
                value={status}
                onChange={(e) =>
                  setStatus(e.target.value)
                }
              >
                <option>
                  Planned
                </option>

                <option>
                  In Progress
                </option>

                <option>
                  Completed
                </option>

              </select>

            </div>

            <div>

              <label className="mb-2 block font-medium">
                Auditor (User ID)
              </label>

              <input
                type="number"
                className="w-full rounded-lg border p-3"
                value={auditorId}
                onChange={(e) =>
                  setAuditorId(
                    Number(e.target.value)
                  )
                }
              />

            </div>

          </div>

          <div className="grid grid-cols-2 gap-4">

            <div>

              <label className="mb-2 block font-medium">
                Start Date
              </label>

              <input
                type="date"
                className="w-full rounded-lg border p-3"
                value={startDate}
                onChange={(e) =>
                  setStartDate(e.target.value)
                }
              />

            </div>

            <div>

              <label className="mb-2 block font-medium">
                End Date
              </label>

              <input
                type="date"
                className="w-full rounded-lg border p-3"
                value={endDate}
                onChange={(e) =>
                  setEndDate(e.target.value)
                }
              />

            </div>

          </div>

          <div className="flex justify-end">

            <button
              type="submit"
              disabled={
                updateMutation.isPending
              }
              className="rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700"
            >
              {updateMutation.isPending
                ? "Updating..."
                : "Update Audit"}
            </button>

          </div>

        </form>

      </div>
    </AppLayout>
  );
}