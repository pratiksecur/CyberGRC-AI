import {
  ShieldCheck,
  ShieldAlert,
  FolderKanban,
  BadgeCheck,
} from "lucide-react";

interface Props {
  totalControls: number;
  activeControls: number;
  inactiveControls: number;
  frameworks: number;
}

export default function ControlStats({
  totalControls,
  activeControls,
  inactiveControls,
  frameworks,
}: Props) {
  const stats = [
    {
      title: "Total Controls",
      value: totalControls,
      subtitle: "All controls",
      icon: ShieldCheck,
      color: "bg-blue-600",
    },
    {
      title: "Active Controls",
      value: activeControls,
      subtitle: "Currently active",
      icon: BadgeCheck,
      color: "bg-emerald-500",
    },
    {
      title: "Inactive Controls",
      value: inactiveControls,
      subtitle: "Need attention",
      icon: ShieldAlert,
      color: "bg-red-500",
    },
    {
      title: "Framework Coverage",
      value: frameworks,
      subtitle: "Frameworks used",
      icon: FolderKanban,
      color: "bg-amber-500",
    },
  ];

  return (
    <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">
      {stats.map((stat) => {
        const Icon = stat.icon;

        return (
          <div
            key={stat.title}
            className="rounded-2xl border bg-white p-5 shadow-sm"
          >
            <div className="flex items-start justify-between">
              <div>
                <p className="text-sm text-slate-500">{stat.title}</p>

                <h2 className="mt-2 text-3xl font-bold">
                  {stat.value}
                </h2>

                <p className="mt-2 text-xs text-slate-400">
                  {stat.subtitle}
                </p>
              </div>

              <div
                className={`rounded-xl p-3 text-white ${stat.color}`}
              >
                <Icon size={22} />
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}