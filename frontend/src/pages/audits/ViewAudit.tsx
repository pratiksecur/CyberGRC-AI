import { useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useAudit } from "@/hooks/useAudit";

export default function ViewAudit() {
  const { id } = useParams();

  const {
    data: audit,
    isLoading,
    error,
  } = useAudit(Number(id));

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading audit...
        </div>
      </AppLayout>
    );
  }

  if (error || !audit) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Audit not found.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>

      <div className="mx-auto max-w-4xl">

        <h1 className="mb-2 text-3xl font-bold">
          {audit.name}
        </h1>

        <p className="mb-8 text-slate-500">
          Audit Details
        </p>

        <div className="rounded-2xl border bg-white p-8 space-y-6">

          <div>

            <p className="text-sm text-slate-500">
              Framework
            </p>

            <p className="font-medium">
              Framework #{audit.framework_id}
            </p>

          </div>

          <div>

            <p className="text-sm text-slate-500">
              Auditor
            </p>

            <p className="font-medium">
              User #{audit.auditor_id}
            </p>

          </div>

          <div>

            <p className="text-sm text-slate-500">
              Status
            </p>

            <p className="font-medium">
              {audit.status}
            </p>

          </div>

          <div>

            <p className="text-sm text-slate-500">
              Scope
            </p>

            <p>{audit.scope}</p>

          </div>

          <div className="grid grid-cols-2 gap-6">

            <div>

              <p className="text-sm text-slate-500">
                Start Date
              </p>

              <p>
                {new Date(
                  audit.start_date
                ).toLocaleDateString()}
              </p>

            </div>

            <div>

              <p className="text-sm text-slate-500">
                End Date
              </p>

              <p>
                {new Date(
                  audit.end_date
                ).toLocaleDateString()}
              </p>

            </div>

          </div>

          <div className="grid grid-cols-2 gap-6">

            <div>

              <p className="text-sm text-slate-500">
                Created
              </p>

              <p>
                {new Date(
                  audit.created_at
                ).toLocaleString()}
              </p>

            </div>

            <div>

              <p className="text-sm text-slate-500">
                Updated
              </p>

              <p>
                {new Date(
                  audit.updated_at
                ).toLocaleString()}
              </p>

            </div>

          </div>

        </div>

      </div>

    </AppLayout>
  );
}