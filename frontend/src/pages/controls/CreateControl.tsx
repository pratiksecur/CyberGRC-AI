import { useState } from "react";
import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";
import { useCreateControl } from "@/hooks/useCreateControl";

export default function CreateControl() {

  const navigate = useNavigate();

  const createControl = useCreateControl();

  const [title, setTitle] = useState("");

  const [description, setDescription] = useState("");

  const [controlType, setControlType] =
    useState("Technical");

  const [status, setStatus] =
    useState("Active");

  const [effectiveness, setEffectiveness] =
    useState(100);

  const [ownerId, setOwnerId] =
    useState(1);

  async function handleSubmit(
    e: React.FormEvent
  ) {

    e.preventDefault();

    if (!title.trim()) {
      alert("Control title is required.");
      return;
    }

    if (!description.trim()) {
      alert("Description is required.");
      return;
    }

    try {

      await createControl.mutateAsync({

        title,

        description,

        control_type: controlType,

        status,

        effectiveness,

        owner_id: ownerId,

      });

      alert("Control created successfully!");

      navigate("/controls");

    } catch {

      alert("Failed to create control.");

    }

  }

  return (

    <AppLayout>

      <div className="mx-auto max-w-3xl space-y-8">

        <div>

          <h1 className="text-3xl font-bold">

            Create Control

          </h1>

          <p className="mt-2 text-slate-500">

            Add a new cybersecurity control.

          </p>

        </div>

        <form
          onSubmit={handleSubmit}
          className="rounded-2xl border bg-white p-8"
        >

          <div className="space-y-6">

            <div>

              <label className="mb-2 block text-sm font-medium">

                Control Title

              </label>

              <input
                type="text"
                value={title}
                onChange={(e) =>
                  setTitle(e.target.value)
                }
                className="w-full rounded-lg border px-4 py-3"
                placeholder="Enter control title"
              />

            </div>

            <div>

              <label className="mb-2 block text-sm font-medium">

                Description

              </label>

              <textarea
                rows={5}
                value={description}
                onChange={(e) =>
                  setDescription(e.target.value)
                }
                className="w-full rounded-lg border px-4 py-3"
                placeholder="Describe this control"
              />

            </div>

            <div className="grid gap-6 md:grid-cols-2">

              <div>

                <label className="mb-2 block text-sm font-medium">

                  Control Type

                </label>

                <select
                  value={controlType}
                  onChange={(e) =>
                    setControlType(
                      e.target.value
                    )
                  }
                  className="w-full rounded-lg border px-4 py-3"
                >

                  <option value="Technical">
                    Technical
                  </option>

                  <option value="Administrative">
                    Administrative
                  </option>

                  <option value="Physical">
                    Physical
                  </option>

                  <option value="Preventive">
                    Preventive
                  </option>

                  <option value="Detective">
                    Detective
                  </option>

                  <option value="Corrective">
                    Corrective
                  </option>

                </select>

              </div>

              <div>

                <label className="mb-2 block text-sm font-medium">

                  Status

                </label>

                <select
                  value={status}
                  onChange={(e) =>
                    setStatus(
                      e.target.value
                    )
                  }
                  className="w-full rounded-lg border px-4 py-3"
                >

                  <option value="Active">
                    Active
                  </option>

                  <option value="Inactive">
                    Inactive
                  </option>

                </select>

              </div>

            </div>

            <div>

              <label className="mb-2 block text-sm font-medium">

                Effectiveness (%)

              </label>

              <input
                type="number"
                min={0}
                max={100}
                value={effectiveness}
                onChange={(e) =>
                  setEffectiveness(
                    Number(e.target.value)
                  )
                }
                className="w-full rounded-lg border px-4 py-3"
              />

            </div>

            <div>

              <label className="mb-2 block text-sm font-medium">

                Owner ID

              </label>

              <input
                type="number"
                value={ownerId}
                onChange={(e) =>
                  setOwnerId(
                    Number(e.target.value)
                  )
                }
                className="w-full rounded-lg border px-4 py-3"
              />

            </div>

            <div className="flex justify-end">

              <button
                type="submit"
                disabled={createControl.isPending}
                className="rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
              >

                {createControl.isPending
                  ? "Creating..."
                  : "Create Control"}

              </button>

            </div>

          </div>

        </form>

      </div>

    </AppLayout>

  );

}