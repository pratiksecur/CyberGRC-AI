import {
  User,
  ShieldCheck,
  Server,
  Info,
  LogOut,
  CheckCircle2,
  UserPlus,
  KeyRound,
} from "lucide-react";
import { Link } from "react-router-dom";
import { useState } from "react";

import AppLayout from "@/layouts/AppLayout";
import Can from "@/components/auth/Can";
import { useCurrentUser } from "@/hooks/useCurrentUser";
import { useAuth } from "@/contexts/useAuth";
import { changePassword } from "@/api/auth";
import { apiErrorMessage } from "@/lib/apiError";

export default function Settings() {
  const { logout, isAuthenticated } = useAuth();

  const {
    data: user,
    isLoading,
    isError,
  } = useCurrentUser();

  const [currentPassword, setCurrentPassword] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [passwordSaving, setPasswordSaving] = useState(false);
  const [passwordError, setPasswordError] = useState("");
  const [passwordSuccess, setPasswordSuccess] = useState("");

  async function handlePasswordChange(e: React.FormEvent) {
    e.preventDefault();

    setPasswordError("");
    setPasswordSuccess("");

    if (newPassword.length < 10) {
      setPasswordError("The new password must be at least 10 characters.");
      return;
    }

    if (newPassword !== confirmPassword) {
      setPasswordError("The new passwords do not match.");
      return;
    }

    setPasswordSaving(true);

    try {
      await changePassword(currentPassword, newPassword);

      setPasswordSuccess(
        "Password changed. Your other sessions were signed out."
      );
      setCurrentPassword("");
      setNewPassword("");
      setConfirmPassword("");
    } catch (err: unknown) {
      setPasswordError(
        apiErrorMessage(err, "Could not change the password.")
      );
    } finally {
      setPasswordSaving(false);
    }
  }

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
        {/* CHANGE PASSWORD */}
        {/* ================================================== */}

        <section className="rounded-2xl border bg-white shadow-sm">

          <div className="flex items-center gap-3 border-b px-6 py-5">

            <div className="rounded-xl bg-amber-50 p-3">
              <KeyRound className="h-5 w-5 text-amber-600" />
            </div>

            <div>
              <h2 className="font-semibold text-slate-900">
                Change Password
              </h2>

              <p className="text-sm text-slate-500">
                Use at least 10 characters. Changing it signs you out
                everywhere else.
              </p>
            </div>

          </div>

          <form
            onSubmit={handlePasswordChange}
            className="grid gap-4 p-6 md:grid-cols-3"
          >

            <div>
              <label className="mb-2 block text-sm font-medium">
                Current password
              </label>

              <input
                type="password"
                value={currentPassword}
                onChange={(e) => setCurrentPassword(e.target.value)}
                required
                autoComplete="current-password"
                className="w-full rounded-xl border border-slate-300 px-4 py-3 focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                New password
              </label>

              <input
                type="password"
                value={newPassword}
                onChange={(e) => setNewPassword(e.target.value)}
                required
                minLength={10}
                autoComplete="new-password"
                className="w-full rounded-xl border border-slate-300 px-4 py-3 focus:border-blue-500 focus:outline-none"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Confirm new password
              </label>

              <input
                type="password"
                value={confirmPassword}
                onChange={(e) => setConfirmPassword(e.target.value)}
                required
                minLength={10}
                autoComplete="new-password"
                className="w-full rounded-xl border border-slate-300 px-4 py-3 focus:border-blue-500 focus:outline-none"
              />
            </div>

            {passwordError && (
              <div className="rounded-lg bg-red-100 p-3 text-sm text-red-700 md:col-span-3">
                {passwordError}
              </div>
            )}

            {passwordSuccess && (
              <div className="rounded-lg bg-green-100 p-3 text-sm text-green-700 md:col-span-3">
                {passwordSuccess}
              </div>
            )}

            <div className="md:col-span-3">
              <button
                type="submit"
                disabled={passwordSaving}
                className="rounded-xl bg-blue-600 px-5 py-2.5 text-sm font-semibold text-white transition hover:bg-blue-700 disabled:opacity-50"
              >
                {passwordSaving ? "Saving..." : "Change password"}
              </button>
            </div>

          </form>

        </section>

        <Can resource="users" action="create">
          <section className="rounded-2xl border bg-white shadow-sm">

            <div className="flex items-center justify-between gap-3 px-6 py-5">

              <div className="flex items-center gap-3">
                <div className="rounded-xl bg-blue-50 p-3">
                  <UserPlus className="h-5 w-5 text-blue-600" />
                </div>

                <div>
                  <h2 className="font-semibold text-slate-900">
                    User Management
                  </h2>

                  <p className="text-sm text-slate-500">
                    Add people, reset passwords and deactivate accounts.
                  </p>
                </div>
              </div>

              <div className="flex items-center gap-2">
                <Link
                  to="/users"
                  className="rounded-xl border px-4 py-2 text-sm font-semibold text-slate-700 hover:bg-slate-50"
                >
                  Manage users
                </Link>

                <Link
                  to="/register"
                  className="rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
                >
                  Create user
                </Link>
              </div>

            </div>

          </section>
        </Can>

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