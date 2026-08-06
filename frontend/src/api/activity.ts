import api from "./axios";

export interface Activity {
  type: string;
  title: string;
  description: string;
  time: string;
}

export const getRecentActivity = async (): Promise<Activity[]> => {
  const response = await api.get("/dashboard/activity");
  return response.data;
};