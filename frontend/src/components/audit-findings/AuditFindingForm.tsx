import { useEffect, useState } from "react";
import { useQuery } from "@tanstack/react-query";

import type {
  AuditFinding,
  CreateAuditFindingRequest,
} from "@/api/auditFindings";

import {
  getAudits,
} from "@/api/audits";

import {
  getControls,
} from "@/api/controls";


interface Props {
  mode: "create" | "edit";

  finding?: AuditFinding;

  onSubmit: (
    data: CreateAuditFindingRequest
  ) => void;

  isSubmitting: boolean;

  onCancel: () => void;
}


export default function AuditFindingForm({
  mode,
  finding,
  onSubmit,
  isSubmitting,
  onCancel,
}: Props) {

  const [auditId, setAuditId] =
    useState<number>(
      finding?.audit_id ?? 0
    );

  const [controlId, setControlId] =
    useState<number>(
      finding?.control_id ?? 0
    );

  const [title, setTitle] =
    useState(
      finding?.title ?? ""
    );

  const [description, setDescription] =
    useState(
      finding?.description ?? ""
    );

  const [severity, setSeverity] =
    useState(
      finding?.severity ?? "Medium"
    );

  const [status, setStatus] =
    useState(
      finding?.status ?? "Open"
    );

  const [recommendation, setRecommendation] =
    useState(
      finding?.recommendation ?? ""
    );


  const auditsQuery = useQuery({
    queryKey: ["audits"],
    queryFn: getAudits,
  });


  const controlsQuery = useQuery({
    queryKey: ["controls"],
    queryFn: getControls,
  });


  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (!finding) return;

    setAuditId(finding.audit_id);
    setControlId(finding.control_id);
    setTitle(finding.title);
    setDescription(finding.description);
    setSeverity(finding.severity);
    setStatus(finding.status);
    setRecommendation(finding.recommendation);
  }, [finding]);
  /* eslint-enable react-hooks/set-state-in-effect */


  function handleSubmit(
    e: React.FormEvent
  ) {

    e.preventDefault();


    if (!auditId) {
      alert("Please select an audit.");
      return;
    }


    if (!controlId) {
      alert("Please select a control.");
      return;
    }


    if (!title.trim()) {
      alert("Please enter a title.");
      return;
    }


    if (!description.trim()) {
      alert(
        "Please enter a description."
      );
      return;
    }


    if (!recommendation.trim()) {
      alert(
        "Please enter a recommendation."
      );
      return;
    }


    onSubmit({
      audit_id: auditId,
      control_id: controlId,

      title: title.trim(),

      description:
        description.trim(),

      severity,

      recommendation:
        recommendation.trim(),

      status,
    });

  }


  const isLoading =
    auditsQuery.isLoading ||
    controlsQuery.isLoading;


  if (isLoading) {

    return (
      <div className="rounded-xl border bg-white p-8">

        <div className="text-slate-500">
          Loading audits and controls...
        </div>

      </div>
    );

  }


  if (
    auditsQuery.error ||
    controlsQuery.error
  ) {

    return (
      <div className="rounded-xl border bg-white p-8">

        <p className="text-red-500">
          Failed to load audits or controls.
        </p>

        <button
          type="button"
          onClick={onCancel}
          className="mt-4 rounded-lg border px-5 py-2"
        >
          Back
        </button>

      </div>
    );

  }


  const audits =
    auditsQuery.data ?? [];

  const controls =
    controlsQuery.data ?? [];


  return (

    <form
      onSubmit={handleSubmit}
      className="space-y-6 rounded-xl border bg-white p-8"
    >

      {/* Audit */}

      <div>

        <label className="mb-2 block font-medium">
          Audit
        </label>

        <select
          value={auditId}
          onChange={(e) =>
            setAuditId(
              Number(e.target.value)
            )
          }
          required
          className="w-full rounded-lg border p-3"
        >

          <option value={0}>
            Select Audit
          </option>

          {audits.map((audit) => (

            <option
              key={audit.id}
              value={audit.id}
            >
              {audit.name}
            </option>

          ))}

        </select>

      </div>


      {/* Control */}

      <div>

        <label className="mb-2 block font-medium">
          Control
        </label>

        <select
          value={controlId}
          onChange={(e) =>
            setControlId(
              Number(e.target.value)
            )
          }
          required
          className="w-full rounded-lg border p-3"
        >

          <option value={0}>
            Select Control
          </option>

          {controls.map((control) => (

            <option
              key={control.id}
              value={control.id}
            >
              {control.title}
            </option>

          ))}

        </select>

      </div>


      {/* Title */}

      <div>

        <label className="mb-2 block font-medium">
          Title
        </label>

        <input
          required
          minLength={5}
          maxLength={255}
          value={title}
          onChange={(e) =>
            setTitle(e.target.value)
          }
          placeholder="Finding title"
          className="w-full rounded-lg border p-3"
        />

      </div>


      {/* Description */}

      <div>

        <label className="mb-2 block font-medium">
          Description
        </label>

        <textarea
          required
          minLength={10}
          rows={5}
          value={description}
          onChange={(e) =>
            setDescription(
              e.target.value
            )
          }
          placeholder="Describe the audit finding..."
          className="w-full rounded-lg border p-3"
        />

      </div>


      {/* Severity */}

      <div>

        <label className="mb-2 block font-medium">
          Severity
        </label>

        <select
          value={severity}
          onChange={(e) =>
            setSeverity(
              e.target.value
            )
          }
          className="w-full rounded-lg border p-3"
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


      {/* Status */}

      <div>

        <label className="mb-2 block font-medium">
          Status
        </label>

        <select
          value={status}
          onChange={(e) =>
            setStatus(
              e.target.value
            )
          }
          className="w-full rounded-lg border p-3"
        >

          <option value="Open">
            Open
          </option>

          <option value="In Progress">
            In Progress
          </option>

          <option value="Closed">
            Closed
          </option>

        </select>

      </div>


      {/* Recommendation */}

      <div>

        <label className="mb-2 block font-medium">
          Recommendation
        </label>

        <textarea
          required
          minLength={10}
          rows={5}
          value={recommendation}
          onChange={(e) =>
            setRecommendation(
              e.target.value
            )
          }
          placeholder="Recommended remediation..."
          className="w-full rounded-lg border p-3"
        />

      </div>


      {/* Buttons */}

      <div className="flex justify-end gap-4">

        <button
          type="button"
          onClick={onCancel}
          disabled={isSubmitting}
          className="rounded-lg border px-6 py-3 hover:bg-slate-50 disabled:opacity-50"
        >
          Cancel
        </button>


        <button
          type="submit"
          disabled={isSubmitting}
          className="rounded-lg bg-indigo-600 px-6 py-3 text-white hover:bg-indigo-700 disabled:cursor-not-allowed disabled:opacity-50"
        >

          {isSubmitting
            ? mode === "create"
              ? "Creating..."
              : "Saving..."
            : mode === "create"
            ? "Create Finding"
            : "Save Changes"}

        </button>

      </div>

    </form>

  );
}