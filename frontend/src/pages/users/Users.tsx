import { useState } from "react";
import { Link } from "react-router-dom";
import {
  useMutation,
  useQuery,
  useQueryClient,
} from "@tanstack/react-query";

import { UserCheck, UserPlus, UserX, KeyRound } from "lucide-react";

import AppLayout from "@/layouts/AppLayout";
import { useAuth } from "@/contexts/useAuth";
import { apiErrorMessage } from "@/lib/apiError";
import {
  activateUser,
  deactivateUser,
  getAllUsers,
  resetUserPassword,
  type ManagedUser,
} from "@/api/user";

const USERS_KEY = ["admin-users"];

export default function Users() {
  const { user: me } = useAuth();
  const queryClient = useQueryClient();

  const [message, setMessage] = useState("");
  const [error, setError] = useState("");

  /* Only one row at a time is in "confirm" or "reset password" mode. */
  const [confirmId, setConfirmId] = useState<number | null>(null);
  const [resetId, setResetId] = useState<number | null>(null);
  const [newPassword, setNewPassword] = useState("");

  const { data: users, isLoading, isError } = useQuery({
    queryKey: USERS_KEY,
    queryFn: getAllUsers,
  });

  function done(text: string) {
    setError("");
    setMessage(text);
    setConfirmId(null);
    setResetId(null);
    setNewPassword("");
    queryClient.invalidateQueries({ queryKey: USERS_KEY });
  }

  function failed(err: unknown, fallback: string) {
    setMessage("");
    setError(apiErrorMessage(err, fallback));
  }

  const deactivate = useMutation({
    mutationFn: (id: number) => deactivateUser(id),
    onSuccess: () => done("User deactivated. Their sessions were ended."),
    onError: (err) => failed(err, "Could not deactivate the user."),
  });

  const activate = useMutation({
    mutationFn: (id: number) => activateUser(id),
    onSuccess: () => done("User activated."),
    onError: (err) => failed(err, "Could not activate the user."),
  });

  const reset = useMutation({
    mutationFn: (vars: { id: number; password: string }) =>
      resetUserPassword(vars.id, vars.password),
    onSuccess: () =>
      done("Password reset. The user must sign in again."),
    onError: (err) => failed(err, "Could not reset the password."),
  });

  const busy =
    deactivate.isPending || activate.isPending || reset.isPending;

  function renderActions(person: ManagedUser) {
    if (person.id === me?.id) {
      return <span className="text-sm text-slate-400">You</span>;
    }

    if (resetId === person.id) {
      return (
        <form
          className="flex flex-wrap items-center gap-2"
          onSubmit={(e) => {
            e.preventDefault();
            reset.mutate({ id: person.id, password: newPassword });
          }}
        >
          <input
            type="password"
            value={newPassword}
            onChange={(e) => setNewPassword(e.target.value)}
            autoComplete="new-password"
            placeholder="New password (10+ characters)"
            required
            minLength={10}
            className="w-64 rounded-lg border border-slate-300 px-3 py-2 text-sm focus:border-blue-500 focus:outline-none"
          />
          <button
            type="submit"
            disabled={busy}
            className="rounded-lg bg-blue-600 px-3 py-2 text-sm font-semibold text-white hover:bg-blue-700 disabled:opacity-50"
          >
            Set password
          </button>
          <button
            type="button"
            onClick={() => {
              setResetId(null);
              setNewPassword("");
            }}
            className="rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
          >
            Cancel
          </button>
        </form>
      );
    }

    if (confirmId === person.id) {
      return (
        <div className="flex items-center gap-2">
          <span className="text-sm text-slate-600">
            Sign them out and block access?
          </span>
          <button
            type="button"
            disabled={busy}
            onClick={() => deactivate.mutate(person.id)}
            className="rounded-lg bg-red-600 px-3 py-2 text-sm font-semibold text-white hover:bg-red-700 disabled:opacity-50"
          >
            Deactivate
          </button>
          <button
            type="button"
            onClick={() => setConfirmId(null)}
            className="rounded-lg px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
          >
            Cancel
          </button>
        </div>
      );
    }

    return (
      <div className="flex items-center gap-2">
        <button
          type="button"
          onClick={() => {
            setConfirmId(null);
            setResetId(person.id);
            setNewPassword("");
          }}
          className="flex items-center gap-1.5 rounded-lg border px-3 py-2 text-sm font-medium text-slate-700 hover:bg-slate-50"
        >
          <KeyRound className="h-4 w-4" />
          Reset password
        </button>

        {person.is_active ? (
          <button
            type="button"
            onClick={() => {
              setResetId(null);
              setConfirmId(person.id);
            }}
            className="flex items-center gap-1.5 rounded-lg border border-red-200 px-3 py-2 text-sm font-medium text-red-600 hover:bg-red-50"
          >
            <UserX className="h-4 w-4" />
            Deactivate
          </button>
        ) : (
          <button
            type="button"
            disabled={busy}
            onClick={() => activate.mutate(person.id)}
            className="flex items-center gap-1.5 rounded-lg border border-green-200 px-3 py-2 text-sm font-medium text-green-700 hover:bg-green-50 disabled:opacity-50"
          >
            <UserCheck className="h-4 w-4" />
            Activate
          </button>
        )}
      </div>
    );
  }

  return (
    <AppLayout>
      <div className="mx-auto max-w-6xl space-y-6">

        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-3xl font-bold text-slate-900">
              Users
            </h1>

            <p className="mt-1 text-slate-500">
              Manage who can sign in to your organization.
            </p>
          </div>

          <Link
            to="/register"
            className="flex items-center gap-2 rounded-xl bg-blue-600 px-4 py-2 text-sm font-semibold text-white hover:bg-blue-700"
          >
            <UserPlus className="h-4 w-4" />
            Create user
          </Link>
        </div>

        {error && (
          <div className="rounded-lg bg-red-100 p-3 text-sm text-red-700">
            {error}
          </div>
        )}

        {message && (
          <div className="rounded-lg bg-green-100 p-3 text-sm text-green-700">
            {message}
          </div>
        )}

        <div className="overflow-x-auto rounded-2xl border bg-white shadow-sm">
          <table className="w-full text-left text-sm">
            <thead className="border-b bg-slate-50 text-slate-500">
              <tr>
                <th className="px-5 py-3 font-medium">Name</th>
                <th className="px-5 py-3 font-medium">Email</th>
                <th className="px-5 py-3 font-medium">Role</th>
                <th className="px-5 py-3 font-medium">Status</th>
                <th className="px-5 py-3 font-medium">Actions</th>
              </tr>
            </thead>

            <tbody className="divide-y">
              {isLoading && (
                <tr>
                  <td colSpan={5} className="px-5 py-6 text-slate-400">
                    Loading...
                  </td>
                </tr>
              )}

              {isError && (
                <tr>
                  <td colSpan={5} className="px-5 py-6 text-red-500">
                    Unable to load users.
                  </td>
                </tr>
              )}

              {users?.map((person) => (
                <tr key={person.id}>
                  <td className="px-5 py-4 font-medium text-slate-900">
                    {person.full_name}
                  </td>
                  <td className="px-5 py-4 text-slate-600">
                    {person.email}
                  </td>
                  <td className="px-5 py-4 capitalize text-slate-600">
                    {person.role.replaceAll("_", " ")}
                  </td>
                  <td className="px-5 py-4">
                    <span
                      className={
                        person.is_active
                          ? "rounded-full bg-green-50 px-2.5 py-1 text-xs font-medium text-green-700"
                          : "rounded-full bg-slate-100 px-2.5 py-1 text-xs font-medium text-slate-500"
                      }
                    >
                      {person.is_active ? "Active" : "Deactivated"}
                    </span>
                  </td>
                  <td className="px-5 py-4">{renderActions(person)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

      </div>
    </AppLayout>
  );
}