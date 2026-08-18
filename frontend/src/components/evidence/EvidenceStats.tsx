import {
  FileText,
  CheckCircle,
  Clock,
  HardDrive,
} from "lucide-react";

interface Props {
  totalEvidence: number;
  approvedEvidence: number;
  pendingEvidence: number;
  totalFiles: number;
}

export default function EvidenceStats({
  totalEvidence,
  approvedEvidence,
  pendingEvidence,
  totalFiles,
}: Props) {
  const stats = [
    {
      title: "Total Evidence",
      value: totalEvidence,
      icon: FileText,
      color: "text-blue-600",
      bg: "bg-blue-100",
    },
    {
      title: "Approved",
      value: approvedEvidence,
      icon: CheckCircle,
      color: "text-green-600",
      bg: "bg-green-100",
    },
    {
      title: "Pending",
      value: pendingEvidence,
      icon: Clock,
      color: "text-yellow-600",
      bg: "bg-yellow-100",
    },
    {
      title: "Files",
      value: totalFiles,
      icon: HardDrive,
      color: "text-purple-600",
      bg: "bg-purple-100",
    },
  ];

  return (
    <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
      {stats.map((stat) => (
        <div
          key={stat.title}
          className="rounded-2xl border bg-white p-6"
        >
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-slate-500">
                {stat.title}
              </p>

              <h2 className="mt-2 text-3xl font-bold">
                {stat.value}
              </h2>
            </div>

            <div className={`${stat.bg} rounded-xl p-3`}>
              <stat.icon
                className={`h-6 w-6 ${stat.color}`}
              />
            </div>
          </div>
        </div>
      ))}
    </div>
  );
}