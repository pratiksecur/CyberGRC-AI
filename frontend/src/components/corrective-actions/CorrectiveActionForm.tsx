import { useEffect, useState } from "react";

import type {
  CorrectiveAction,
  CreateCorrectiveActionRequest,
} from "@/api/correctiveActions";

import { useAuditFindings } from "@/hooks/useAuditFindings";
import { useCorrectiveActionAssignees } from "@/hooks/useCorrectiveActionAssignees";

interface Props {
  initialData?: CorrectiveAction;

  onSubmit: (
    data: CreateCorrectiveActionRequest
  ) => Promise<void>;

  onCancel: () => void;

  isSubmitting?: boolean;

  submitLabel?: string;
}

export default function CorrectiveActionForm({
  initialData,
  onSubmit,
  onCancel,
  isSubmitting = false,
  submitLabel = "Create Action",
}: Props) {
  /* const isEdit = Boolean(initialData); */

  const {
    data: findings,
    isLoading: findingsLoading,
  } = useAuditFindings();

  const {
    data: assignees,
    isLoading: assigneesLoading,
  } = useCorrectiveActionAssignees();

  const [findingId, setFindingId] =
    useState(
      initialData?.finding_id
        ? String(initialData.finding_id)
        : ""
    );

  const [assignedTo, setAssignedTo] =
    useState(
      initialData?.assigned_to
        ? String(initialData.assigned_to)
        : ""
    );

  const [title, setTitle] =
    useState(initialData?.title ?? "");

  const [description, setDescription] =
    useState(
      initialData?.description ?? ""
    );

  const [priority, setPriority] =
    useState(
      initialData?.priority ?? "Medium"
    );

  const [status, setStatus] =
    useState(
      initialData?.status ?? "Open"
    );

  const [dueDate, setDueDate] =
    useState(
      initialData?.due_date
        ? initialData.due_date.slice(0, 10)
        : ""
    );

  const [comments, setComments] =
    useState(
      initialData?.comments ?? ""
    );

  useEffect(() => {
    if (!initialData) return;

    setFindingId(
      String(initialData.finding_id)
    );

    setAssignedTo(
      String(initialData.assigned_to)
    );

    setTitle(initialData.title);
    setDescription(initialData.description);
    setPriority(initialData.priority);
    setStatus(initialData.status);

    setDueDate(
      initialData.due_date
        ? initialData.due_date.slice(0, 10)
        : ""
    );

    setComments(
      initialData.comments ?? ""
    );
  }, [initialData]);

  async function handleSubmit(
    e: React.FormEvent<HTMLFormElement>
  ) {
    e.preventDefault();

    if (!findingId) {
      alert("Please select an audit finding.");
      return;
    }

    if (!assignedTo) {
      alert("Please select an assignee.");
      return;
    }

    const formData: CreateCorrectiveActionRequest =
      {
        finding_id: Number(findingId),
        assigned_to: Number(assignedTo),
        title: title.trim(),
        description: description.trim(),
        priority,
        status,
        due_date: dueDate,
        completed_at:
          status === "Completed" ||
          status === "Closed"
            ? initialData?.completed_at ?? null
            : null,
        comments:
          comments.trim() || null,
      };

    await onSubmit(formData);
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-6 rounded-xl border bg-white p-8 shadow-sm"
    >
      {/* Finding */}

      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Audit Finding
        </label>

        <select
          required
          value={findingId}
          onChange={(e) =>
            setFindingId(e.target.value)
          }
          disabled={
            findingsLoading || isSubmitting
          }
          className="w-full rounded-lg border border-slate-200 bg-white p-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-50"
        >
          <option value="">
            {findingsLoading
              ? "Loading findings..."
              : "Select an audit finding"}
          </option>

          {findings?.map((finding) => (
            <option
              key={finding.id}
              value={finding.id}
            >
              {finding.title}
            </option>
          ))}
        </select>
      </div>

      {/* Assigned To */}

      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Assigned To
        </label>

        <select
          required
          value={assignedTo}
          onChange={(e) =>
            setAssignedTo(e.target.value)
          }
          disabled={
            assigneesLoading || isSubmitting
          }
          className="w-full rounded-lg border border-slate-200 bg-white p-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-50"
        >
          <option value="">
            {assigneesLoading
              ? "Loading users..."
              : "Select an assignee"}
          </option>

          {assignees?.map((assignee) => (
            <option
              key={assignee.id}
              value={assignee.id}
            >
              {assignee.name}
            </option>
          ))}
        </select>
      </div>

      {/* Title */}

      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Title
        </label>

        <input
          required
          minLength={5}
          value={title}
          onChange={(e) =>
            setTitle(e.target.value)
          }
          placeholder="Corrective action title"
          disabled={isSubmitting}
          className="w-full rounded-lg border border-slate-200 p-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-50"
        />
      </div>

      {/* Description */}

      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Description
        </label>

        <textarea
          required
          minLength={10}
          rows={5}
          value={description}
          onChange={(e) =>
            setDescription(e.target.value)
          }
          placeholder="Describe the corrective action..."
          disabled={isSubmitting}
          className="w-full rounded-lg border border-slate-200 p-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-50"
        />
      </div>

      {/* Priority + Status */}

      <div className="grid gap-6 md:grid-cols-2">
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">
            Priority
          </label>

          <select
            value={priority}
            onChange={(e) =>
              setPriority(e.target.value)
            }
            disabled={isSubmitting}
            className="w-full rounded-lg border border-slate-200 bg-white p-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-50"
          >
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
        </div>

        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">
            Status
          </label>

          <select
            value={status}
            onChange={(e) =>
              setStatus(e.target.value)
            }
            disabled={isSubmitting}
            className="w-full rounded-lg border border-slate-200 bg-white p-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-50"
          >
            <option value="Open">
              Open
            </option>

            <option value="In Progress">
              In Progress
            </option>

            <option value="Completed">
              Completed
            </option>

            <option value="Closed">
              Closed
            </option>
          </select>
        </div>
      </div>

      {/* Due Date */}

      {/* Due Date */}

        <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
            Due Date
        </label>

        <input
            type="date"
            required
            value={dueDate}
            onChange={(e) =>
            setDueDate(e.target.value)
            }
            disabled={isSubmitting}
            className="w-full rounded-lg border border-slate-200 p-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-50"
        />
        </div>

      {/* Comments */}

      <div>
        <label className="mb-2 block text-sm font-medium text-slate-700">
          Comments
        </label>

        <textarea
          rows={4}
          value={comments}
          onChange={(e) =>
            setComments(e.target.value)
          }
          placeholder="Add comments or additional notes..."
          disabled={isSubmitting}
          className="w-full rounded-lg border border-slate-200 p-3 outline-none focus:border-blue-500 focus:ring-2 focus:ring-blue-100 disabled:bg-slate-50"
        />
      </div>

      {/* Buttons */}

      <div className="flex justify-end gap-3 border-t pt-6">
        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="rounded-lg border border-slate-200 px-6 py-3 font-medium text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
        >
          Cancel
        </button>

        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-lg bg-blue-600 px-6 py-3 font-medium text-white transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
        >
          {isSubmitting
            ? "Saving..."
            : submitLabel}
        </button>
      </div>
    </form>
  );
}