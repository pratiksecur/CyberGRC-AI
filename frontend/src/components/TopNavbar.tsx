import {
  Bell,
  Moon,
  Search,
  User,
  Settings,
  LogOut,
  ChevronDown,
} from "lucide-react";

import { Avatar, AvatarFallback } from "@/components/ui/avatar";

import {
  DropdownMenu,
  DropdownMenuTrigger,
  DropdownMenuContent,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuItem,
} from "@/components/ui/dropdown-menu";

import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useAuth } from "@/contexts/AuthContext";

export default function TopNavbar() {

  const { data: user, isLoading } = useCurrentUser();

  const { logout } = useAuth();

  const initials = user
    ? user.full_name
        .split(" ")
        .map((name) => name[0])
        .join("")
        .toUpperCase()
    : "--";

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">

      {/* Search */}

      <div className="flex items-center gap-3 rounded-xl border bg-slate-50 px-4 py-2">

        <Search
          size={18}
          className="text-slate-400"
        />

        <input
          type="text"
          placeholder="Search risks, controls, audits..."
          className="w-72 bg-transparent text-sm outline-none placeholder:text-slate-400"
        />

      </div>

      {/* Right */}

      <div className="flex items-center gap-5">

        <button className="rounded-xl p-2 transition hover:bg-slate-100">

          <Moon size={20} />

        </button>

        <button className="relative rounded-xl p-2 transition hover:bg-slate-100">

          <Bell size={20} />

          <span className="absolute right-1 top-1 h-2 w-2 rounded-full bg-red-500"></span>

        </button>

        <DropdownMenu>

          <DropdownMenuTrigger asChild>

            <button className="flex items-center gap-3 rounded-xl px-3 py-2 transition hover:bg-slate-100">

              <Avatar>

                <AvatarFallback>

                  {initials}

                </AvatarFallback>

              </Avatar>

              <div className="hidden text-left md:block">

                {isLoading ? (

                  <>
                    <p className="font-semibold">
                      Loading...
                    </p>

                    <p className="text-sm text-slate-500">
                      Please wait
                    </p>
                  </>

                ) : (

                  <>
                    <p className="font-semibold">

                      {user?.full_name}

                    </p>

                    <p className="text-sm capitalize text-slate-500">

                      {user?.role.replace("_", " ")}

                    </p>
                  </>

                )}

              </div>

              <ChevronDown
                size={18}
                className="text-slate-500"
              />

            </button>

          </DropdownMenuTrigger>

          <DropdownMenuContent
            align="end"
            className="w-56"
          >

            <DropdownMenuLabel>

              My Account

            </DropdownMenuLabel>

            <DropdownMenuSeparator />

            <DropdownMenuItem>

              <User
                size={16}
                className="mr-2"
              />

              Profile

            </DropdownMenuItem>

            <DropdownMenuItem>

              <Settings
                size={16}
                className="mr-2"
              />

              Settings

            </DropdownMenuItem>

            <DropdownMenuSeparator />

            <DropdownMenuItem
              onClick={logout}
              className="text-red-600 focus:text-red-600"
            >

              <LogOut
                size={16}
                className="mr-2"
              />

              Logout

            </DropdownMenuItem>

          </DropdownMenuContent>

        </DropdownMenu>

      </div>

    </header>
  );
}