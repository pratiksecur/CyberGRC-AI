import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";
import { Input } from "@/components/ui/input";

import { useCreateRisk } from "@/hooks/useCreateRisk";
import { useVisibleUsers } from "@/hooks/useVisibleUsers";

export default function CreateRisk() {

  const navigate = useNavigate();

  const createRiskMutation = useCreateRisk();

  const {
    data: visibleUsers,
    isLoading: usersLoading,
    isError: usersError,
  } = useVisibleUsers();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");

  const [likelihood, setLikelihood] = useState(1);
  const [impact, setImpact] = useState(1);

  const [ownerId, setOwnerId] = useState<number | null>(
    null
  );

  // ------------------------------------------------------
  // Select current user by default
  // ------------------------------------------------------

  /* eslint-disable react-hooks/set-state-in-effect */
  useEffect(() => {
    if (
      ownerId === null &&
      visibleUsers &&
      visibleUsers.length > 0
    ) {
      const currentUser = visibleUsers[0];

      setOwnerId(currentUser.id);
    }
  }, [visibleUsers, ownerId]);
  /* eslint-enable react-hooks/set-state-in-effect */


  const handleSubmit = async (
    e: React.FormEvent
  ) => {

    e.preventDefault();

    if (ownerId === null) {
      alert("Please select a risk owner.");
      return;
    }

    try {

      await createRiskMutation.mutateAsync({
        title,
        description,
        likelihood,
        impact,
        owner_id: ownerId,
      });

      navigate("/risks");

    } catch (error) {

      console.error(error);

      alert("Failed to create risk.");

    }

  };


  return (
    <AppLayout>

      <div className="mx-auto max-w-3xl space-y-8">

        {/* ================================================== */}
        {/* HEADER */}
        {/* ================================================== */}

        <div>

          <h1 className="text-3xl font-bold">
            Create Risk
          </h1>

          <p className="text-slate-500">
            Add a new cybersecurity risk.
          </p>

        </div>


        {/* ================================================== */}
        {/* FORM */}
        {/* ================================================== */}

        <div className="rounded-xl border bg-white p-8 shadow-sm">

          <form
            onSubmit={handleSubmit}
            className="space-y-6"
          >

            {/* Risk Title */}

            <div>

              <label className="mb-2 block text-sm font-medium">
                Risk Title
              </label>

              <Input
                value={title}
                onChange={(e) =>
                  setTitle(e.target.value)
                }
                placeholder="SQL Injection Vulnerability"
                required
              />

            </div>


            {/* Description */}

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
                placeholder="Describe the cybersecurity risk..."
                required
                className="w-full rounded-lg border p-3"
              />

            </div>


            {/* Likelihood + Impact */}

            <div className="grid gap-6 md:grid-cols-2">

              <div>

                <label className="mb-2 block text-sm font-medium">
                  Likelihood (1-5)
                </label>

                <Input
                  type="number"
                  min={1}
                  max={5}
                  value={likelihood}
                  onChange={(e) =>
                    setLikelihood(
                      Number(e.target.value)
                    )
                  }
                  required
                />

              </div>


              <div>

                <label className="mb-2 block text-sm font-medium">
                  Impact (1-5)
                </label>

                <Input
                  type="number"
                  min={1}
                  max={5}
                  value={impact}
                  onChange={(e) =>
                    setImpact(
                      Number(e.target.value)
                    )
                  }
                  required
                />

              </div>

            </div>


            {/* ================================================== */}
            {/* RISK OWNER */}
            {/* ================================================== */}

            <div>

              <label className="mb-2 block text-sm font-medium">
                Risk Owner
              </label>

              {usersLoading ? (

                <div className="rounded-lg border bg-slate-50 px-4 py-3 text-sm text-slate-500">
                  Loading available users...
                </div>

              ) : usersError ? (

                <div className="rounded-lg border border-red-200 bg-red-50 px-4 py-3 text-sm text-red-600">
                  Unable to load available risk owners.
                </div>

              ) : (

                <select
                  value={ownerId ?? ""}
                  onChange={(e) =>
                    setOwnerId(
                      Number(e.target.value)
                    )
                  }
                  required
                  className="w-full rounded-lg border border-slate-300 bg-white px-4 py-3 focus:border-blue-500 focus:outline-none"
                >

                  <option value="" disabled>
                    Select risk owner
                  </option>

                  {visibleUsers?.map((user) => (

                    <option
                      key={user.id}
                      value={user.id}
                    >
                      {user.full_name} — {user.role}
                    </option>

                  ))}

                </select>

              )}

            </div>


            {/* ================================================== */}
            {/* ACTIONS */}
            {/* ================================================== */}

            <div className="flex justify-end gap-4">

              <button
                type="button"
                onClick={() =>
                  navigate("/risks")
                }
                className="rounded-lg border px-5 py-2"
              >
                Cancel
              </button>


              <button
                type="submit"
                disabled={
                  createRiskMutation.isPending ||
                  usersLoading ||
                  ownerId === null
                }
                className="rounded-lg bg-blue-600 px-5 py-2 text-white hover:bg-blue-700 disabled:opacity-50"
              >

                {createRiskMutation.isPending
                  ? "Creating..."
                  : "Create Risk"}

              </button>

            </div>

          </form>

        </div>

      </div>

    </AppLayout>
  );
}