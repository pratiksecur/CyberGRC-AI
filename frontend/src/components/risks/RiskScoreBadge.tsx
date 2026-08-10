interface Props {
  score: number;
}

export default function RiskScoreBadge({ score }: Props) {
  let bg = "";
  let text = "";
  let label = "";

  if (score <= 5) {
    bg = "bg-green-100";
    text = "text-green-700";
    label = "Low";
  } else if (score <= 10) {
    bg = "bg-yellow-100";
    text = "text-yellow-700";
    label = "Medium";
  } else if (score <= 15) {
    bg = "bg-orange-100";
    text = "text-orange-700";
    label = "High";
  } else {
    bg = "bg-red-100";
    text = "text-red-700";
    label = "Critical";
  }

  return (
    <div className="flex flex-col gap-1">

      <span
        className={`inline-flex w-fit rounded-full px-3 py-1 text-xs font-semibold ${bg} ${text}`}
      >
        {label}
      </span>

      <span className="font-semibold text-slate-800">
        {score}
      </span>

    </div>
  );
}