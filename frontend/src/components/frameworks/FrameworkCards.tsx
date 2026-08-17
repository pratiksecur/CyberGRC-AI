import { Layers3 } from "lucide-react";

interface Framework {
  id: number;
  name: string;
  version: string;
}

interface Props {
  frameworks: Framework[];
}

export default function FrameworkCards({
  frameworks,
}: Props) {

  return (
    <div className="rounded-2xl border bg-white">

      <div className="border-b p-5">

        <h2 className="text-lg font-semibold">
          Framework Library
        </h2>

        <p className="text-sm text-slate-500">
          Available compliance frameworks
        </p>

      </div>

      <div className="divide-y">

        {frameworks.length === 0 ? (

          <div className="p-6 text-center text-slate-500">
            No frameworks available.
          </div>

        ) : (

          frameworks.map((framework) => (

            <div
              key={framework.id}
              className="flex items-center gap-4 p-5"
            >

              <div className="rounded-xl bg-indigo-100 p-3">

                <Layers3 className="h-5 w-5 text-indigo-600" />

              </div>

              <div>

                <h3 className="font-semibold">
                  {framework.name}
                </h3>

                <p className="text-sm text-slate-500">
                  Version {framework.version}
                </p>

              </div>

            </div>

          ))

        )}

      </div>

    </div>
  );
}