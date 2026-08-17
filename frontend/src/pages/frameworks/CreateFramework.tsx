import { useState } from "react";
import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useCreateFramework } from "@/hooks/useCreateFramework";

export default function CreateFramework() {
  const navigate = useNavigate();

  const mutation = useCreateFramework();

  const [name, setName] = useState("");

  const [version, setVersion] = useState("");

  const [description, setDescription] =
    useState("");

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    await mutation.mutateAsync({
      name,
      version,
      description,
    });

    navigate("/frameworks");
  };

  return (
    <AppLayout>

      <div className="mx-auto max-w-3xl">

        <h1 className="mb-2 text-3xl font-bold">
          Create Framework
        </h1>

        <p className="mb-8 text-slate-500">
          Add a new compliance framework.
        </p>

        <form
          onSubmit={handleSubmit}
          className="space-y-6 rounded-2xl border bg-white p-8"
        >

          <div>

            <label className="mb-2 block font-medium">
              Framework Name
            </label>

            <input
              className="w-full rounded-lg border p-3"
              value={name}
              onChange={(e) =>
                setName(e.target.value)
              }
              required
            />

          </div>

          <div>

            <label className="mb-2 block font-medium">
              Version
            </label>

            <input
              className="w-full rounded-lg border p-3"
              value={version}
              onChange={(e) =>
                setVersion(e.target.value)
              }
              placeholder="ISO 27001:2022"
              required
            />

          </div>

          <div>

            <label className="mb-2 block font-medium">
              Description
            </label>

            <textarea
              rows={6}
              className="w-full rounded-lg border p-3"
              value={description}
              onChange={(e) =>
                setDescription(e.target.value)
              }
              required
            />

          </div>

          <div className="flex justify-end">

            <button
              type="submit"
              disabled={mutation.isPending}
              className="rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:opacity-50"
            >
              {mutation.isPending
                ? "Creating..."
                : "Create Framework"}
            </button>

          </div>

        </form>

      </div>

    </AppLayout>
  );
}