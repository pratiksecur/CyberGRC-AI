import { BookOpen, Calendar } from "lucide-react";

interface Framework {
  id: number;
  name: string;
  version: string;
  created_at: string;
}

interface Props {
  frameworks: Framework[];
}

export default function RecentFrameworks({
  frameworks,
}: Props) {
  const recent = [...frameworks].slice(0, 5);

  return (
    <div className="rounded-2xl border bg-white">

      <div className="border-b p-5">

        <h2 className="text-lg font-semibold">
          Recent Frameworks
        </h2>

        <p className="text-sm text-slate-500">
          Latest compliance frameworks
        </p>

      </div>

      <div className="divide-y">

        {recent.length === 0 ? (

          <div className="p-6 text-center text-slate-500">
            No frameworks found.
          </div>

        ) : (

          recent.map((framework) => (

            <div
              key={framework.id}
              className="flex items-center justify-between p-5"
            >

              <div className="flex items-center gap-4">

                <div className="rounded-xl bg-blue-50 p-3">

                  <BookOpen className="h-5 w-5 text-blue-600" />

                </div>

                <div>

                  <h3 className="font-medium">
                    {framework.name}
                  </h3>

                  <p className="text-sm text-slate-500">
                    Version {framework.version}
                  </p>

                </div>

              </div>

              <div className="flex items-center gap-1 text-xs text-slate-400">

                <Calendar className="h-3 w-3" />

                {new Date(
                  framework.created_at
                ).toLocaleDateString()}

              </div>

            </div>

          ))

        )}

      </div>

    </div>
  );
}