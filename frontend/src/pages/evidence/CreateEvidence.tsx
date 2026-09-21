import {
  useRef,
  useState,
} from "react";

import {
  FileUp,
  Upload,
  X,
} from "lucide-react";

import {
  useNavigate,
} from "react-router-dom";

import AppLayout from "@/layouts/AppLayout";

import {
  useCreateEvidence,
} from "@/hooks/useCreateEvidence";

import {
  useControls,
} from "@/hooks/useControls";

import { useAuth } from "@/contexts/useAuth";


const MAX_FILE_SIZE = 10 * 1024 * 1024;

const ALLOWED_EXTENSIONS = [
  ".pdf",
  ".png",
  ".jpg",
  ".jpeg",
  ".txt",
  ".csv",
  ".doc",
  ".docx",
  ".xls",
  ".xlsx",
  ".zip",
];


function formatFileSize(
  bytes: number
) {
  if (bytes < 1024) {
    return `${bytes} B`;
  }

  if (bytes < 1024 * 1024) {
    return `${(bytes / 1024).toFixed(1)} KB`;
  }

  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}


function isAllowedFile(
  file: File
) {
  const extension =
    `.${file.name.split(".").pop()?.toLowerCase() ?? ""}`;

  return ALLOWED_EXTENSIONS.includes(
    extension
  );
}


