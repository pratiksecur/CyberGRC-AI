import {
  User,
  ShieldCheck,
  Server,
  Info,
  LogOut,
  CheckCircle2,
} from "lucide-react";

import AppLayout from "@/layouts/AppLayout";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useAuth } from "@/contexts/AuthContext";

export default function Settings() {
  const { logout, isAuthenticated } = useAuth();

  const {
    data: user,
    isLoading,
    isError,
  } = useCurrentUser();

  return (
    <AppLayout>
      <div className="mx-auto max-w-6xl space-y-8">

        {/* ================================================== */}
        {/* HEADER */}
        {/* ================================================== */}

        <div>
          <h1 className="text-3xl font-bold text-slate-900">
            Settings
          </h1>

          <p className="mt-1 text-slate-500">
            Manage your CyberGRC AI account and platform information.
          </p>
        </div>

        {/* ================================================== */}
        {/* ACCOUNT */}
        {/* ================================================== */}

        <section className="rounded-2xl border bg-white shadow-sm">

          <div className="flex items-center gap-3 border-b px-6 py-5">

            <div className="rounded-xl bg-indigo-50 p-3">
              <User className="h-5 w-5 text-indigo-600" />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900">
                Account
              </h2>

              <p className="text-sm text-slate-500">
                Your current CyberGRC AI account information.
              </p>
            </div>

          </div>

          <div className="grid gap-6 p-6 md:grid-cols-2">

            {/* Full Name */}

            <div>
              <p className="text-sm font-medium text-slate-500">
                Full Name
              </p>

              <div className="mt-2 rounded-lg border bg-slate-50 px-4 py-3">

                {isLoading ? (
                  <span className="text-sm text-slate-400">
                    Loading...
                  </span>
                ) : isError ? (
                  <span className="text-sm text-red-500">
                    Unable to load account information.
                  </span>
                ) : (
                  <span className="font-medium text-slate-900">
                    {user?.full_name || "—"}
                  </span>
                )}

              </div>
            </div>

            {/* Email */}

            <div>
              <p className="text-sm font-medium text-slate-500">
                Email Address
              </p>

              <div className="mt-2 rounded-lg border bg-slate-50 px-4 py-3">

                {isLoading ? (
                  <span className="text-sm text-slate-400">
                    Loading...
                  </span>
                ) : isError ? (
                  <span className="text-sm text-red-500">
                    Unable to load account information.
                  </span>
                ) : (
                  <span className="font-medium text-slate-900">
                    {user?.email || "—"}
                  </span>
                )}

              </div>
            </div>

            {/* Role */}

            <div>
              <p className="text-sm font-medium text-slate-500">
                Role
              </p>

              <div className="mt-2 flex items-center gap-2 rounded-lg border bg-slate-50 px-4 py-3">

                {isLoading ? (
                  <span className="text-sm text-slate-400">
                    Loading...
                  </span>
                ) : isError ? (
                  <span className="text-sm text-red-500">
                    Unable to load account information.
                  </span>
                ) : (
                  <span className="font-medium capitalize text-slate-900">
                    {user?.role
                      ? user.role.replaceAll("_", " ")
                      : "—"}
                  </span>
                )}

              </div>
            </div>

            {/* Account Status */}

            <div>
              <p className="text-sm font-medium text-slate-500">
                Account Status
              </p>

              <div className="mt-2 flex items-center gap-2 rounded-lg border bg-slate-50 px-4 py-3">

                <CheckCircle2 className="h-4 w-4 text-green-600" />

                <span className="font-medium text-green-700">
                  {isAuthenticated ? "Active" : "Signed Out"}
                </span>

              </div>

            </div>

          </div>

        </section>

        {/* ================================================== */}
        {/* SECURITY */}
        {/* ================================================== */}

        <section className="rounded-2xl border bg-white shadow-sm">

          <div className="flex items-center gap-3 border-b px-6 py-5">

            <div className="rounded-xl bg-green-50 p-3">
              <ShieldCheck className="h-5 w-5 text-green-600" />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900">
                Security
              </h2>

              <p className="text-sm text-slate-500">
                Information about your current authentication session.
              </p>
            </div>

          </div>

          <div className="space-y-4 p-6">

            <div className="flex items-center justify-between rounded-xl border p-4">

              <div>
                <p className="font-medium text-slate-900">
                  Authentication
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  Your account is authenticated using a secure access token.
                </p>
              </div>

              <div className="flex items-center gap-2 rounded-full bg-green-50 px-3 py-1.5 text-sm font-medium text-green-700">

                <CheckCircle2 className="h-4 w-4" />

                Authenticated

              </div>

            </div>

            <div className="flex items-center justify-between rounded-xl border p-4">

              <div>
                <p className="font-medium text-slate-900">
                  Session
                </p>

                <p className="mt-1 text-sm text-slate-500">
                  Your current CyberGRC AI session is active.
                </p>
              </div>

              <div className="text-sm font-medium text-slate-600">
                Active
              </div>

            </div>

          </div>

        </section>

        {/* ================================================== */}
        {/* PLATFORM */}
        {/* ================================================== */}

        <section className="rounded-2xl border bg-white shadow-sm">

          <div className="flex items-center gap-3 border-b px-6 py-5">

            <div className="rounded-xl bg-blue-50 p-3">
              <Server className="h-5 w-5 text-blue-600" />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900">
                Platform
              </h2>

              <p className="text-sm text-slate-500">
                CyberGRC AI platform information.
              </p>
            </div>

          </div>

          <div className="grid gap-6 p-6 md:grid-cols-2">

            <div className="rounded-xl border bg-slate-50 p-4">

              <p className="text-sm font-medium text-slate-500">
                Application
              </p>

              <p className="mt-1 font-semibold text-slate-900">
                CyberGRC AI
              </p>

              <p className="mt-1 text-sm text-slate-500">
                AI-Powered Governance, Risk & Compliance Platform
              </p>

            </div>

            <div className="rounded-xl border bg-slate-50 p-4">

              <p className="text-sm font-medium text-slate-500">
                Version
              </p>

              <p className="mt-1 font-semibold text-slate-900">
                1.0.0
              </p>

              <p className="mt-1 text-sm text-slate-500">
                Current platform version
              </p>

            </div>

          </div>

        </section>

        {/* ================================================== */}
        {/* INFORMATION */}
        {/* ================================================== */}

        <section className="rounded-2xl border bg-slate-50 p-6">

          <div className="flex items-start gap-3">

            <div className="rounded-lg bg-indigo-100 p-2">
              <Info className="h-5 w-5 text-indigo-600" />
            </div>

            <div>

              <h2 className="font-semibold text-slate-900">
                About CyberGRC AI
              </h2>

              <p className="mt-1 text-sm leading-6 text-slate-600">
                CyberGRC AI provides governance, risk, compliance,
                audit, evidence, remediation, reporting, and AI-powered
                security intelligence capabilities from a centralized
                platform.
              </p>

            </div>

          </div>

        </section>

        {/* ================================================== */}
        {/* LOGOUT */}
        {/* ================================================== */}

        <section className="rounded-2xl border border-red-100 bg-white shadow-sm">

          <div className="flex items-center justify-between gap-6 p-6">

            <div>

              <h2 className="font-semibold text-slate-900">
                Sign Out
              </h2>

              <p className="mt-1 text-sm text-slate-500">
                Sign out of your current CyberGRC AI session.
              </p>

            </div>

            <button
              type="button"
              onClick={logout}
              className="flex items-center gap-2 rounded-lg border border-red-200 px-4 py-2.5 text-sm font-medium text-red-600 transition hover:bg-red-50"
            >

              <LogOut className="h-4 w-4" />

              Sign Out

            </button>

          </div>

        </section>

      </div>
    </AppLayout>
  );
}