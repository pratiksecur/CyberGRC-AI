import { useState } from "react";
import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useCreateEvidence } from "@/hooks/useCreateEvidence";
import { useControls } from "@/hooks/useControls";

export default function CreateEvidence() {
  const navigate = useNavigate();

  const createMutation = useCreateEvidence();

  const { data: controls } = useControls();

  const [controlId, setControlId] = useState<number>(0);

  const [title, setTitle] = useState("");

  const [description, setDescription] = useState("");

  const [selectedFile, setSelectedFile] =
    useState<File | null>(null);

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    if (controlId === 0) {
      alert("Please select a control.");
      return;
    }

    if (!selectedFile) {
      alert("Please select a file.");
      return;
    }

    const formData = new FormData();

    formData.append(
    "control_id",
    controlId.toString()
    );

    formData.append(
    "title",
    title
    );

    formData.append(
    "description",
    description
    );

    formData.append(
    "uploaded_by",
    "1"
    );

    formData.append(
    "file",
    selectedFile
    );

    await createMutation.mutateAsync(
    formData
    );

    navigate("/evidence");
  };

  return (
    <AppLayout>
      <div className="mx-auto max-w-3xl">

        <h1 className="mb-2 text-3xl font-bold">
          Upload Evidence
        </h1>

        <p className="mb-8 text-slate-500">
          Upload cybersecurity evidence.
        </p>

        <form
          onSubmit={handleSubmit}
          className="space-y-6 rounded-2xl border bg-white p-8"
        >

          {/* Control */}

          <div>

            <label className="mb-2 block font-medium">
              Control
            </label>

            <select
              className="w-full rounded-lg border p-3"
              value={controlId}
              onChange={(e) =>
                setControlId(Number(e.target.value))
              }
            >
              <option value={0}>
                Select Control
              </option>

              {controls?.map((control) => (
                <option
                  key={control.id}
                  value={control.id}
                >
                  {control.title}
                </option>
              ))}

            </select>

          </div>

          {/* Evidence Title */}

          <div>

            <label className="mb-2 block font-medium">
              Evidence Title
            </label>

            <input
              className="w-full rounded-lg border p-3"
              value={title}
              onChange={(e) =>
                setTitle(e.target.value)
              }
            />

          </div>

          {/* Description */}

          <div>

            <label className="mb-2 block font-medium">
              Description
            </label>

            <textarea
              rows={5}
              className="w-full rounded-lg border p-3"
              value={description}
              onChange={(e) =>
                setDescription(e.target.value)
              }
            />

          </div>

          {/* File Upload */}

          <div>

            <label className="mb-2 block font-medium">
              Evidence File
            </label>

            <input
              type="file"
              className="w-full rounded-lg border p-3"
              onChange={(e) => {
                const file =
                  e.target.files?.[0] ?? null;

                setSelectedFile(file);
              }}
            />

            {selectedFile && (
              <p className="mt-2 text-sm text-slate-500">
                Selected File:
                {" "}
                <strong>
                  {selectedFile.name}
                </strong>
              </p>
            )}

          </div>

          <div className="flex justify-end">

            <button
              type="submit"
              disabled={createMutation.isPending}
              className="rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {createMutation.isPending
                ? "Uploading..."
                : "Upload Evidence"}
            </button>

          </div>

        </form>

      </div>
    </AppLayout>
  );
}