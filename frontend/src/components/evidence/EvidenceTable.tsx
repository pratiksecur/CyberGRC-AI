import {
  Eye,
  Pencil,
  Trash2,
  Download,
  FileText,
} from "lucide-react";

import {
  downloadEvidence,
  openEvidence,
} from "@/api/evidence";

interface Evidence {
  id: number;
  title: string;
  description: string;
  file_name: string;
  file_path: string;
  control_id: number;
  uploaded_by: number;
  uploaded_at: string;
}

interface Props {
  evidence: Evidence[];
  onEdit?: (id: number) => void;
  onDelete?: (id: number) => void;
}

export default function EvidenceTable({
  evidence,
  onEdit,
  onDelete,
}: Props) {

  const handleView = async (
    id: number
  ) => {
    try {
      await openEvidence(id);
    } catch {
      // The API/client layer handles authentication errors.
    }
  };


  const handleDownload = async (
    item: Evidence
  ) => {
    try {
      const blob =
        await downloadEvidence(item.id);

      const objectUrl =
        URL.createObjectURL(blob);

      const link =
        document.createElement("a");

      link.href = objectUrl;
      link.download = item.file_name;

      document.body.appendChild(link);

      link.click();

      document.body.removeChild(link);

      URL.revokeObjectURL(objectUrl);

    } catch {
      // Keep download failures inside the API
      // error handling flow.
    }
  };


  return (
    <div className="overflow-hidden rounded-2xl border bg-white">

      <div className="border-b p-5">

        <h2 className="text-lg font-semibold">
          Evidence
        </h2>

        <p className="text-sm text-slate-500">
          Manage uploaded cybersecurity evidence
        </p>

      </div>

      <div className="overflow-x-auto">

        <table className="min-w-full">

          <thead className="border-b bg-slate-50">

            <tr>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Evidence
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                File
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Control
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Uploaded By
              </th>

              <th className="px-6 py-4 text-left text-sm font-semibold">
                Uploaded
              </th>

              <th className="px-6 py-4 text-center text-sm font-semibold">
                Actions
              </th>

            </tr>

          </thead>

          <tbody>

            {evidence.length === 0 ? (

              <tr>

                <td
                  colSpan={6}
                  className="py-10 text-center text-slate-500"
                >
                  No evidence found.
                </td>

              </tr>

            ) : (

              evidence.map((item) => (

                <tr
                  key={item.id}
                  className="border-b hover:bg-slate-50"
                >

                  <td className="px-6 py-5">

                    <div className="flex items-center gap-3">

                      <div className="rounded-lg bg-blue-100 p-2">

                        <FileText className="h-5 w-5 text-blue-600" />

                      </div>

                      <div>

                        <div className="font-medium">
                          {item.title}
                        </div>

                        <div className="text-sm text-slate-500 line-clamp-1">
                          {item.description}
                        </div>

                      </div>

                    </div>

                  </td>

                  <td className="px-6 py-5">
                    {item.file_name}
                  </td>

                  <td className="px-6 py-5">
                    Control #{item.control_id}
                  </td>

                  <td className="px-6 py-5">
                    User #{item.uploaded_by}
                  </td>

                  <td className="px-6 py-5">
                    {new Date(
                      item.uploaded_at
                    ).toLocaleDateString()}
                  </td>

                  <td className="px-6 py-5">

                    <div className="flex justify-center gap-3">

                      <button
                        onClick={() =>
                          handleView(item.id)
                        }
                        className="text-slate-500 hover:text-blue-600"
                        title="View"
                      >
                        <Eye size={18} />
                      </button>


                      <button
                        onClick={() =>
                          handleDownload(item)
                        }
                        className="text-slate-500 hover:text-green-600"
                        title="Download"
                      >
                        <Download size={18} />
                      </button>


                      <button
                        onClick={() =>
                          onEdit?.(item.id)
                        }
                        className="text-slate-500 hover:text-amber-600"
                        title="Edit"
                      >
                        <Pencil size={18} />
                      </button>


                      <button
                        onClick={() =>
                          onDelete?.(item.id)
                        }
                        className="text-slate-500 hover:text-red-600"
                        title="Delete"
                      >
                        <Trash2 size={18} />
                      </button>

                    </div>

                  </td>

                </tr>

              ))

            )}

          </tbody>

        </table>

      </div>

    </div>
  );
}