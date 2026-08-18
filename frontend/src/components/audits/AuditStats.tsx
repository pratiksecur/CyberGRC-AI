interface Props {
  totalAudits: number;
  planned: number;
  inProgress: number;
  completed: number;
}

export default function AuditStats({
  totalAudits,
  planned,
  inProgress,
  completed,
}: Props) {
  const cards = [
    {
      title: "Total Audits",
      value: totalAudits,
    },
    {
      title: "Planned",
      value: planned,
    },
    {
      title: "In Progress",
      value: inProgress,
    },
    {
      title: "Completed",
      value: completed,
    },
  ];

  return (
    <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-4">

      {cards.map((card) => (

        <div
          key={card.title}
          className="rounded-2xl border bg-white p-6"
        >
          <p className="text-sm text-slate-500">
            {card.title}
          </p>

          <h2 className="mt-2 text-3xl font-bold">
            {card.value}
          </h2>

        </div>

      ))}

    </div>
  );
}