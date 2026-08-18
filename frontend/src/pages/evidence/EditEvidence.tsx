import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useEvidenceItem } from "@/hooks/useEvidenceItem";
import { useUpdateEvidence } from "@/hooks/useUpdateEvidence";

export default function EditEvidence() {
  const { id } = useParams();

  const evidenceId = Number(id);

  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
  } = useEvidenceItem(evidenceId);

  const updateMutation =
    useUpdateEvidence(evidenceId);

  const [title, setTitle] = useState("");

  const [description, setDescription] =
    useState("");

  useEffect(() => {
    if (data) {
      setTitle(data.title);
      setDescription(data.description);
    }
  }, [data]);

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    await updateMutation.mutateAsync({
      title,
      description,
    });

    navigate("/evidence");
  };

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading...
        </div>
      </AppLayout>
    );
  }

  if (error || !data) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Failed to load evidence.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>

      <div className="mx-auto max-w-3xl">

        <h1 className="mb-2 text-3xl font-bold">
          Edit Evidence
        </h1>

        <p className="mb-8 text-slate-500">
          Update evidence details.
        </p>

        <form
          onSubmit={handleSubmit}
          className="space-y-6 rounded-2xl border bg-white p-8"
        >

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

          <div>

            <label className="mb-2 block font-medium">
              Description
            </label>

            <textarea
              rows={5}
              className="w-full rounded-lg border p-3"
              value={description}
              onChange={(e) =>
                setDescription(
                  e.target.value
                )
              }
            />

          </div>

          <div>

            <label className="mb-2 block font-medium">
              Current File
            </label>

            <input
              className="w-full rounded-lg border bg-slate-100 p-3"
              value={data.file_name}
              disabled
            />

          </div>

          <div>

            <label className="mb-2 block font-medium">
              Control ID
            </label>

            <input
              className="w-full rounded-lg border bg-slate-100 p-3"
              value={data.control_id}
              disabled
            />

          </div>

          <div>

            <label className="mb-2 block font-medium">
              Uploaded By
            </label>

            <input
              className="w-full rounded-lg border bg-slate-100 p-3"
              value={`User #${data.uploaded_by}`}
              disabled
            />

          </div>

          <div className="flex justify-end">

            <button
              type="submit"
              disabled={
                updateMutation.isPending
              }
              className="rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {updateMutation.isPending
                ? "Updating..."
                : "Update Evidence"}
            </button>

          </div>

        </form>

      </div>

    </AppLayout>
  );
}