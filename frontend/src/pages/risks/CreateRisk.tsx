import { useState } from "react";
import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";
import { Input } from "@/components/ui/input";
import { useCreateRisk } from "@/hooks/useCreateRisk";

export default function CreateRisk() {
  const navigate = useNavigate();

  const createRiskMutation = useCreateRisk();

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [likelihood, setLikelihood] = useState(1);
  const [impact, setImpact] = useState(1);
  const [ownerId, setOwnerId] = useState(1);

  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

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

        <div>
          <h1 className="text-3xl font-bold">
            Create Risk
          </h1>

          <p className="text-slate-500">
            Add a new cybersecurity risk.
          </p>
        </div>

        <div className="rounded-xl border bg-white p-8 shadow-sm">

          <form
            onSubmit={handleSubmit}
            className="space-y-6"
          >

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
                placeholder="Describe the cybersecurity risk..."
                className="w-full rounded-lg border p-3"
              />
            </div>

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
                    setLikelihood(Number(e.target.value))
                  }
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
                    setImpact(Number(e.target.value))
                  }
                />
              </div>

            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Owner ID
              </label>

              <Input
                type="number"
                value={ownerId}
                onChange={(e) =>
                  setOwnerId(Number(e.target.value))
                }
              />
            </div>

            <div className="flex justify-end gap-4">

              <button
                type="button"
                onClick={() => navigate("/risks")}
                className="rounded-lg border px-5 py-2"
              >
                Cancel
              </button>

              <button
                type="submit"
                disabled={createRiskMutation.isPending}
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