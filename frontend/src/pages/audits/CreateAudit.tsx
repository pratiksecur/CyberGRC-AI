import { useState } from "react";
import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useCreateAudit } from "@/hooks/useCreateAudit";
import { useFrameworks } from "@/hooks/useFrameworks";

export default function CreateAudit() {
  const navigate = useNavigate();

  const createMutation = useCreateAudit();

  const { data: frameworks } = useFrameworks();

  const [name, setName] = useState("");

  const [frameworkId, setFrameworkId] =
    useState<number>(0);

  const [auditorId, setAuditorId] =
    useState<number>(1);

  const [scope, setScope] = useState("");

  const [status, setStatus] =
    useState("Planned");

  const [startDate, setStartDate] =
    useState("");

  const [endDate, setEndDate] =
    useState("");

  async function handleSubmit(
    e: React.FormEvent
  ) {
    e.preventDefault();

    await createMutation.mutateAsync({
      name,
      framework_id: frameworkId,
      auditor_id: auditorId,
      scope,
      status,
      start_date: startDate,
      end_date: endDate,
    });

    navigate("/audits");
  }

  return (
    <AppLayout>
      <div className="mx-auto max-w-3xl">

        <h1 className="mb-2 text-3xl font-bold">
          Create Audit
        </h1>

        <p className="mb-8 text-slate-500">
          Schedule a cybersecurity audit.
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
              required
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
              required
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
              required
            />

          </div>

          <div className="grid grid-cols-2 gap-6">

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

          <div className="grid grid-cols-2 gap-6">

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
                required
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
                required
              />

            </div>

          </div>

          <div className="flex justify-end">

            <button
              type="submit"
              disabled={
                createMutation.isPending
              }
              className="rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700"
            >
              {createMutation.isPending
                ? "Creating..."
                : "Create Audit"}
            </button>

          </div>

        </form>

      </div>
    </AppLayout>
  );
}