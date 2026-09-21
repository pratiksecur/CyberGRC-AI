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
  const [
    token,
    setToken,
  ] = useState<string | null>(null);

  const [
    user,
    setUser,
  ] = useState<CurrentUser | null>(null);

  const [
    isLoading,
    setIsLoading,
  ] = useState(true);


  // ==================================================
  // CLEAR SESSION
  // ==================================================

  function clearSession() {
    localStorage.removeItem(
      "access_token"
    );

    setToken(null);
    setUser(null);
  }


  // ==================================================
  // RESTORE SESSION
  // ==================================================

  useEffect(() => {
    async function restoreSession() {
      const savedToken =
        localStorage.getItem(
          "access_token"
        );

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
        clearSession();

      } finally {
        setIsLoading(false);
      }
    }

    restoreSession();
  }, []);


  // ==================================================
  // HANDLE CENTRAL 401 EVENTS
  // ==================================================

  useEffect(() => {
    const handleUnauthorized =
      () => {
        clearSession();
      };

    window.addEventListener(
      "auth:unauthorized",
      handleUnauthorized
    );

    return () => {
      window.removeEventListener(
        "auth:unauthorized",
        handleUnauthorized
      );
    };
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

    /*
     * Store the token temporarily so the authenticated
     * /auth/me request can use the normal Axios interceptor.
     */
    localStorage.setItem(
      "access_token",
      response.access_token
    );

    setToken(
      response.access_token
    );

    try {
      const currentUser =
        await getCurrentUser();

      setUser(currentUser);

    } catch (error) {
      /*
       * If authentication succeeds but the user session
       * cannot be established, do not leave a stale token
       * behind.
       */
      clearSession();

      throw error;
    }
  }


  // ==================================================
  // LOGOUT
  // ==================================================

  function logout() {
    clearSession();

    window.location.href =
      "/login";
  }


  // ==================================================
  // PROVIDER
  // ==================================================

  return (
    <AuthContext.Provider
      value={{
        token,
        user,
        isAuthenticated:
          !!token && !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}