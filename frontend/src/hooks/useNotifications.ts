import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import {
  getNotifications,
  getUnreadNotificationCount,
  markNotificationAsRead,
  markAllNotificationsAsRead,
} from "@/api/notifications";


export function useNotifications() {

  const queryClient = useQueryClient();

  const notificationsQuery = useQuery({
    queryKey: ["notifications"],
    queryFn: getNotifications,
    refetchInterval: 30000,
  });

  const unreadCountQuery = useQuery({
    queryKey: ["notifications", "unread-count"],
    queryFn: getUnreadNotificationCount,
    refetchInterval: 30000,
  });

  const markReadMutation = useMutation({
    mutationFn: markNotificationAsRead,

    onSuccess: () => {

      queryClient.invalidateQueries({
        queryKey: ["notifications"],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "notifications",
          "unread-count",
        ],
      });
    },
  });

  const markAllReadMutation = useMutation({
    mutationFn: markAllNotificationsAsRead,

    onSuccess: () => {

      queryClient.invalidateQueries({
        queryKey: ["notifications"],
      });

      queryClient.invalidateQueries({
        queryKey: [
          "notifications",
          "unread-count",
        ],
      });
    },
  });

  return {
    notifications: notificationsQuery.data ?? [],

    unreadCount:
      unreadCountQuery.data ?? 0,

    isLoading:
      notificationsQuery.isLoading ||
      unreadCountQuery.isLoading,

    isError:
      notificationsQuery.isError ||
      unreadCountQuery.isError,

    markAsRead:
      markReadMutation.mutate,

    markAllAsRead:
      markAllReadMutation.mutate,

    isMarkingRead:
      markReadMutation.isPending,

    isMarkingAllRead:
      markAllReadMutation.isPending,
  };
}