export default function CreateEvidence() {
  const navigate = useNavigate();

  const createMutation =
    useCreateEvidence();

  const {
    data: controls,
  } = useControls();

  const {
    user,
  } = useAuth();

  const fileInputRef =
    useRef<HTMLInputElement | null>(null);

  const [
    controlId,
    setControlId,
  ] = useState<number>(0);

  const [
    title,
    setTitle,
  ] = useState("");

  const [
    description,
    setDescription,
  ] = useState("");

  const [
    selectedFile,
    setSelectedFile,
  ] = useState<File | null>(null);


  const handleFileChange = (
    e: React.ChangeEvent<HTMLInputElement>
  ) => {
    const file =
      e.target.files?.[0] ?? null;

    if (!file) {
      setSelectedFile(null);
      return;
    }

    if (!isAllowedFile(file)) {
      alert(
        "This file type is not allowed."
      );

      e.target.value = "";
      setSelectedFile(null);

      return;
    }

    if (
      file.size >
      MAX_FILE_SIZE
    ) {
      alert(
        "The selected file is larger than the 10 MB upload limit."
      );

      e.target.value = "";
      setSelectedFile(null);

      return;
    }

    setSelectedFile(file);
  };


  const clearSelectedFile = () => {
    setSelectedFile(null);

    if (fileInputRef.current) {
      fileInputRef.current.value = "";
    }
  };


  const handleSubmit = async (
    e: React.FormEvent
  ) => {
    e.preventDefault();

    if (!user) {
      alert(
        "Your session has expired. Please sign in again."
      );

      return;
    }

    if (controlId === 0) {
      alert(
        "Please select a control."
      );

      return;
    }

    if (!title.trim()) {
      alert(
        "Please enter an evidence title."
      );

      return;
    }

    if (!description.trim()) {
      alert(
        "Please enter a description."
      );

      return;
    }

    if (!selectedFile) {
      alert(
        "Please select a file."
      );

      return;
    }

    const formData =
      new FormData();

    formData.append(
      "control_id",
      controlId.toString()
    );

    formData.append(
      "title",
      title.trim()
    );

    formData.append(
      "description",
      description.trim()
    );

    formData.append(
      "uploaded_by",
      user.id.toString()
    );

    formData.append(
      "file",
      selectedFile
    );

    try {
      await createMutation.mutateAsync(
        formData
      );

      navigate("/evidence");
    } catch (error) {
      console.error(
        "Evidence upload failed:",
        error
      );

      alert(
        "Failed to upload evidence. Please try again."
      );
    }
  };


  return (
    <AppLayout>

      <div className="mx-auto max-w-3xl">

        {/* ==================================================
            Header
        ================================================== */}

        <div className="mb-8">

          <div className="flex items-center gap-3">

            <div className="rounded-xl bg-blue-50 p-3">
              <FileUp className="h-7 w-7 text-blue-600" />
            </div>

            <div>

              <h1 className="text-3xl font-bold text-slate-900">
                Upload Evidence
              </h1>

              <p className="mt-1 text-slate-500">
                Upload cybersecurity evidence to support a control.
              </p>

            </div>

          </div>

        </div>


        {/* ==================================================
            Form
        ================================================== */}

        <form
          onSubmit={handleSubmit}
          className="space-y-6 rounded-2xl border border-slate-200 bg-white p-8 shadow-sm"
        >

          {/* ==================================================
              Control
          ================================================== */}

          <div>

            <label
              htmlFor="control"
              className="mb-2 block text-sm font-medium text-slate-700"
            >
              Control
            </label>

            <select
              id="control"
              className="w-full rounded-lg border border-slate-300 bg-white p-3 text-slate-900 outline-none transition focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              value={controlId}
              onChange={(e) =>
                setControlId(
                  Number(e.target.value)
                )
              }
            >

              <option value={0}>
                Select Control
              </option>

              {controls?.map(
                (control) => (
                  <option
                    key={control.id}
                    value={control.id}
                  >
                    {control.title}
                  </option>
                )
              )}

            </select>

          </div>


          {/* ==================================================
              Evidence Title
          ================================================== */}

          <div>

            <label
              htmlFor="evidence-title"
              className="mb-2 block text-sm font-medium text-slate-700"
            >
              Evidence Title
            </label>

            <input
              id="evidence-title"
              type="text"
              className="w-full rounded-lg border border-slate-300 p-3 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              placeholder="e.g. Event Driven Notification Control Evidence"
              value={title}
              onChange={(e) =>
                setTitle(e.target.value)
              }
            />

          </div>


          {/* ==================================================
              Description
          ================================================== */}

          <div>

            <label
              htmlFor="description"
              className="mb-2 block text-sm font-medium text-slate-700"
            >
              Description
            </label>

            <textarea
              id="description"
              rows={5}
              className="w-full resize-y rounded-lg border border-slate-300 p-3 text-slate-900 outline-none transition placeholder:text-slate-400 focus:border-blue-500 focus:ring-2 focus:ring-blue-100"
              placeholder="Describe how this evidence supports the selected control."
              value={description}
              onChange={(e) =>
                setDescription(
                  e.target.value
                )
              }
            />

          </div>


          {/* ==================================================
              File Upload
          ================================================== */}

          <div>

            <label className="mb-2 block text-sm font-medium text-slate-700">
              Evidence File
            </label>

            <input
              ref={fileInputRef}
              type="file"
              className="sr-only"
              onChange={handleFileChange}
              accept=".pdf,.png,.jpg,.jpeg,.txt,.csv,.doc,.docx,.xls,.xlsx,.zip"
            />

            {!selectedFile ? (

              <button
                type="button"
                onClick={() =>
                  fileInputRef.current?.click()
                }
                className="group flex w-full items-center justify-center rounded-xl border-2 border-dashed border-slate-300 bg-slate-50 px-6 py-8 text-center transition hover:border-blue-400 hover:bg-blue-50"
              >

                <div className="flex flex-col items-center">

                  <div className="mb-3 rounded-xl bg-white p-3 shadow-sm">
                    <Upload className="h-6 w-6 text-blue-600" />
                  </div>

                  <span className="text-sm font-semibold text-slate-700 group-hover:text-blue-700">
                    Choose a file
                  </span>

                  <span className="mt-1 text-xs text-slate-500">
                    PDF, Word, Excel, images, TXT, CSV or ZIP
                  </span>

                  <span className="mt-1 text-xs text-slate-400">
                    Maximum size: 10 MB
                  </span>

                </div>

              </button>

            ) : (

              <div className="rounded-xl border border-blue-200 bg-blue-50 p-4">

                <div className="flex items-center justify-between gap-4">

                  <div className="flex min-w-0 items-center gap-3">

                    <div className="shrink-0 rounded-lg bg-white p-2 shadow-sm">
                      <FileUp className="h-5 w-5 text-blue-600" />
                    </div>

                    <div className="min-w-0">

                      <p className="truncate text-sm font-medium text-slate-800">
                        {selectedFile.name}
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        {formatFileSize(
                          selectedFile.size
                        )}
                      </p>

                    </div>

                  </div>

                  <button
                    type="button"
                    onClick={clearSelectedFile}
                    className="shrink-0 rounded-lg p-2 text-slate-500 transition hover:bg-white hover:text-red-600"
                    aria-label="Remove selected file"
                  >
                    <X className="h-5 w-5" />
                  </button>

                </div>

              </div>

            )}

          </div>


          {/* ==================================================
              Actions
          ================================================== */}

          <div className="flex justify-end gap-3 border-t border-slate-100 pt-6">

            <button
              type="button"
              onClick={() =>
                navigate("/evidence")
              }
              disabled={
                createMutation.isPending
              }
              className="rounded-lg border border-slate-300 bg-white px-5 py-3 text-sm font-medium text-slate-700 transition hover:bg-slate-50 disabled:opacity-50"
            >
              Cancel
            </button>

            <button
              type="submit"
              disabled={
                createMutation.isPending ||
                !selectedFile
              }
              className="inline-flex items-center rounded-lg bg-blue-600 px-6 py-3 text-sm font-medium text-white shadow-sm transition hover:bg-blue-700 disabled:cursor-not-allowed disabled:opacity-50"
            >

              {createMutation.isPending ? (

                <>
                  <Upload className="mr-2 h-4 w-4 animate-pulse" />
                  Uploading...
                </>

              ) : (

                <>
                  <Upload className="mr-2 h-4 w-4" />
                  Upload Evidence
                </>

              )}

            </button>

          </div>

        </form>

      </div>

    </AppLayout>
  );
}