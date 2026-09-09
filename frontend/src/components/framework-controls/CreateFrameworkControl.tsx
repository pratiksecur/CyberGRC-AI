import { useNavigate } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useFrameworks } from "@/hooks/useFrameworks";
import { useCreateFrameworkControl } from "@/hooks/useCreateFrameworkControl";

import Can from "@/components/auth/Can";

import FrameworkControlForm from "@/components/framework-controls/FrameworkControlForm";

export default function CreateFrameworkControl() {
  const navigate = useNavigate();

  const {
    data: frameworks,
    isLoading,
    error,
  } = useFrameworks();

  const mutation =
    useCreateFrameworkControl();

  if (isLoading) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading frameworks...
        </div>
      </AppLayout>
    );
  }

  if (error || !frameworks) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Failed to load frameworks.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>

      <div className="mx-auto max-w-3xl">

        <h1 className="mb-2 text-3xl font-bold">
          Create Framework Control
        </h1>

        <p className="mb-8 text-slate-500">
          Add a control requirement to a compliance framework.
        </p>

        <Can
          resource="framework_controls"
          action="create"
        >
          <FrameworkControlForm
            frameworks={frameworks}
            submitLabel="Create Framework Control"
            loading={mutation.isPending}
            onSubmit={async (data) => {
              if (
                !data.framework_id
              ) {
                alert(
                  "Please select a framework."
                );
                return;
              }

              try {
                await mutation.mutateAsync({
                  framework_id:
                    data.framework_id,
                  control_code:
                    data.control_code,
                  title: data.title,
                  description:
                    data.description,
                });

                navigate(
                  "/framework-controls"
                );
              } catch (error) {
                console.error(error);
                alert(
                  "Failed to create framework control."
                );
              }
            }}
          />
        </Can>

      </div>

    </AppLayout>
  );
}