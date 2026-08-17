import { useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useFramework } from "@/hooks/useFramework";

export default function ViewFramework() {
  const { id } = useParams();

  const frameworkId = Number(id);

  const {
    data,
    isLoading,
    error,
  } = useFramework(frameworkId);

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading framework...
        </div>
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Framework not found.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>

      <div className="mx-auto max-w-4xl space-y-8">

        <div>

          <h1 className="text-3xl font-bold">
            {data.name}
          </h1>

          <p className="mt-2 text-slate-500">
            Compliance Framework Details
          </p>

        </div>

        <div className="rounded-2xl border bg-white p-8 space-y-6">

          <div>

            <h2 className="text-sm font-semibold text-slate-500">
              Framework Name
            </h2>

            <p className="mt-1 text-lg">
              {data.name}
            </p>

          </div>

          <div>

            <h2 className="text-sm font-semibold text-slate-500">
              Version
            </h2>

            <p className="mt-1">
              {data.version}
            </p>

          </div>

          <div>

            <h2 className="text-sm font-semibold text-slate-500">
              Description
            </h2>

            <p className="mt-1 whitespace-pre-wrap">
              {data.description}
            </p>

          </div>

          <div className="grid gap-6 md:grid-cols-2">

            <div>

              <h2 className="text-sm font-semibold text-slate-500">
                Created At
              </h2>

              <p className="mt-1">
                {new Date(data.created_at).toLocaleString()}
              </p>

            </div>

            <div>

              <h2 className="text-sm font-semibold text-slate-500">
                Updated At
              </h2>

              <p className="mt-1">
                {new Date(data.updated_at).toLocaleString()}
              </p>

            </div>

          </div>

        </div>

      </div>

    </AppLayout>
  );
}