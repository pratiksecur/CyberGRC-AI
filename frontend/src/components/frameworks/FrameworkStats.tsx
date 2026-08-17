import {
  Layers,
  BadgeCheck,
  Clock3,
  FileText,
} from "lucide-react";

interface Props {
  totalFrameworks: number;
  latestVersion: number;
  oldVersions: number;
  totalDocuments: number;
}

export default function FrameworkStats({
  totalFrameworks,
  latestVersion,
  oldVersions,
  totalDocuments,
}: Props) {
  const cards = [
    {
      title: "Total Frameworks",
      value: totalFrameworks,
      icon: Layers,
      color: "bg-blue-100 text-blue-600",
    },
    {
      title: "Latest Versions",
      value: latestVersion,
      icon: BadgeCheck,
      color: "bg-green-100 text-green-600",
    },
    {
      title: "Older Versions",
      value: oldVersions,
      icon: Clock3,
      color: "bg-amber-100 text-amber-600",
    },
    {
      title: "Documents",
      value: totalDocuments,
      icon: FileText,
      color: "bg-purple-100 text-purple-600",
    },
  ];

  return (
    <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
      {cards.map((card) => {
        const Icon = card.icon;

        return (
          <div
            key={card.title}
            className="rounded-2xl border bg-white p-6"
          >
            <div className="flex items-center justify-between">

              <div>

                <p className="text-sm text-slate-500">
                  {card.title}
                </p>

                <h2 className="mt-2 text-3xl font-bold">
                  {card.value}
                </h2>

              </div>

              <div
                className={`rounded-xl p-3 ${card.color}`}
              >
                <Icon className="h-6 w-6" />
              </div>

            </div>
          </div>
        );
      })}
    </div>
  );
}