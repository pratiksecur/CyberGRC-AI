import { useParams, useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useControl } from "@/hooks/useControl";

export default function ViewControl() {
  const { id } = useParams();
  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
  } = useControl(Number(id));

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading control...
        </div>
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Failed to load control.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="mx-auto max-w-4xl space-y-6">

        <div className="flex items-center justify-between">

          <div>

            <h1 className="text-3xl font-bold">
              {data.title}
            </h1>

            <p className="text-slate-500">
              View cybersecurity control
            </p>

          </div>

          <button
            onClick={() => navigate("/controls")}
            className="rounded-lg border px-4 py-2 hover:bg-slate-100"
          >
            Back
          </button>

        </div>

        <div className="rounded-2xl border bg-white p-8 space-y-8">

          <div>
            <h2 className="mb-2 text-lg font-semibold">
              Description
            </h2>

            <p className="text-slate-600">
              {data.description}
            </p>
          </div>

          <div className="grid gap-6 md:grid-cols-2">

            <div>

              <p className="text-sm text-slate-500">
                Control Type
              </p>

              <p className="font-medium">
                {data.control_type}
              </p>

            </div>

            <div>

              <p className="text-sm text-slate-500">
                Status
              </p>

              <p className="font-medium">
                {data.status}
              </p>

            </div>

            <div>

              <p className="text-sm text-slate-500">
                Effectiveness
              </p>

              <p className="font-medium">
                {data.effectiveness}%
              </p>

            </div>

            <div>

              <p className="text-sm text-slate-500">
                Owner
              </p>

              <p className="font-medium">
                User #{data.owner_id}
              </p>

            </div>

            <div>

              <p className="text-sm text-slate-500">
                Created
              </p>

              <p className="font-medium">
                {new Date(data.created_at).toLocaleString()}
              </p>

            </div>

            <div>

              <p className="text-sm text-slate-500">
                Updated
              </p>

              <p className="font-medium">
                {new Date(data.updated_at).toLocaleString()}
              </p>

            </div>

          </div>

        </div>

      </div>
    </AppLayout>
  );
}