import type { ReactNode } from "react";

interface DashboardCardProps {
  title: string;
  subtitle?: string;
  icon?: ReactNode;
  children: ReactNode;
}

export default function DashboardCard({
  title,
  subtitle,
  icon,
  children,
}: DashboardCardProps) {
  return (
    <div className="rounded-2xl border border-slate-200 bg-white shadow-sm transition-all duration-300 hover:shadow-lg">

      {/* Header */}

      <div className="flex items-center justify-between border-b border-slate-200 p-6">

        <div className="flex items-center gap-3">

          {icon && (
            <div className="rounded-xl bg-slate-100 p-3">
              {icon}
            </div>
          )}

          <div>

            <h2 className="text-xl font-bold text-slate-900">
              {title}
            </h2>

            {subtitle && (
              <p className="text-sm text-slate-500">
                {subtitle}
              </p>
            )}

          </div>

        </div>

      </div>

      {/* Content */}

      <div className="p-6">

        {children}

      </div>

    </div>
  );
}