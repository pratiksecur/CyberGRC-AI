import { useNavigate, useParams } from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import { useEvidenceItem } from "@/hooks/useEvidenceItem";

import {
  downloadEvidence,
  openEvidence,
} from "@/api/evidence";


export default function ViewEvidence() {

  const { id } = useParams();

  const evidenceId = Number(id);

  const navigate = useNavigate();

  const {
    data,
    isLoading,
    error,
  } = useEvidenceItem(evidenceId);


  const handleView = async () => {
    try {
      await openEvidence(evidenceId);
    } catch {
      // API authentication/error handling remains
      // centralized.
    }
  };


  const handleDownload = async () => {
    try {

      const blob =
        await downloadEvidence(
          evidenceId
        );

      const objectUrl =
        URL.createObjectURL(blob);

      const link =
        document.createElement("a");

      link.href = objectUrl;
      link.download = data?.file_name || "evidence";

      document.body.appendChild(link);

      link.click();

      document.body.removeChild(link);

      URL.revokeObjectURL(objectUrl);

    } catch {
      // Keep failure handling inside the API flow.
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
          Failed to load evidence.
        </div>
      </AppLayout>
    );
  }


  return (
    <AppLayout>

      <div className="mx-auto max-w-4xl">

        <div className="mb-8 flex items-center justify-between">

          <div>

            <h1 className="text-3xl font-bold">
              {data.title}
            </h1>

            <p className="mt-2 text-slate-500">
              View uploaded evidence details.
            </p>

          </div>


          <div className="flex gap-3">

            <button
              onClick={() =>
                navigate(
                  `/evidence/${data.id}/edit`
                )
              }
              className="rounded-lg bg-amber-500 px-5 py-2 text-white hover:bg-amber-600"
            >
              Edit
            </button>


            <button
              onClick={() =>
                navigate("/evidence")
              }
              className="rounded-lg border px-5 py-2 hover:bg-slate-100"
            >
              Back
            </button>

          </div>

        </div>


        <div className="space-y-6 rounded-2xl border bg-white p-8">

          <div>

            <h2 className="mb-2 text-sm font-semibold uppercase text-slate-500">
              Title
            </h2>

            <p className="text-lg">
              {data.title}
            </p>

          </div>


          <div>

            <h2 className="mb-2 text-sm font-semibold uppercase text-slate-500">
              Description
            </h2>

            <p>
              {data.description}
            </p>

          </div>


          <div className="grid grid-cols-2 gap-6">

            <div>

              <h2 className="mb-2 text-sm font-semibold uppercase text-slate-500">
                Control ID
              </h2>

              <p>
                {data.control_id}
              </p>

            </div>


            <div>

              <h2 className="mb-2 text-sm font-semibold uppercase text-slate-500">
                Uploaded By
              </h2>

              <p>
                User #{data.uploaded_by}
              </p>

            </div>

          </div>


          <div className="grid grid-cols-2 gap-6">

            <div>

              <h2 className="mb-2 text-sm font-semibold uppercase text-slate-500">
                Uploaded On
              </h2>

              <p>
                {new Date(
                  data.uploaded_at
                ).toLocaleString()}
              </p>

            </div>


            <div>

              <h2 className="mb-2 text-sm font-semibold uppercase text-slate-500">
                File Name
              </h2>

              <p>
                {data.file_name}
              </p>

            </div>

          </div>


          <div>

            <h2 className="mb-3 text-sm font-semibold uppercase text-slate-500">
              Evidence File
            </h2>

            <div className="flex gap-3">

              <button
                onClick={handleView}
                className="rounded-lg bg-blue-600 px-5 py-3 text-white hover:bg-blue-700"
              >
                Open Evidence
              </button>


              <button
                onClick={handleDownload}
                className="rounded-lg border px-5 py-3 hover:bg-slate-100"
              >
                Download Evidence
              </button>

            </div>

          </div>

        </div>

      </div>

    </AppLayout>
  );
}