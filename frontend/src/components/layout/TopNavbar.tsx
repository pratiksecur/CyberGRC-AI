import { Bell, Moon, Search } from "lucide-react";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export default function TopNavbar() {
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

        <button className="rounded-lg p-2 hover:bg-gray-100 transition">
          <Moon size={20} />
        </button>

        <button className="rounded-lg p-2 hover:bg-gray-100 transition">
          <Bell size={20} />
        </button>

        <Avatar>

          <AvatarFallback>
            PG
          </AvatarFallback>

        </Avatar>

      </div>

    </header>
  );
}