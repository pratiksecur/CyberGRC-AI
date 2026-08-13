import { Award } from "lucide-react";

interface Control {
  id: number;
  control_type: string;
}

interface Props {
  controls: Control[];
}

export default function HighestFramework({
  controls,
}: Props) {

  const typeCounts = controls.reduce(
    (acc, control) => {

      acc[control.control_type] =
        (acc[control.control_type] || 0) + 1;

      return acc;

    },
    {} as Record<string, number>
  );

  const types = Object.entries(typeCounts);

  const highest =
    types.length > 0
      ? types.sort((a, b) => b[1] - a[1])[0]
      : null;

  const percentage =
    highest && controls.length > 0
      ? Math.round(
          (highest[1] / controls.length) * 100
        )
      : 0;

  return (
    <div className="rounded-2xl border bg-white">

      <div className="border-b p-5">

        <h2 className="text-lg font-semibold">
          Most Common Control Type
        </h2>

        <p className="text-sm text-slate-500">
          Distribution by control type
        </p>

      </div>

      <div className="flex flex-col items-center justify-center p-10">

        <div className="mb-5 rounded-full bg-amber-100 p-5">

          <Award className="h-10 w-10 text-amber-600" />

        </div>

        {highest ? (
          <>

            <h3 className="text-2xl font-bold">
              {highest[0]}
            </h3>

            <p className="mt-2 text-slate-500">
              {highest[1]} Controls
            </p>

            <div className="mt-6 h-3 w-full rounded-full bg-slate-200">

              <div
                className="h-3 rounded-full bg-amber-500 transition-all"
                style={{
                  width: `${percentage}%`,
                }}
              />

            </div>

            <p className="mt-3 font-semibold text-amber-600">
              {percentage}% Coverage
            </p>

          </>
        ) : (

          <p className="text-slate-500">
            No control type data available.
          </p>

        )}

      </div>

    </div>
  );
}