import { useNavigate, useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useRisk } from "@/hooks/useRisk";
import { useUpdateRisk } from "@/hooks/useUpdateRisk";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";

import { useState, useEffect } from "react";

export default function EditRisk() {

  const { id } = useParams();

  const navigate = useNavigate();

  const {
    data,
    isLoading,
  } = useRisk(Number(id));

  const updateRisk = useUpdateRisk(Number(id));

  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [likelihood, setLikelihood] = useState(1);
  const [impact, setImpact] = useState(1);
  const [ownerId, setOwnerId] = useState(1);

  useEffect(() => {

    if (!data) return;

    setTitle(data.title);
    setDescription(data.description);
    setLikelihood(data.likelihood);
    setImpact(data.impact);
    setOwnerId(data.owner_id);

  }, [data]);

  if (isLoading) {

    return (

      <AppLayout>

        <div className="p-10">

          Loading...

        </div>

      </AppLayout>

    );

  }

  async function handleSubmit(
    e: React.FormEvent
  ) {

    e.preventDefault();

    await updateRisk.mutateAsync({

      title,

      description,

      likelihood,

      impact,

      owner_id: ownerId,

    });

    navigate(`/risks/${id}`);

  }

  return (

    <AppLayout>

      <div className="mx-auto max-w-3xl">

        <h1 className="mb-8 text-3xl font-bold">

          Edit Risk

        </h1>

        <form
          onSubmit={handleSubmit}
          className="space-y-5"
        >

          <Input
            value={title}
            onChange={(e) =>
              setTitle(e.target.value)
            }
          />

          <Input
            value={description}
            onChange={(e) =>
              setDescription(e.target.value)
            }
          />

          <Input
            type="number"
            value={likelihood}
            onChange={(e) =>
              setLikelihood(Number(e.target.value))
            }
          />

          <Input
            type="number"
            value={impact}
            onChange={(e) =>
              setImpact(Number(e.target.value))
            }
          />

          <Input
            type="number"
            value={ownerId}
            onChange={(e) =>
              setOwnerId(Number(e.target.value))
            }
          />

          <Button type="submit">

            Save Changes

          </Button>

        </form>

      </div>

    </AppLayout>

  );

}