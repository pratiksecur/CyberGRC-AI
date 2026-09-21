import Can from "@/components/auth/Can";

import { useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useCorrectiveActions } from "@/hooks/useCorrectiveActions";
import { useDeleteCorrectiveAction } from "@/hooks/useDeleteCorrectiveAction";

import CorrectiveActionOverview from "@/components/corrective-actions/CorrectiveActionOverview";
import CorrectiveActionFilters from "@/components/corrective-actions/CorrectiveActionFilters";
import CorrectiveActionTable from "@/components/corrective-actions/CorrectiveActionTable";

import DashboardSkeleton from "@/components/dashboard/DashboardSkeleton";

import { Button } from "@/components/ui/button";
import { Plus } from "lucide-react";

export default function CorrectiveActions() {
  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
  } = useCorrectiveActions();

  const deleteMutation =
    useDeleteCorrectiveAction();

  const [search, setSearch] =
    useState("");

  const [priority, setPriority] =
    useState("");

  const [status, setStatus] =
    useState("");

  const [sort, setSort] =
    useState("");

  const filteredActions = useMemo(() => {
    if (!data) return [];

    let actions = [...data];

    if (search) {
      const query =
        search.toLowerCase();

      actions = actions.filter(
        (action) =>
          action.title
            .toLowerCase()
            .includes(query) ||
          action.description
            .toLowerCase()
            .includes(query) ||
          action.finding_title
            .toLowerCase()
            .includes(query) ||
          action.assignee_name
            .toLowerCase()
            .includes(query)
      );
    }

    if (priority) {
      actions = actions.filter(
        (action) =>
          action.priority === priority
      );
    }

    if (status) {
      actions = actions.filter(
        (action) =>
          action.status === status
      );
    }

    if (sort === "soonest") {
      actions.sort((a, b) => {
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;

        return (
          new Date(a.due_date).getTime() -
          new Date(b.due_date).getTime()
        );
      });
    }

    if (sort === "latest") {
      actions.sort((a, b) => {
        if (!a.due_date) return 1;
        if (!b.due_date) return -1;

        return (
          new Date(b.due_date).getTime() -
          new Date(a.due_date).getTime()
        );
      });
    }

    return actions;
  }, [
    data,
    search,
    priority,
    status,
    sort,
  ]);

  function handleDelete(id: number) {
    const confirmed =
      window.confirm(
        "Are you sure you want to delete this corrective action?"
      );

    if (!confirmed) return;

    deleteMutation.mutate(id);
  }

  if (isLoading) {
    return (
      <AppLayout>
        <DashboardSkeleton />
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="p-10 text-center text-red-500">
          Failed to load corrective actions.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>
      <div className="space-y-6">

        {/* Header */}

        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">
              Corrective Actions
            </h1>

            <p className="text-slate-500">
              Track and manage remediation activities resulting from audit findings.
            </p>
          </div>
          
          <Can
            resource="corrective_actions"
            action="create"
          >
            <Button
              onClick={() =>
                  navigate(
                  "/corrective-actions/new"
                  )
              }
              className="bg-blue-600 text-white shadow-sm hover:bg-blue-700"
              >
              <Plus className="mr-2 h-4 w-4" />
              New Action
            </Button>
          </Can>
        </div>

        {/* Overview */}

        <CorrectiveActionOverview
          actions={filteredActions}
        />

        {/* Filters */}

        <CorrectiveActionFilters
          search={search}
          onSearchChange={setSearch}
          priority={priority}
          onPriorityChange={setPriority}
          status={status}
          onStatusChange={setStatus}
          sort={sort}
          onSortChange={setSort}
        />

        {/* Table */}

        <CorrectiveActionTable
          actions={filteredActions}
          onView={(id) =>
            navigate(
              `/corrective-actions/${id}`
            )
          }
          onEdit={(id) =>
            navigate(
              `/corrective-actions/${id}/edit`
            )
          }
          onDelete={handleDelete}
        />

      </div>
    </AppLayout>
  );
}