import AppLayout from "@/layouts/AppLayout";

import AIGRCAnalyst from "@/components/ai/AIGRCAnalyst";


export default function AIGRCAnalystPage() {
  return (
    <AppLayout>
      <div className="mx-auto max-w-7xl space-y-6 p-6">
        <div>
          <h1 className="text-2xl font-bold text-slate-900">
            AI GRC Analyst
          </h1>

          <p className="mt-1 text-sm text-slate-500">
            Governed AI analysis across enterprise
            risk, controls, evidence, findings and
            regulatory posture.
          </p>
        </div>

        <AIGRCAnalyst />
      </div>
    </AppLayout>
  );
}