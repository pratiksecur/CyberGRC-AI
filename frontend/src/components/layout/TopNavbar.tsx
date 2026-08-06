import { Bell, Moon, Search } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

import { useCurrentUser } from "@/hooks/useCurrentUser";

export default function TopNavbar() {

  const { data: user, isLoading } = useCurrentUser();

  const initials = user
    ? user.full_name
        .split(" ")
        .map((name) => name[0])
        .join("")
        .toUpperCase()
    : "--";

  return (
    <header className="flex h-16 items-center justify-between border-b bg-white px-6">

      {/* Left */}

      <div className="flex items-center gap-3">

        <Search className="h-5 w-5 text-gray-400" />

        <span className="text-gray-400">
          Search...
        </span>

      </div>

      {/* Right */}

      <div className="flex items-center gap-5">

        <button className="rounded-lg p-2 transition hover:bg-gray-100">

          <Moon size={20} />

        </button>

        <button className="rounded-lg p-2 transition hover:bg-gray-100">

          <Bell size={20} />

        </button>

        <div className="flex items-center gap-3">

          <Avatar>

            <AvatarFallback>

              {initials}

            </AvatarFallback>

          </Avatar>

          <div className="hidden text-right md:block">

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

        </div>

      </div>

    </header>
  );
}