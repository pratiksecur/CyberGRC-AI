import { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useFramework } from "@/hooks/useFramework";
import { useUpdateFramework } from "@/hooks/useUpdateFramework";

import { AxiosError } from "axios";

import Can from "@/components/auth/Can";

export default function EditFramework() {
  const { id } = useParams();

  const frameworkId = Number(id);

  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
  } = useFramework(frameworkId);

  const updateMutation =
    useUpdateFramework(frameworkId);

  const [name, setName] = useState("");
  const [version, setVersion] = useState("");
  const [description, setDescription] =
    useState("");

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (data) {
      setName(data.name);
      setVersion(data.version);
      setDescription(data.description);
    }
  }, [data]);
  /* eslint-enable react-hooks/set-state-in-effect */

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    try {
      await updateMutation.mutateAsync({
        name,
        version,
        description,
      });

      navigate("/frameworks");
    } catch (error: unknown) {
      const axiosError =
        error instanceof AxiosError
          ? error
          : null;

      const responseData =
        axiosError?.response?.data as
          | {
              error?: {
                message?: string;
              };
            }
          | undefined;

      alert(
        responseData?.error?.message ??
          "Failed to update framework."
      );
    }
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
          Failed to load framework.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>

      <div className="mx-auto max-w-3xl">

        <h1 className="mb-2 text-3xl font-bold">
          Edit Framework
        </h1>

        <p className="mb-8 text-slate-500">
          Update an existing framework.
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
            />

          </div>

          <div className="flex justify-end">

            <Can
              resource="frameworks"
              action="update"
            >
              <button
                type="submit"
                disabled={updateMutation.isPending}
                className="rounded-lg bg-blue-600 px-6 py-3 text-white hover:bg-blue-700 disabled:opacity-50"
              >
                {updateMutation.isPending
                  ? "Updating..."
                  : "Update Framework"}
              </button>
            </Can>

          </div>

        </form>

      </div>

    </AppLayout>
  );
}