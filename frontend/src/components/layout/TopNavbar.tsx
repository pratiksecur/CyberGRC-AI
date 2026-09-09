import {
  Bell,
  Moon,
  Sun,
  Search,
  CheckCheck,
  ShieldAlert,
  ClipboardCheck,
  FileWarning,
  Wrench,
  BookOpen,
  FileText,
  X,
} from "lucide-react";

import {
  useEffect,
  useRef,
  useState,
} from "react";

import { useNavigate } from "react-router-dom";

import {
  Avatar,
  AvatarFallback,
} from "@/components/ui/avatar";

import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useTheme } from "@/contexts/ThemeContext";

import {
  getNotifications,
  getUnreadNotificationCount,
  markNotificationAsRead,
  markAllNotificationsAsRead,
} from "@/api/notifications";

type Notification = {
  id: number;
  type: string;
  title: string;
  message: string;
  source_type: string;
  source_id: number;
  is_read: boolean;
  created_at: string;
};

type SearchResult = {
  id: number;
  title: string;
  description?: string;
  type:
    | "Risk"
    | "Control"
    | "Audit"
    | "Finding"
    | "Corrective Action"
    | "Framework"
    | "Evidence";
  path: string;
};

const API_BASE_URL =
  "http://localhost:8000/api/v1";

