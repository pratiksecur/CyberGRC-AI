import { type LucideIcon } from "lucide-react";
import { motion } from "framer-motion";

interface StatCardProps {
  title: string;
  value: number | string;
  subtitle: string;
  icon: LucideIcon;
  iconColor?: string;

  trend?: string;
  trendPositive?: boolean;
}

export default function StatCard({
  title,
  value,
  subtitle,
  icon: Icon,
  iconColor = "bg-blue-600",

  trend,
  trendPositive = true,
}: StatCardProps) {
  return (
    <motion.div
      whileHover={{
        y: -4,
        scale: 1.02,
      }}
      transition={{
        duration: 0.2,
      }}
      className="rounded-2xl border border-slate-200 bg-white p-6 shadow-sm"
    >
      <div className="flex items-center justify-between">

        <div>

          <p className="text-sm text-slate-500">
            {title}
          </p>

          <h2 className="mt-2 text-4xl font-bold text-slate-900">
            {value}
          </h2>

          <div className="mt-3">

            <p className="text-sm text-slate-500">
              {subtitle}
            </p>

            {trend && (

              <span
                className={`mt-2 inline-flex rounded-full px-2 py-1 text-xs font-medium ${
                  trendPositive
                    ? "bg-green-100 text-green-700"
                    : "bg-red-100 text-red-700"
                }`}
              >
                {trend}
              </span>

            )}

          </div>

        </div>

        <div
          className={`flex h-14 w-14 items-center justify-center rounded-2xl text-white ${iconColor}`}
        >
          <Icon size={28} />
        </div>

      </div>
    </motion.div>
  );
}