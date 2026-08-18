import {
  Calendar,
  FileText,
} from "lucide-react";

interface Evidence {
  id: number;
  title: string;
  file_name: string;
  uploaded_at: string;
}

interface Props {
  evidence: Evidence[];
}

export default function RecentEvidence({
  evidence,
}: Props) {
  const recent = [...evidence].slice(0, 5);

  return (
    <div className="rounded-2xl border bg-white">

      <div className="border-b p-5">

        <h2 className="text-lg font-semibold">
          Recent Evidence
        </h2>

      </div>

      <div className="divide-y">

        {recent.map((item) => (
          <div
            key={item.id}
            className="flex items-center justify-between p-5"
          >

            <div className="flex items-center gap-4">

              <div className="rounded-xl bg-blue-100 p-3">

                <FileText className="h-5 w-5 text-blue-600" />

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

            <div className="flex items-center gap-1 text-xs text-slate-400">

              <Calendar className="h-3 w-3" />

              {new Date(
                item.uploaded_at
              ).toLocaleDateString()}

            </div>

          </div>
        ))}

      </div>

    </div>
  );
}