export default function TopNavbar() {
  const navigate = useNavigate();

  const {
    data: user,
    isLoading,
  } = useCurrentUser();

  const {
    theme,
    toggleTheme,
  } = useTheme();

  const [search, setSearch] =
    useState("");

  const [searchResults, setSearchResults] =
    useState<SearchResult[]>([]);

  const [searchLoading, setSearchLoading] =
    useState(false);

  const [searchOpen, setSearchOpen] =
    useState(false);

  const [notifications, setNotifications] =
    useState<Notification[]>([]);

  const [unreadCount, setUnreadCount] =
    useState(0);

  const [notificationsOpen, setNotificationsOpen] =
    useState(false);

  const [notificationsLoading, setNotificationsLoading] =
    useState(false);

  const [notificationsError, setNotificationsError] =
    useState(false);

  const searchInputRef =
    useRef<HTMLInputElement>(null);

  const notificationRef =
    useRef<HTMLDivElement>(null);

  const searchRef =
    useRef<HTMLDivElement>(null);

  const initials = user
    ? user.full_name
        .split(" ")
        .map((name) => name[0])
        .join("")
        .toUpperCase()
    : "--";

  /* ================================================== */
  /* GLOBAL SEARCH */
  /* ================================================== */

  useEffect(() => {
    const query = search
      .trim()
      .toLowerCase();

    if (!query) {
      setSearchResults([]);
      setSearchOpen(false);
      return;
    }

    const runSearch = async () => {
      const token =
        localStorage.getItem(
          "access_token"
        );

      if (!token) {
        return;
      }

      setSearchLoading(true);
      setSearchOpen(true);

      try {
        const headers = {
          Authorization: `Bearer ${token}`,
          "Content-Type":
            "application/json",
        };

        const endpoints = [
          {
            type: "Risk" as const,
            path: "/risks/",
            route: "/risks",
          },
          {
            type: "Control" as const,
            path: "/controls/",
            route: "/controls",
          },
          {
            type: "Audit" as const,
            path: "/audits/",
            route: "/audits",
          },
          {
            type: "Finding" as const,
            path: "/audit-findings/",
            route: "/audit-findings",
          },
          {
            type: "Corrective Action" as const,
            path: "/corrective-actions/",
            route: "/corrective-actions",
          },
          {
            type: "Framework" as const,
            path: "/frameworks/",
            route: "/frameworks",
          },
          {
            type: "Evidence" as const,
            path: "/evidence/",
            route: "/evidence",
          },
        ];

        const responses =
          await Promise.allSettled(
            endpoints.map(
              async (endpoint) => {
                const response =
                  await fetch(
                    `${API_BASE_URL}${endpoint.path}`,
                    {
                      headers,
                    }
                  );

                if (!response.ok) {
                  throw new Error(
                    `Failed to search ${endpoint.type}`
                  );
                }

                const data =
                  await response.json();

                return {
                  endpoint,
                  data,
                };
              }
            )
          );

        const results: SearchResult[] = [];

        for (const result of responses) {
          if (
            result.status !==
            "fulfilled"
          ) {
            continue;
          }

          const {
            endpoint,
            data,
          } = result.value;

          if (!Array.isArray(data)) {
            continue;
          }

          for (const item of data) {
            const title =
              item.title ??
              item.name ??
              item.file_name ??
              `${endpoint.type} #${item.id}`;

            const description =
              item.description ??
              item.scope ??
              item.message ??
              "";

            const searchableText = [
              title,
              description,
              item.status,
              item.control_type,
              item.severity,
              item.priority,
              item.finding_title,
              item.assignee_name,
              item.version,
              item.file_name,
            ]
              .filter(Boolean)
              .join(" ")
              .toLowerCase();

            if (
              searchableText.includes(
                query
              )
            ) {
              results.push({
                id: item.id,
                title,
                description,
                type: endpoint.type,
                path: endpoint.route,
              });
            }
          }
        }

        setSearchResults(
          results.slice(0, 10)
        );
      } catch (error) {
        console.error(
          "Global search failed:",
          error
        );

        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    };

    const timeout =
      window.setTimeout(
        runSearch,
        250
      );

    return () => {
      window.clearTimeout(timeout);
    };
  }, [search]);

  /* ================================================== */
  /* SEARCH KEYBOARD SHORTCUT */
  /* ================================================== */

  useEffect(() => {
    const handleKeyboardShortcut = (
      event: KeyboardEvent
    ) => {
      if (
        (event.ctrlKey ||
          event.metaKey) &&
        event.key.toLowerCase() ===
          "k"
      ) {
        event.preventDefault();

        searchInputRef.current?.focus();

        setSearchOpen(true);
      }

      if (event.key === "Escape") {
        setSearch("");
        setSearchResults([]);
        setSearchOpen(false);

        searchInputRef.current?.blur();

        setNotificationsOpen(false);
      }
    };

    window.addEventListener(
      "keydown",
      handleKeyboardShortcut
    );

    return () => {
      window.removeEventListener(
        "keydown",
        handleKeyboardShortcut
      );
    };
  }, []);

  /* ================================================== */
  /* CLOSE SEARCH / NOTIFICATIONS OUTSIDE */
  /* ================================================== */

  useEffect(() => {
    const handleOutsideClick = (
      event: MouseEvent
    ) => {
      if (
        searchRef.current &&
        !searchRef.current.contains(
          event.target as Node
        )
      ) {
        setSearchOpen(false);
      }

      if (
        notificationRef.current &&
        !notificationRef.current.contains(
          event.target as Node
        )
      ) {
        setNotificationsOpen(false);
      }
    };

    document.addEventListener(
      "mousedown",
      handleOutsideClick
    );

    return () => {
      document.removeEventListener(
        "mousedown",
        handleOutsideClick
      );
    };
  }, []);

  /* ================================================== */
  /* SEARCH RESULT CLICK */
  /* ================================================== */

  const handleSearchResultClick = (
    result: SearchResult
  ) => {
    setSearch("");
    setSearchResults([]);
    setSearchOpen(false);

    navigate(
      `${result.path}/${result.id}`
    );
  };

  /* ================================================== */
  /* FETCH NOTIFICATIONS */
  /* ================================================== */

  const fetchNotifications = async () => {
    try {
      setNotificationsError(false);

      const data =
        await getNotifications();

      setNotifications(data);
    } catch (error) {
      console.error(
        "Failed to load notifications:",
        error
      );

      setNotificationsError(true);
    }
  };

  /* ================================================== */
  /* FETCH UNREAD COUNT */
  /* ================================================== */

  const fetchUnreadCount = async () => {
    try {
      const count =
        await getUnreadNotificationCount();

      setUnreadCount(count);
    } catch (error) {
      console.error(
        "Failed to load unread notification count:",
        error
      );
    }
  };

  /* ================================================== */
  /* LOAD NOTIFICATIONS */
  /* ================================================== */

  const loadNotificationData =
    async () => {
      setNotificationsLoading(true);

      try {
        await Promise.all([
          fetchNotifications(),
          fetchUnreadCount(),
        ]);
      } finally {
        setNotificationsLoading(
          false
        );
      }
    };

  /* ================================================== */
  /* NOTIFICATION AUTO REFRESH */
  /* ================================================== */

  useEffect(() => {
    loadNotificationData();

    const interval =
      window.setInterval(() => {
        fetchNotifications();
        fetchUnreadCount();
      }, 30000);

    return () => {
      window.clearInterval(
        interval
      );
    };
  }, []);

  /* ================================================== */
  /* MARK ONE NOTIFICATION AS READ */
  /* ================================================== */

  const handleMarkNotificationAsRead =
    async (
      notificationId: number
    ) => {
      try {
        await markNotificationAsRead(
          notificationId
        );

        setNotifications(
          (current) =>
            current.map(
              (notification) =>
                notification.id ===
                notificationId
                  ? {
                      ...notification,
                      is_read: true,
                    }
                  : notification
            )
        );

        setUnreadCount(
          (current) =>
            Math.max(
              0,
              current - 1
            )
        );
      } catch (error) {
        console.error(
          "Failed to mark notification as read:",
          error
        );
      }
    };

  /* ================================================== */
  /* MARK ALL NOTIFICATIONS AS READ */
  /* ================================================== */

  const handleMarkAllNotificationsAsRead =
    async () => {
      if (unreadCount === 0) {
        return;
      }

      try {
        await markAllNotificationsAsRead();

        setNotifications(
          (current) =>
            current.map(
              (notification) => ({
                ...notification,
                is_read: true,
              })
            )
        );

        setUnreadCount(0);
      } catch (error) {
        console.error(
          "Failed to mark all notifications as read:",
          error
        );
      }
    };

  /* ================================================== */
  /* NOTIFICATION ICON */
  /* ================================================== */

  const getNotificationIcon = (
    type: string
  ) => {
    switch (type) {
      case "critical_risk":
        return (
          <ShieldAlert
            size={18}
            className="text-red-500"
          />
        );

      case "audit_created":
        return (
          <ClipboardCheck
            size={18}
            className="text-blue-500"
          />
        );

      case "critical_finding":
        return (
          <FileWarning
            size={18}
            className="text-orange-500"
          />
        );

      case "critical_action":
      case "action_due_soon":
      case "action_overdue":
        return (
          <Wrench
            size={18}
            className="text-amber-500"
          />
        );

      default:
        return (
          <Bell
            size={18}
            className="text-blue-500"
          />
        );
    }
  };

  return (
    <header
      className="
        relative
        flex
        h-16
        items-center
        justify-between
        border-b
        border-slate-200
        bg-white
        px-6
        transition-colors
        dark:border-slate-800
        dark:bg-slate-950
      "
    >
      {/* ================================================== */}
      {/* SEARCH */}
      {/* ================================================== */}

      <div
        ref={searchRef}
        className="relative"
      >
        <div
          className="
            flex
            items-center
            gap-3
            rounded-xl
            border
            border-slate-200
            bg-slate-50
            px-4
            py-2
            transition
            focus-within:border-blue-500
            focus-within:bg-white
            focus-within:ring-2
            focus-within:ring-blue-100
            dark:border-slate-700
            dark:bg-slate-900
            dark:focus-within:border-blue-500
            dark:focus-within:bg-slate-900
          "
        >
          <Search
            size={18}
            className="
              shrink-0
              text-slate-400
              dark:text-slate-500
            "
          />

          <input
            ref={searchInputRef}
            type="text"
            value={search}
            onFocus={() => {
              if (search.trim()) {
                setSearchOpen(true);
              }
            }}
            onChange={(event) =>
              setSearch(
                event.target.value
              )
            }
            placeholder="Search risks, controls, audits..."
            className="
              w-72
              bg-transparent
              text-sm
              text-slate-900
              outline-none
              placeholder:text-slate-400
              dark:text-slate-100
              dark:placeholder:text-slate-500
            "
          />

          {search ? (
            <button
              type="button"
              onClick={() => {
                setSearch("");
                setSearchResults([]);
                setSearchOpen(false);
                searchInputRef.current?.focus();
              }}
              className="
                rounded-md
                p-1
                text-slate-400
                hover:bg-slate-200
                hover:text-slate-700
                dark:hover:bg-slate-700
                dark:hover:text-slate-200
              "
              aria-label="Clear search"
            >
              <X size={14} />
            </button>
          ) : (
            <span
              className="
                hidden
                rounded-md
                border
                border-slate-200
                bg-white
                px-2
                py-0.5
                text-[10px]
                font-medium
                text-slate-400
                lg:inline-block
                dark:border-slate-700
                dark:bg-slate-800
                dark:text-slate-500
              "
            >
              Ctrl K
            </span>
          )}
        </div>

        {/* ================================================== */}
        {/* SEARCH RESULTS */}
        {/* ================================================== */}

        {searchOpen &&
          search.trim() && (
            <div
              className="
                absolute
                left-0
                top-full
                z-50
                mt-2
                w-[420px]
                overflow-hidden
                rounded-xl
                border
                border-slate-200
                bg-white
                shadow-xl
                dark:border-slate-700
                dark:bg-slate-900
              "
            >
              {searchLoading ? (
                <div
                  className="
                    px-4
                    py-5
                    text-center
                    text-sm
                    text-slate-500
                    dark:text-slate-400
                  "
                >
                  Searching...
                </div>
              ) : searchResults.length ===
                0 ? (
                <div
                  className="
                    px-4
                    py-6
                    text-center
                  "
                >
                  <Search
                    size={22}
                    className="
                      mx-auto
                      mb-2
                      text-slate-400
                    "
                  />

                  <p
                    className="
                      text-sm
                      font-medium
                      text-slate-700
                      dark:text-slate-200
                    "
                  >
                    No results found
                  </p>

                  <p
                    className="
                      mt-1
                      text-xs
                      text-slate-400
                    "
                  >
                    Try another search term.
                  </p>
                </div>
              ) : (
                <>
                  <div
                    className="
                      border-b
                      border-slate-100
                      px-4
                      py-2
                      text-xs
                      font-semibold
                      uppercase
                      tracking-wide
                      text-slate-400
                      dark:border-slate-800
                    "
                  >
                    Search Results
                  </div>

                  {searchResults.map(
                    (result) => (
                      <button
                        key={`${result.type}-${result.id}`}
                        type="button"
                        onClick={() =>
                          handleSearchResultClick(
                            result
                          )
                        }
                        className="
                          flex
                          w-full
                          items-start
                          gap-3
                          border-b
                          border-slate-100
                          px-4
                          py-3
                          text-left
                          transition
                          last:border-b-0
                          hover:bg-slate-50
                          dark:border-slate-800
                          dark:hover:bg-slate-800
                        "
                      >
                        <div
                          className="
                            mt-0.5
                            flex
                            h-8
                            w-8
                            shrink-0
                            items-center
                            justify-center
                            rounded-lg
                            bg-blue-50
                            text-blue-600
                            dark:bg-blue-950
                            dark:text-blue-400
                          "
                        >
                          {result.type ===
                            "Risk" && (
                            <ShieldAlert
                              size={16}
                            />
                          )}

                          {result.type ===
                            "Control" && (
                            <Wrench
                              size={16}
                            />
                          )}

                          {result.type ===
                            "Audit" && (
                            <ClipboardCheck
                              size={16}
                            />
                          )}

                          {result.type ===
                            "Finding" && (
                            <FileWarning
                              size={16}
                            />
                          )}

                          {result.type ===
                            "Corrective Action" && (
                            <CheckCheck
                              size={16}
                            />
                          )}

                          {result.type ===
                            "Framework" && (
                            <BookOpen
                              size={16}
                            />
                          )}

                          {result.type ===
                            "Evidence" && (
                            <FileText
                              size={16}
                            />
                          )}
                        </div>

                        <div className="min-w-0">
                          <p
                            className="
                              truncate
                              text-sm
                              font-semibold
                              text-slate-800
                              dark:text-slate-100
                            "
                          >
                            {result.title}
                          </p>

                          <p
                            className="
                              mt-0.5
                              text-xs
                              font-medium
                              text-blue-600
                              dark:text-blue-400
                            "
                          >
                            {result.type}
                          </p>

                          {result.description && (
                            <p
                              className="
                                mt-1
                                line-clamp-1
                                text-xs
                                text-slate-500
                                dark:text-slate-400
                              "
                            >
                              {
                                result.description
                              }
                            </p>
                          )}
                        </div>
                      </button>
                    )
                  )}
                </>
              )}
            </div>
          )}
      </div>

      {/* ================================================== */}
      {/* RIGHT SIDE */}
      {/* ================================================== */}

      <div className="flex items-center gap-3">

        {/* DARK / LIGHT MODE */}

        <button
          type="button"
          onClick={toggleTheme}
          aria-label={
            theme === "dark"
              ? "Switch to light mode"
              : "Switch to dark mode"
          }
          title={
            theme === "dark"
              ? "Switch to light mode"
              : "Switch to dark mode"
          }
          className="
            rounded-xl
            p-2
            transition
            hover:bg-slate-100
            dark:hover:bg-slate-800
          "
        >
          {theme === "dark" ? (
            <Sun
              size={20}
              className="
                text-slate-700
                dark:text-slate-200
              "
            />
          ) : (
            <Moon
              size={20}
              className="
                text-slate-700
                dark:text-slate-200
              "
            />
          )}
        </button>

        {/* ================================================== */}
        {/* NOTIFICATIONS */}
        {/* ================================================== */}

        <div
          ref={notificationRef}
          className="relative"
        >
          <button
            type="button"
            aria-label="Notifications"
            title="Notifications"
            onClick={() =>
              setNotificationsOpen(
                (current) => !current
              )
            }
            className="
              relative
              rounded-xl
              p-2.5
              text-slate-600
              transition
              hover:bg-slate-100
              hover:text-slate-900
              dark:text-slate-300
              dark:hover:bg-slate-800
              dark:hover:text-white
            "
          >
            <Bell size={20} />

            {unreadCount > 0 && (
              <span
                className="
                  absolute
                  right-1
                  top-1
                  flex
                  h-2
                  w-2
                  rounded-full
                  bg-red-500
                "
              />
            )}
          </button>

          {notificationsOpen && (
            <div
              className="
                absolute
                right-0
                top-full
                z-50
                mt-2
                w-96
                overflow-hidden
                rounded-xl
                border
                border-slate-200
                bg-white
                shadow-xl
                dark:border-slate-700
                dark:bg-slate-900
              "
            >
              <div
                className="
                  flex
                  items-center
                  justify-between
                  border-b
                  border-slate-100
                  px-4
                  py-3
                  dark:border-slate-800
                "
              >
                <div>
                  <p
                    className="
                      font-semibold
                      text-slate-800
                      dark:text-slate-100
                    "
                  >
                    Notifications
                  </p>

                  <p
                    className="
                      text-xs
                      text-slate-500
                      dark:text-slate-400
                    "
                  >
                    {unreadCount} unread
                  </p>
                </div>

                {unreadCount > 0 && (
                  <button
                    type="button"
                    onClick={
                      handleMarkAllNotificationsAsRead
                    }
                    className="
                      text-xs
                      font-medium
                      text-blue-600
                      hover:text-blue-700
                      dark:text-blue-400
                    "
                  >
                    Mark all read
                  </button>
                )}
              </div>

              <div className="max-h-96 overflow-y-auto">
                {notificationsLoading ? (
                  <div
                    className="
                      px-4
                      py-8
                      text-center
                      text-sm
                      text-slate-500
                    "
                  >
                    Loading notifications...
                  </div>
                ) : notificationsError ? (
                  <div
                    className="
                      px-4
                      py-8
                      text-center
                      text-sm
                      text-red-500
                    "
                  >
                    Unable to load notifications.
                  </div>
                ) : notifications.length ===
                  0 ? (
                  <div className="px-4 py-8 text-center">
                    <Bell
                      size={20}
                      className="
                        mx-auto
                        mb-2
                        text-slate-400
                      "
                    />

                    <p
                      className="
                        text-sm
                        font-medium
                        text-slate-700
                        dark:text-slate-200
                      "
                    >
                      No notifications
                    </p>

                    <p
                      className="
                        mt-1
                        text-xs
                        text-slate-500
                      "
                    >
                      You're all caught up.
                    </p>
                  </div>
                ) : (
                  notifications.map(
                    (notification) => (
                      <button
                        key={notification.id}
                        type="button"
                        onClick={() => {
                          if (
                            !notification.is_read
                          ) {
                            handleMarkNotificationAsRead(
                              notification.id
                            );
                          }
                        }}
                        className={`
                          flex
                          w-full
                          gap-3
                          border-b
                          border-slate-100
                          px-4
                          py-3
                          text-left
                          transition
                          last:border-b-0
                          hover:bg-slate-50
                          dark:border-slate-800
                          dark:hover:bg-slate-800
                          ${
                            notification.is_read
                              ? ""
                              : "bg-blue-50/50 dark:bg-blue-950/20"
                          }
                        `}
                      >
                        <div className="mt-1 shrink-0">
                          {getNotificationIcon(
                            notification.type
                          )}
                        </div>

                        <div className="min-w-0">
                          <p
                            className="
                              text-sm
                              font-semibold
                              text-slate-800
                              dark:text-slate-100
                            "
                          >
                            {
                              notification.title
                            }
                          </p>

                          <p
                            className="
                              mt-1
                              text-xs
                              leading-5
                              text-slate-500
                              dark:text-slate-400
                            "
                          >
                            {
                              notification.message
                            }
                          </p>
                        </div>
                      </button>
                    )
                  )
                )}
              </div>
            </div>
          )}
        </div>

        {/* ================================================== */}
        {/* USER INFORMATION */}
        {/* Static — no dropdown */}
        {/* ================================================== */}

        <div
          className="
            flex
            items-center
            gap-3
            rounded-xl
            px-3
            py-2
          "
        >
          <Avatar>
            <AvatarFallback>
              {initials}
            </AvatarFallback>
          </Avatar>

          <div className="hidden text-left md:block">
            {isLoading ? (
              <>
                <p
                  className="
                    font-semibold
                    text-slate-900
                    dark:text-white
                  "
                >
                  Loading...
                </p>

                <p
                  className="
                    text-sm
                    text-slate-500
                    dark:text-slate-400
                  "
                >
                  Please wait
                </p>
              </>
            ) : (
              <>
                <p
                  className="
                    font-semibold
                    text-slate-900
                    dark:text-white
                  "
                >
                  {user?.full_name}
                </p>

                <p
                  className="
                    text-sm
                    capitalize
                    text-slate-500
                    dark:text-slate-400
                  "
                >
                  {user?.role.replace(
                    "_",
                    " "
                  )}
                </p>
              </>
            )}
          </div>
        </div>

      </div>
    </header>
  );
}