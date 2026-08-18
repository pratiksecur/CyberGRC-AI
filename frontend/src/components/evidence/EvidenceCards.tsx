import { FileArchive } from "lucide-react";

interface Evidence {
  id: number;
  title: string;
  file_name: string;
}

interface Props {
  evidence: Evidence[];
}

export default function EvidenceCards({
  evidence,
}: Props) {
  return (
    <div className="rounded-2xl border bg-white">

      <div className="border-b p-5">

        <h2 className="text-lg font-semibold">
          Evidence Library
        </h2>

      </div>

      <div className="divide-y">

        {evidence.map((item) => (
          <div
            key={item.id}
            className="flex items-center gap-4 p-5"
          >

            <div className="rounded-xl bg-blue-100 p-3">

              <FileArchive className="h-5 w-5 text-blue-600" />

            </div>

            <div>

              <h3 className="font-medium">
                {item.title}
              </h3>

              <p className="text-sm text-slate-500">
                {item.file_name}
              </p>

            </div>

          </div>
        ))}

      </div>

    </div>
  );
}