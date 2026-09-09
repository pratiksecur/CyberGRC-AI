import type { ReactNode } from "react";

import { useAuth } from "@/contexts/AuthContext";
import {
  hasPermission,
  type PermissionAction,
  type PermissionResource,
} from "@/auth/permissions";

interface CanProps {
  resource: PermissionResource;
  action: PermissionAction;
  children: ReactNode;
  fallback?: ReactNode;
}

export default function Can({
  resource,
  action,
  children,
  fallback = null,
}: CanProps) {
  const { user } = useAuth();

  const allowed = hasPermission(
    user?.role,
    resource,
    action
  );

  if (!allowed) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}