import { useAuth } from "@/contexts/AuthContext";

import {
  hasPermission,
} from "@/auth/permissions";

import type {
  PermissionAction,
  PermissionResource,
} from "@/auth/permissions";

export function usePermission(
  resource: PermissionResource,
  action: PermissionAction
): boolean {
  const { user } = useAuth();

  return hasPermission(
    user?.role,
    resource,
    action
  );
}