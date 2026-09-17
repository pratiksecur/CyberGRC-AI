import { useState } from "react";
import { Navigate } from "react-router-dom";

import { Shield } from "lucide-react";

import { useAuth } from "@/contexts/useAuth";

export default function Login() {

  const { login, isAuthenticated } = useAuth();

  const [email, setEmail] = useState("");

  const [password, setPassword] = useState("");

  const [loading, setLoading] = useState(false);

  const [error, setError] = useState("");

  if (isAuthenticated) {
    return <Navigate to="/dashboard" replace />;
  }

  async function handleSubmit(
    e: React.FormEvent
  ) {

    e.preventDefault();

    setLoading(true);

    setError("");

    try {

      await login(
        email,
        password
      );

    } catch {

      setError(
        "Invalid email or password."
      );

    } finally {

      setLoading(false);

    }

  }

  return (

    <div className="flex min-h-screen items-center justify-center bg-slate-100 p-6">

      <div className="w-full max-w-md rounded-2xl bg-white p-8 shadow-xl">

        <div className="mb-8 text-center">

          <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-2xl bg-blue-600 text-white">

            <Shield size={32} />

          </div>

          <h1 className="text-3xl font-bold">

            CyberGRC AI

          </h1>

          <p className="mt-2 text-slate-500">

            Enterprise Governance,
            Risk & Compliance Platform

          </p>

        </div>

        <form
          onSubmit={handleSubmit}
          className="space-y-5"
        >

          <div>

            <label className="mb-2 block text-sm font-medium">

              Email

            </label>

            <input
              type="email"
              value={email}
              onChange={(e) =>
                setEmail(
                  e.target.value
                )
              }
              required
              className="w-full rounded-xl border border-slate-300 px-4 py-3 focus:border-blue-500 focus:outline-none"
            />

          </div>

          <div>

            <label className="mb-2 block text-sm font-medium">

              Password

            </label>

            <input
              type="password"
              value={password}
              onChange={(e) =>
                setPassword(
                  e.target.value
                )
              }
              required
              className="w-full rounded-xl border border-slate-300 px-4 py-3 focus:border-blue-500 focus:outline-none"
            />

          </div>

          {error && (

            <div className="rounded-lg bg-red-100 p-3 text-sm text-red-700">

              {error}

            </div>

          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full rounded-xl bg-blue-600 py-3 font-semibold text-white transition hover:bg-blue-700 disabled:opacity-50"
          >

            {loading
              ? "Signing In..."
              : "Sign In"}

          </button>

        </form>

        <div className="mt-6 text-center text-sm text-slate-500">
          Don't have an account?{" "}
          <button
            type="button"
            onClick={() => {
              window.location.href = "/register";
            }}
            className="font-semibold text-blue-600 hover:text-blue-700"
          >
            Create one
          </button>
        </div>

        <div className="mt-8 text-center text-sm text-slate-500">

          Secure JWT Authentication

        </div>

      </div>

    </div>

  );

}