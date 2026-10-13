import { useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import {
  ArrowLeft,
  BookOpen,
  CalendarDays,
  Eye,
  Pencil,
  Search,
} from "lucide-react";

import AppLayout from "@/layouts/AppLayout";

import { useFramework } from "@/hooks/useFramework";
import { useFrameworkControls } from "@/hooks/useFrameworkControls";

import Can from "@/components/auth/Can";

function formatDate(value: string) {
  const date = new Date(value);

  return Number.isNaN(date.getTime())
    ? "—"
    : date.toLocaleDateString();
}

export default function ViewFramework() {
  const { id } = useParams();
  const navigate = useNavigate();

  const frameworkId = Number(id);

  const [search, setSearch] = useState("");

  const {
    data: framework,
    isLoading,
    error,
  } = useFramework(frameworkId);

  const {
    data: allRequirements,
    isLoading: requirementsLoading,
  } = useFrameworkControls();

  const requirements = useMemo(() => {
    if (!allRequirements) return [];

    return allRequirements
      .filter(
        (requirement) =>
          requirement.framework_id === frameworkId
      )
      .sort((a, b) =>
        a.control_code.localeCompare(
          b.control_code,
          undefined,
          { numeric: true }
        )
      );
  }, [allRequirements, frameworkId]);

  const visibleRequirements = useMemo(() => {
    const term = search.trim().toLowerCase();

    if (!term) return requirements;

    return requirements.filter(
      (requirement) =>
        requirement.control_code
          .toLowerCase()
          .includes(term) ||
        requirement.title
          .toLowerCase()
          .includes(term)
    );
  }, [requirements, search]);

  if (isLoading || requirementsLoading) {
    return (
      <AppLayout>
        <div className="mx-auto max-w-5xl space-y-4">
          <div className="h-5 w-32 animate-pulse rounded bg-slate-200" />
          <div className="h-10 w-80 animate-pulse rounded bg-slate-200" />
          <div className="h-72 animate-pulse rounded-2xl bg-slate-100" />
        </div>
      </AppLayout>
    );
  }

  if (error || !framework) {
    return (
      <AppLayout>
        <div className="mx-auto max-w-4xl">
          <div className="rounded-xl border border-red-200 bg-red-50 p-6">
            <h2 className="font-semibold text-red-700">
              Framework Not Found
            </h2>

            <p className="mt-1 text-sm text-red-600">
              The requested framework could not be found within your access scope.
            </p>

            <button
              type="button"
              onClick={() => navigate("/frameworks")}
              className="mt-4 flex items-center gap-2 rounded-lg bg-red-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-red-700"
            >
              <ArrowLeft size={16} />
              Back to Frameworks
            </button>
          </div>
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="mx-auto max-w-5xl space-y-6">
        {/* Header */}
        <div className="flex items-start justify-between gap-4">
          <div>
            <button
              type="button"
              onClick={() => navigate("/frameworks")}
              className="mb-4 flex items-center gap-2 text-sm text-slate-500 transition hover:text-slate-900"
            >
              <ArrowLeft size={16} />
              Back to Frameworks
            </button>

            <div className="flex items-start gap-3">
              <div className="rounded-xl bg-blue-100 p-3">
                <BookOpen
                  size={22}
                  className="text-blue-600"
                />
              </div>

              <div>
                <h1 className="text-3xl font-bold text-slate-900">
                  {framework.name}
                </h1>

                <p className="mt-1 text-slate-500">
                  Version {framework.version} · Framework #{framework.id}
                </p>
              </div>
            </div>
          </div>

          <Can
            resource="frameworks"
            action="update"
          >
            <button
              type="button"
              onClick={() =>
                navigate(
                  `/frameworks/${framework.id}/edit`
                )
              }
              className="flex items-center gap-2 rounded-lg bg-indigo-600 px-4 py-2.5 text-sm font-medium text-white transition hover:bg-indigo-700"
            >
              <Pencil size={16} />
              Edit Framework
            </button>
          </Can>
        </div>

        {/* Overview */}
        <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">
          <div className="border-b bg-slate-50 p-6">
            <h2 className="text-lg font-semibold text-slate-900">
              Overview
            </h2>
          </div>

          <div className="space-y-6 p-6">
            <p className="whitespace-pre-line text-slate-700">
              {framework.description || "No description provided."}
            </p>

            <div className="grid gap-6 md:grid-cols-3">
              <div>
                <p className="text-sm font-semibold text-slate-500">
                  Requirements
                </p>

                <p className="mt-1 text-2xl font-bold text-slate-900">
                  {requirements.length}
                </p>
              </div>

              <div>
                <p className="text-sm font-semibold text-slate-500">
                  Created
                </p>

                <p className="mt-1 flex items-center gap-2 text-slate-900">
                  <CalendarDays
                    size={16}
                    className="text-slate-400"
                  />
                  {formatDate(framework.created_at)}
                </p>
              </div>

              <div>
                <p className="text-sm font-semibold text-slate-500">
                  Last updated
                </p>

                <p className="mt-1 flex items-center gap-2 text-slate-900">
                  <CalendarDays
                    size={16}
                    className="text-slate-400"
                  />
                  {formatDate(framework.updated_at)}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Requirements */}
        <div className="overflow-hidden rounded-2xl border bg-white shadow-sm">
          <div className="flex flex-wrap items-center justify-between gap-3 border-b bg-slate-50 p-6">
            <div>
              <h2 className="text-lg font-semibold text-slate-900">
                Requirements
              </h2>

              <p className="text-sm text-slate-500">
                {visibleRequirements.length} of {requirements.length} shown
              </p>
            </div>

            <div className="relative w-full max-w-xs">
              <Search
                size={16}
                className="pointer-events-none absolute left-3 top-1/2 -translate-y-1/2 text-slate-400"
              />

              <input
                type="search"
                value={search}
                onChange={(event) =>
                  setSearch(event.target.value)
                }
                placeholder="Search code or title"
                aria-label="Search requirements"
                className="w-full rounded-lg border border-slate-300 py-2 pl-9 pr-3 text-sm outline-none focus:border-blue-500"
              />
            </div>
          </div>

          {visibleRequirements.length === 0 ? (
            <p className="p-6 text-sm text-slate-500">
              {requirements.length === 0
                ? "This framework has no requirements yet."
                : "No requirements match your search."}
            </p>
          ) : (
            <ul className="divide-y">
              {visibleRequirements.map((requirement) => (
                <li
                  key={requirement.id}
                  className="flex items-center justify-between gap-4 px-6 py-4"
                >
                  <div className="min-w-0">
                    <p className="font-mono text-sm font-semibold text-blue-600">
                      {requirement.control_code}
                    </p>

                    <p className="truncate font-medium text-slate-900">
                      {requirement.title}
                    </p>
                  </div>

                  <button
                    type="button"
                    onClick={() =>
                      navigate(
                        `/framework-controls/${requirement.id}`
                      )
                    }
                    className="flex shrink-0 items-center gap-2 rounded-lg border px-3 py-1.5 text-sm font-medium text-slate-700 transition hover:bg-slate-50"
                  >
                    <Eye size={16} />
                    View
                  </button>
                </li>
              ))}
            </ul>
          )}
        </div>
      </div>
    </AppLayout>
  );
}
