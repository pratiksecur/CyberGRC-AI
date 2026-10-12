import { useState } from "react";
import { Link } from "react-router-dom";

import { UserPlus } from "lucide-react";
import { AxiosError } from "axios";

import AppLayout from "@/layouts/AppLayout";
import { register } from "@/api/auth";

const ROLES = [
  "Employee",
  "Risk Analyst",
  "GRC Manager",
  "Auditor",
  "Admin",
] as const;

export default function Register() {
  const [fullName, setFullName] = useState("");
  const [email, setEmail] = useState("");
  const [role, setRole] = useState<string>("Employee");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] =
    useState("");

  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");

  async function handleSubmit(
    e: React.FormEvent
  ) {
    e.preventDefault();

    setError("");
    setSuccess("");

    if (password.length < 8) {
      setError(
        "Password must be at least 8 characters."
      );
      return;
    }

    if (password !== confirmPassword) {
      setError("Passwords do not match.");
      return;
    }

    setLoading(true);

    try {
      await register({
        full_name: fullName,
        email,
        password,
        role,
      });

      setSuccess(
        `User ${email} was created as ${role}.`
      );

      setFullName("");
      setEmail("");
      setRole("Employee");
      setPassword("");
      setConfirmPassword("");
    } catch (error: unknown) {
      const axiosError =
        error instanceof AxiosError
          ? error
          : null;

      const detail =
        axiosError?.response?.data?.detail;

      if (typeof detail === "string") {
        setError(detail);
      } else {
        setError(
          "Unable to create the user. Please try again."
        );
      }
    } finally {
      setLoading(false);
    }
  }

  return (
    <AppLayout>
      <div className="mx-auto max-w-xl space-y-6">

        <div>
          <h1 className="text-3xl font-bold text-slate-900">
            Create User
          </h1>

          <p className="mt-1 text-slate-500">
            Add a person to your organization. They can
            sign in straight away with the password you
            set here.
          </p>
        </div>

        <div className="rounded-2xl border bg-white p-8 shadow-sm">

          <div className="mb-6 flex h-12 w-12 items-center justify-center rounded-xl bg-blue-600 text-white">
            <UserPlus size={24} />
          </div>

          <form
            onSubmit={handleSubmit}
            className="space-y-5"
          >

            <div>
              <label className="mb-2 block text-sm font-medium">
                Full Name
              </label>

              <input
                type="text"
                value={fullName}
                onChange={(e) =>
                  setFullName(e.target.value)
                }
                required
                minLength={2}
                maxLength={100}
                className="w-full rounded-xl border border-slate-300 px-4 py-3 focus:border-blue-500 focus:outline-none"
                placeholder="Enter the full name"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Email
              </label>

              <input
                type="email"
                value={email}
                onChange={(e) =>
                  setEmail(e.target.value)
                }
                required
                className="w-full rounded-xl border border-slate-300 px-4 py-3 focus:border-blue-500 focus:outline-none"
                placeholder="Enter the email address"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Role
              </label>

              <select
                value={role}
                onChange={(e) =>
                  setRole(e.target.value)
                }
                className="w-full rounded-xl border border-slate-300 bg-white px-4 py-3 focus:border-blue-500 focus:outline-none"
              >
                {ROLES.map((option) => (
                  <option
                    key={option}
                    value={option}
                  >
                    {option}
                  </option>
                ))}
              </select>
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Password
              </label>

              <input
                type="password"
                value={password}
                onChange={(e) =>
                  setPassword(e.target.value)
                }
                required
                minLength={8}
                autoComplete="new-password"
                className="w-full rounded-xl border border-slate-300 px-4 py-3 focus:border-blue-500 focus:outline-none"
                placeholder="Minimum 8 characters"
              />
            </div>

            <div>
              <label className="mb-2 block text-sm font-medium">
                Confirm Password
              </label>

              <input
                type="password"
                value={confirmPassword}
                onChange={(e) =>
                  setConfirmPassword(
                    e.target.value
                  )
                }
                required
                minLength={8}
                autoComplete="new-password"
                className="w-full rounded-xl border border-slate-300 px-4 py-3 focus:border-blue-500 focus:outline-none"
                placeholder="Repeat the password"
              />
            </div>

            {error && (
              <div className="rounded-lg bg-red-100 p-3 text-sm text-red-700">
                {error}
              </div>
            )}

            {success && (
              <div className="rounded-lg bg-green-100 p-3 text-sm text-green-700">
                {success}
              </div>
            )}

            <button
              type="submit"
              disabled={loading}
              className="w-full rounded-xl bg-blue-600 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:opacity-50"
            >
              {loading
                ? "Creating User..."
                : "Create User"}
            </button>

          </form>

          <div className="mt-6 text-center text-sm text-slate-500">
            <Link
              to="/settings"
              className="font-semibold text-blue-600 hover:text-blue-700"
            >
              Back to Settings
            </Link>
          </div>

        </div>
      </div>
    </AppLayout>
  );
}