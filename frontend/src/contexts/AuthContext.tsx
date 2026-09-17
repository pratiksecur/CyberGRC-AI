import {
  useEffect,
  useState,
} from "react";

import type { ReactNode } from "react";
import type { CurrentUser } from "@/api/auth";

import {
  login as loginRequest,
  getCurrentUser,
} from "@/api/auth";

import { AuthContext } from "./auth-context";

interface Props {
  children: ReactNode;
}

export function AuthProvider({
  children,
}: Props) {
  const [token, setToken] =
    useState<string | null>(null);

  const [user, setUser] =
    useState<CurrentUser | null>(null);

  const [isLoading, setIsLoading] =
    useState(true);

  // ==================================================
  // RESTORE SESSION
  // ==================================================

  useEffect(() => {
    async function restoreSession() {
      const savedToken =
        localStorage.getItem("access_token");

      if (!savedToken) {
        setIsLoading(false);
        return;
      }

      setToken(savedToken);

      try {
        const currentUser =
          await getCurrentUser();

        setUser(currentUser);
      } catch {
        localStorage.removeItem(
          "access_token"
        );

        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    restoreSession();
  }, []);

  // ==================================================
  // LOGIN
  // ==================================================

  async function login(
    email: string,
    password: string
  ) {
    const response =
      await loginRequest(
        email,
        password
      );

    localStorage.setItem(
      "access_token",
      response.access_token
    );

    setToken(
      response.access_token
    );

    const currentUser =
      await getCurrentUser();

    setUser(currentUser);
  }

  // ==================================================
  // LOGOUT
  // ==================================================

  function logout() {
    localStorage.removeItem(
      "access_token"
    );

    setToken(null);
    setUser(null);

    window.location.href = "/login";
  }

  // ==================================================
  // PROVIDER
  // ==================================================

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        isAuthenticated: !!token && !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}