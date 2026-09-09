import { useEffect, useState } from "react";

import type {
  Framework,
} from "@/api/frameworks";

interface Props {
  frameworks: Framework[];
  initialValues?: {
    framework_id?: number;
    control_code?: string;
    title?: string;
    description?: string;
  };
  submitLabel: string;
  loading?: boolean;
  onSubmit: (data: {
    framework_id?: number;
    control_code: string;
    title: string;
    description: string;
  }) => void;
}

export default function FrameworkControlForm({
  frameworks,
  initialValues,
  submitLabel,
  loading = false,
  onSubmit,
}: Props) {
  const [frameworkId, setFrameworkId] =
    useState(
      initialValues?.framework_id
        ? String(initialValues.framework_id)
        : ""
    );

  const [controlCode, setControlCode] =
    useState(
      initialValues?.control_code ?? ""
    );

  const [title, setTitle] =
    useState(
      initialValues?.title ?? ""
    );

  const [description, setDescription] =
    useState(
      initialValues?.description ?? ""
    );

  useEffect(() => {
    if (!initialValues) return;

    setFrameworkId(
      initialValues.framework_id
        ? String(initialValues.framework_id)
        : ""
    );

    setControlCode(
      initialValues.control_code ?? ""
    );

    setTitle(
      initialValues.title ?? ""
    );

    setDescription(
      initialValues.description ?? ""
    );
  }, [initialValues]);

  function handleSubmit(
    event: React.FormEvent
  ) {
    event.preventDefault();

    onSubmit({
      framework_id: frameworkId
        ? Number(frameworkId)
        : undefined,
      control_code: controlCode,
      title,
      description,
    });
  }

  return (
    <form
      onSubmit={handleSubmit}
      className="space-y-6 rounded-2xl border bg-white p-8"
    >

      <div>

        <label className="mb-2 block font-medium">
          Framework
        </label>

        <select
          value={frameworkId}
          onChange={(e) =>
            setFrameworkId(e.target.value)
          }
          required
          disabled={
            !!initialValues?.framework_id
          }
          className="w-full rounded-lg border p-3 disabled:bg-slate-100"
        >
          <option value="">
            Select Framework
          </option>

          {frameworks.map((framework) => (
            <option
              key={framework.id}
              value={framework.id}
            >
              {framework.name} {framework.version}
            </option>
          ))}

        </select>

      </div>

      <div>

        <label className="mb-2 block font-medium">
          Control Code
        </label>

        <input
          value={controlCode}
          onChange={(e) =>
            setControlCode(e.target.value)
          }
          required
          maxLength={50}
          className="w-full rounded-lg border p-3"
          placeholder="A.5.1"
        />

      </div>

      <div>

        <label className="mb-2 block font-medium">
          Title
        </label>

        <input
          value={title}
          onChange={(e) =>
            setTitle(e.target.value)
          }
          required
          minLength={3}
          className="w-full rounded-lg border p-3"
          placeholder="Policies for information security"
        />

      </div>

      <div>

        <label className="mb-2 block font-medium">
          Description
        </label>

        <textarea
          value={description}
          onChange={(e) =>
            setDescription(e.target.value)
          }
          required
          minLength={10}
          rows={6}
          className="w-full rounded-lg border p-3"
        />

      </div>

      <div className="flex justify-end">

        <button
          type="submit"
          disabled={loading}
          className="rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:opacity-50"
        >
          {loading
            ? "Saving..."
            : submitLabel}
        </button>

      </div>

    </form>
  );
}