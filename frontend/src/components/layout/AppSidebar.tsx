import { NavLink } from "react-router-dom";
import { Shield } from "lucide-react";

import { navigation } from "@/config/navigation";
import { hasPermission } from "@/auth/permissions";

import { useAuth } from "@/contexts/AuthContext";

export default function AppSidebar() {
  const { user } = useAuth();

  const visibleNavigation =
    navigation.filter((item) => {
      if (
        !item.resource ||
        !item.action
      ) {
        return true;
      }

      return hasPermission(
        user?.role,
        item.resource,
        item.action
      );
    });

  const initials =
    user?.full_name
      ?.split(" ")
      .filter(Boolean)
      .map(
        (name) => name[0]
      )
      .join("")
      .slice(0, 2)
      .toUpperCase() || "U";

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

      <nav className="flex-1 space-y-1 overflow-y-auto p-4">

        {visibleNavigation.map(
          (item) => {
            const Icon =
              item.icon;

            return (
              <NavLink
                key={item.path}
                to={item.path}
                className={({
                  isActive,
                }) =>
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
          }
        )}

      </nav>

      {/* Footer */}

      <div className="border-t border-slate-200 p-5">

        <div className="flex items-center gap-3">

          <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-full bg-blue-600 text-white font-semibold">
            {initials}
          </div>

          <div className="min-w-0">

            <p className="truncate font-semibold text-slate-900">
              {user?.full_name ||
                "User"}
            </p>

            <p className="truncate text-sm text-slate-500">
              {user?.role ||
                "User"}
            </p>

          </div>

        </div>

      </div>

    </aside>
  );
}