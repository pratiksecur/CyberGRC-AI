interface Props {
  status: string;
}

export default function RiskStatusBadge({
  status,
}: Props) {

  const statusStyles: Record<
    string,
    { bg: string; text: string }
  > = {
    open: {
      bg: "bg-blue-100",
      text: "text-blue-700",
    },
    "in progress": {
      bg: "bg-yellow-100",
      text: "text-yellow-700",
    },
    mitigated: {
      bg: "bg-green-100",
      text: "text-green-700",
    },
    closed: {
      bg: "bg-slate-200",
      text: "text-slate-700",
    },
  };

  const { bg, text } =
    statusStyles[status.toLowerCase()] ?? {
      bg: "bg-slate-100",
      text: "text-slate-700",
    };

  return (
    <span
      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${bg} ${text}`}
    >
      {status}
    </span>
  );
}