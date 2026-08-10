interface Props {
  status: string;
}

export default function RiskStatusBadge({
  status,
}: Props) {

  let bg = "";
  let text = "";

  switch (status.toLowerCase()) {

    case "open":
      bg = "bg-blue-100";
      text = "text-blue-700";
      break;

    case "in progress":
      bg = "bg-yellow-100";
      text = "text-yellow-700";
      break;

    case "mitigated":
      bg = "bg-green-100";
      text = "text-green-700";
      break;

    case "closed":
      bg = "bg-slate-200";
      text = "text-slate-700";
      break;

    default:
      bg = "bg-slate-100";
      text = "text-slate-700";
  }

  return (
    <span
      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${bg} ${text}`}
    >
      {status}
    </span>
  );
}