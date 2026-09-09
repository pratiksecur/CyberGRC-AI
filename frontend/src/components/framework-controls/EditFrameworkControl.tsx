import { useNavigate, useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useFrameworkControl } from "@/hooks/useFrameworkControl";
import { useFrameworks } from "@/hooks/useFrameworks";
import { useUpdateFrameworkControl } from "@/hooks/useUpdateFrameworkControl";

import Can from "@/components/auth/Can";

import FrameworkControlForm from "@/components/framework-controls/FrameworkControlForm";

export default function EditFrameworkControl() {
  const { id } = useParams();

  const frameworkControlId =
    Number(id);

  const navigate = useNavigate();

  const {
    data: control,
    isLoading: controlLoading,
    error: controlError,
  } = useFrameworkControl(
    frameworkControlId
  );

  const {
    data: frameworks,
    isLoading: frameworksLoading,
  } = useFrameworks();

  const mutation =
    useUpdateFrameworkControl(
      frameworkControlId
    );

  if (
    controlLoading ||
    frameworksLoading
  ) {
    return (
      <AppLayout>
        <div className="p-10">
          Loading framework control...
        </div>
      </AppLayout>
    );
  }

  if (
    controlError ||
    !control ||
    !frameworks
  ) {
    return (
      <AppLayout>
        <div className="p-10 text-red-500">
          Failed to load framework control.
        </div>
      </AppLayout>
    );
  }

  return (
    <AppLayout>

      <div className="mx-auto max-w-3xl">

        <h1 className="mb-2 text-3xl font-bold">
          Edit Framework Control
        </h1>

        <p className="mb-8 text-slate-500">
          Update the framework control requirement.
        </p>

        <Can
          resource="framework_controls"
          action="update"
        >
          <FrameworkControlForm
            frameworks={frameworks}
            initialValues={{
              framework_id:
                control.framework_id,
              control_code:
                control.control_code,
              title: control.title,
              description:
                control.description,
            }}
            submitLabel="Update Framework Control"
            loading={mutation.isPending}
            onSubmit={async (data) => {
              try {
                await mutation.mutateAsync({
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
                  "Failed to update framework control."
                );
              }
            }}
          />
        </Can>

      </div>

    </AppLayout>
  );
}