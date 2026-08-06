import { NavLink } from "react-router-dom";
import { Shield } from "lucide-react";

import { navigation } from "@/config/navigation";

export default function AppSidebar() {
  return (
    <aside className="flex h-screen w-64 flex-col border-r border-slate-200 bg-white">

      {/* Logo */}

      <div className="border-b border-slate-200 p-6">

        <div className="flex items-center gap-3">

          <div className="flex h-11 w-11 items-center justify-center rounded-xl bg-blue-600 text-white shadow-sm">
            <Shield size={22} />
          </div>

          <div>
            <h1 className="text-xl font-bold text-slate-900">
              CyberGRC AI
            </h1>

            <p className="text-xs text-slate-500">
              Enterprise GRC Platform
            </p>
          </div>

        </div>

      </div>

      {/* Navigation */}

      <nav className="flex-1 space-y-1 p-4">

        {navigation.map((item) => {

          const Icon = item.icon;

          return (

            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `
                flex items-center gap-3 rounded-xl px-4 py-3
                transition-all duration-200

                ${
                  isActive
                    ? "bg-blue-600 text-white shadow-md"
                    : "text-slate-600 hover:bg-slate-100 hover:text-slate-900"
                }
                `
              }
            >
              <Icon size={20} />

              <span className="font-medium">
                {item.label}
              </span>

            </NavLink>

          );
        })}

      </nav>

      {/* Footer */}

      <div className="border-t border-slate-200 p-5">

        <div className="flex items-center gap-3">

          <div className="flex h-11 w-11 items-center justify-center rounded-full bg-blue-600 text-white font-semibold">
            PG
          </div>

          <div>

            <p className="font-semibold text-slate-900">
              Pratik Gupta
            </p>

            <p className="text-sm text-slate-500">
              GRC Administrator
            </p>

          </div>

        </div>

      </div>

    </aside>
  );
}