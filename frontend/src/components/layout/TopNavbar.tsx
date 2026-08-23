import {
  Bell,
  Check,
  Moon,
  Search,
  ShieldAlert,
  ClipboardCheck,
  Clock,
  CheckCircle2,
  AlertTriangle,
  X,
} from "lucide-react";

import { useState } from "react";

import {
  Avatar,
  AvatarFallback,
} from "@/components/ui/avatar";

import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useNotifications } from "@/hooks/useNotifications";


function getNotificationIcon(type: string) {

  if (
    type === "critical_risk" ||
    type === "critical_finding" ||
    type === "action_overdue" ||
    type === "critical_action"
  ) {
    return (
      <div className="rounded-lg bg-red-50 p-2">
        <ShieldAlert className="h-4 w-4 text-red-600" />
      </div>
    );
  }

  if (type === "action_due_soon") {
    return (
      <div className="rounded-lg bg-orange-50 p-2">
        <Clock className="h-4 w-4 text-orange-600" />
      </div>
    );
  }

  if (type === "action_completed") {
    return (
      <div className="rounded-lg bg-green-50 p-2">
        <CheckCircle2 className="h-4 w-4 text-green-600" />
      </div>
    );
  }

  if (type === "audit_created") {
    return (
      <div className="rounded-lg bg-blue-50 p-2">
        <ClipboardCheck className="h-4 w-4 text-blue-600" />
      </div>
    );
  }

  return (
    <div className="rounded-lg bg-slate-100 p-2">
      <AlertTriangle className="h-4 w-4 text-slate-600" />
    </div>
  );
}


function formatNotificationTime(
  value: string
): string {

  const date = new Date(value);

  const now = new Date();

  const diff =
    Math.floor(
      (now.getTime() - date.getTime())
      / 1000
    );

  if (diff < 60) {
    return "Just now";
  }

  if (diff < 3600) {
    return `${Math.floor(diff / 60)}m ago`;
  }

  if (diff < 86400) {
    return `${Math.floor(diff / 3600)}h ago`;
  }

  if (diff < 604800) {
    return `${Math.floor(diff / 86400)}d ago`;
  }

  return date.toLocaleDateString();
}


export default function TopNavbar() {

  const {
    data: user,
    isLoading,
  } = useCurrentUser();

  const {
    notifications,
    unreadCount,
    markAsRead,
    markAllAsRead,
  } = useNotifications();

  const [
    notificationsOpen,
    setNotificationsOpen,
  ] = useState(false);


  const initials = user
    ? user.full_name
        .split(" ")
        .map(
          (name) => name[0]
        )
        .join("")
        .toUpperCase()
    : "--";


  return (

    <header className="relative flex h-16 items-center justify-between border-b bg-white px-6">

      {/* Left */}

      <div className="flex items-center gap-3">

        <Search className="h-5 w-5 text-gray-400" />

        <span className="text-gray-400">
          Search...
        </span>

      </div>


      {/* Right */}

      <div className="flex items-center gap-5">

        {/* Theme */}

        <button
          type="button"
          className="rounded-lg p-2 transition hover:bg-gray-100"
        >
          <Moon size={20} />
        </button>


        {/* Notifications */}

        <div className="relative">

          <button
            type="button"
            onClick={() =>
              setNotificationsOpen(
                (value) => !value
              )
            }
            className="relative rounded-lg p-2 transition hover:bg-gray-100"
            aria-label="Notifications"
          >

            <Bell size={20} />

            {unreadCount > 0 && (

              <span className="absolute -right-1 -top-1 flex min-h-5 min-w-5 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] font-semibold text-white">

                {unreadCount > 99
                  ? "99+"
                  : unreadCount}

              </span>

            )}

          </button>


          {notificationsOpen && (

            <>

              {/* Backdrop */}

              <button
                type="button"
                aria-label="Close notifications"
                className="fixed inset-0 z-40 cursor-default"
                onClick={() =>
                  setNotificationsOpen(false)
                }
              />


              {/* Dropdown */}

              <div className="absolute right-0 z-50 mt-3 w-[380px] overflow-hidden rounded-2xl border bg-white shadow-xl">

                {/* Header */}

                <div className="flex items-center justify-between border-b px-4 py-3">

                  <div>

                    <h3 className="font-semibold text-slate-900">
                      Notifications
                    </h3>

                    <p className="text-xs text-slate-500">
                      {unreadCount} unread
                    </p>

                  </div>


                  <div className="flex items-center gap-1">

                    {unreadCount > 0 && (

                      <button
                        type="button"
                        onClick={() =>
                          markAllAsRead()
                        }
                        className="rounded-lg px-2 py-1 text-xs font-medium text-blue-600 transition hover:bg-blue-50"
                      >
                        Mark all as read
                      </button>

                    )}

                    <button
                      type="button"
                      onClick={() =>
                        setNotificationsOpen(false)
                      }
                      className="rounded-lg p-1.5 text-slate-400 transition hover:bg-slate-100 hover:text-slate-700"
                    >
                      <X className="h-4 w-4" />
                    </button>

                  </div>

                </div>


                {/* Notifications */}

                <div className="max-h-[420px] overflow-y-auto">

                  {notifications.length === 0 ? (

                    <div className="px-6 py-10 text-center">

                      <div className="mx-auto mb-3 flex h-10 w-10 items-center justify-center rounded-full bg-slate-100">

                        <Bell className="h-5 w-5 text-slate-400" />

                      </div>

                      <p className="font-medium text-slate-700">
                        No notifications
                      </p>

                      <p className="mt-1 text-xs text-slate-500">
                        You're all caught up.
                      </p>

                    </div>

                  ) : (

                    notifications.map(
                      (notification) => (

                        <div
                          key={notification.id}
                          className={`flex gap-3 border-b px-4 py-3 transition hover:bg-slate-50 ${
                            notification.is_read
                              ? "bg-white"
                              : "bg-blue-50/40"
                          }`}
                        >

                          {getNotificationIcon(
                            notification.type
                          )}


                          <div className="min-w-0 flex-1">

                            <div className="flex items-start justify-between gap-2">

                              <p
                                className={`text-sm ${
                                  notification.is_read
                                    ? "font-medium text-slate-700"
                                    : "font-semibold text-slate-900"
                                }`}
                              >
                                {notification.title}
                              </p>

                              {!notification.is_read && (

                                <span className="mt-1 h-2 w-2 shrink-0 rounded-full bg-blue-600" />

                              )}

                            </div>


                            <p className="mt-1 text-xs leading-5 text-slate-500">

                              {notification.message}

                            </p>


                            <div className="mt-2 flex items-center justify-between">

                              <span className="text-[11px] text-slate-400">

                                {formatNotificationTime(
                                  notification.created_at
                                )}

                              </span>


                              {!notification.is_read && (

                                <button
                                  type="button"
                                  onClick={() =>
                                    markAsRead(
                                      notification.id
                                    )
                                  }
                                  className="flex items-center gap-1 rounded-md px-2 py-1 text-[11px] font-medium text-blue-600 transition hover:bg-blue-50"
                                >

                                  <Check className="h-3 w-3" />

                                  Mark read

                                </button>

                              )}

                            </div>

                          </div>

                        </div>

                      )
                    )

                  )}

                </div>

              </div>

            </>

          )}

        </div>


        {/* User */}

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