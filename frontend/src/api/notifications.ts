import api from "./axios";

export interface Notification {
  id: number;

  type: string;

  title: string;

  message: string;

  source_type: string;

  source_id: number;

  is_read: boolean;

  created_at: string;
}

export interface UnreadNotificationCount {
  unread_count: number;
}

export async function getNotifications(): Promise<Notification[]> {
  const response = await api.get(
    "/notifications/"
  );

  return response.data;
}

export async function getUnreadNotificationCount(): Promise<number> {
  const response = await api.get(
    "/notifications/unread-count"
  );

  return response.data.unread_count;
}

export async function markNotificationAsRead(
  notificationId: number
): Promise<Notification> {
  const response = await api.patch(
    `/notifications/${notificationId}/read`
  );

  return response.data;
}

export async function markAllNotificationsAsRead(): Promise<void> {
  await api.patch(
    "/notifications/read-all"
  );
}