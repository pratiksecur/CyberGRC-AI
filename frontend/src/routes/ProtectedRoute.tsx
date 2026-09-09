import { Navigate } from "react-router-dom";

import { useAuth } from "@/contexts/AuthContext";

import {
  hasPermission,
} from "@/auth/permissions";

import type {
  PermissionAction,
  PermissionResource,
} from "@/auth/permissions";

interface Props {
  children: React.ReactNode;

  resource?: PermissionResource;
  action?: PermissionAction;
}

export default function ProtectedRoute({
  children,
  resource,
  action,
}: Props) {
  const {
    isAuthenticated,
    isLoading,
    user,
  } = useAuth();

  // ==================================================
  // AUTH SESSION LOADING
  // ==================================================

  if (isLoading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-slate-50">
        <div className="text-sm text-slate-500">
          Loading...
        </div>
      </div>
    );
  }

  // ==================================================
  // NOT AUTHENTICATED
  // ==================================================

  if (!isAuthenticated) {
    return (
      <Navigate
        to="/login"
        replace
      />
    );
  }

  // ==================================================
  // PERMISSION CHECK
  // ==================================================

  if (
    resource &&
    action &&
    !hasPermission(
      user?.role,
      resource,
      action
    )
  ) {
    return (
      <Navigate
        to="/dashboard"
        replace
      />
    );
  }

  return <>{children}</>;
}