import {
  ShieldCheck,
  Calendar,
} from "lucide-react";

interface Control {
  id: number;
  title: string;
  control_type: string;
  status: string;
  created_at?: string;
}

interface Props {
  controls: Control[];
}

export default function RecentControls({
  controls,
}: Props) {

  const recent = [...controls].slice(0, 5);

  return (
    <div className="rounded-2xl border bg-white">

      <div className="border-b p-5">

        <h2 className="text-lg font-semibold">
          Recent Controls
        </h2>

        <p className="text-sm text-slate-500">
          Latest cybersecurity controls
        </p>

      </div>

      <div className="divide-y">

        {recent.length === 0 ? (

          <div className="p-6 text-center text-slate-500">
            No controls found.
          </div>

        ) : (

          recent.map((control) => (

            <div
              key={control.id}
              className="flex items-center justify-between p-5"
            >

              <div className="flex items-center gap-4">

                <div className="rounded-xl bg-blue-50 p-3">

                  <ShieldCheck className="h-5 w-5 text-blue-600" />

                </div>

                <div>

                  <h3 className="font-medium">
                    {control.title}
                  </h3>

                  <p className="text-sm text-slate-500">
                    {control.control_type}
                  </p>

                </div>

              </div>

              <div className="text-right">

                <span
                  className={`rounded-full px-3 py-1 text-xs font-medium ${
                    control.status === "Active"
                      ? "bg-green-100 text-green-700"
                      : "bg-red-100 text-red-700"
                  }`}
                >
                  {control.status}
                </span>

                {control.created_at && (

                  <div className="mt-2 flex items-center justify-end gap-1 text-xs text-slate-400">

                    <Calendar className="h-3 w-3" />

                    {new Date(
                      control.created_at
                    ).toLocaleDateString()}

                  </div>

                )}

              </div>

            </div>

          ))

        )}

      </div>

    </div>
  );
}