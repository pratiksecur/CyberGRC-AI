import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useControl } from "@/hooks/useControl";
import { useUpdateControl } from "@/hooks/useUpdateControl";

export default function EditControl() {
  const { id } = useParams();

  const controlId = Number(id);

  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
  } = useControl(controlId);

  const updateMutation = useUpdateControl(controlId);

  const [title, setTitle] = useState("");

  const [description, setDescription] = useState("");

  const [controlType, setControlType] = useState("");

  const [status, setStatus] = useState("");

  const [effectiveness, setEffectiveness] =
    useState(0);

  const [ownerId, setOwnerId] = useState(1);

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (data) {
      setTitle(data.title);
      setDescription(data.description);
      setControlType(data.control_type);
      setStatus(data.status);
      setEffectiveness(data.effectiveness);
      setOwnerId(data.owner_id);
    }
  }, [data]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    await updateMutation.mutateAsync({
      title,
      description,
      control_type: controlType,
      status,
      effectiveness,
      owner_id: ownerId,
    });

    navigate("/controls");
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
          Failed to load control.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>

      <div className="mx-auto max-w-3xl">

        <h1 className="mb-2 text-3xl font-bold">
          Edit Control
        </h1>

        <p className="mb-8 text-slate-500">
          Update an existing control.
        </p>

        <form
          onSubmit={handleSubmit}
          className="space-y-6 rounded-2xl border bg-white p-8"
        >

          <div>

            <label className="mb-2 block font-medium">
              Title
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
                setDescription(e.target.value)
              }
            />

          </div>

          <div className="grid grid-cols-2 gap-6">

            <div>

              <label className="mb-2 block font-medium">
                Type
              </label>

              <select
                className="w-full rounded-lg border p-3"
                value={controlType}
                onChange={(e) =>
                  setControlType(e.target.value)
                }
              >
                <option>Technical</option>
                <option>Administrative</option>
                <option>Physical</option>
                <option>Preventive</option>
                <option>Detective</option>
                <option>Corrective</option>
              </select>

            </div>

            <div>

              <label className="mb-2 block font-medium">
                Status
              </label>

              <select
                className="w-full rounded-lg border p-3"
                value={status}
                onChange={(e) =>
                  setStatus(e.target.value)
                }
              >
                <option>Active</option>
                <option>Inactive</option>
              </select>

            </div>

          </div>

          <div>

            <label className="mb-2 block font-medium">
              Effectiveness
            </label>

            <input
              type="number"
              className="w-full rounded-lg border p-3"
              value={effectiveness}
              onChange={(e) =>
                setEffectiveness(
                  Number(e.target.value)
                )
              }
            />

          </div>

          <div>

            <label className="mb-2 block font-medium">
              Owner ID
            </label>

            <input
              type="number"
              className="w-full rounded-lg border p-3"
              value={ownerId}
              onChange={(e) =>
                setOwnerId(
                  Number(e.target.value)
                )
              }
            />

          </div>

          <div className="flex justify-end">

            <button
              type="submit"
              disabled={updateMutation.isPending}
              className="rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {updateMutation.isPending
                ? "Updating..."
                : "Update Control"}
            </button>

          </div>

        </form>

      </div>

    </AppLayout>
  );
}