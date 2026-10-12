import {
  useEffect,
  useState,
} from "react";

import type { ReactNode } from "react";
import type { CurrentUser } from "@/api/auth";

import {
  login as loginRequest,
  logout as logoutRequest,
  getCurrentUser,
  getCsrfToken,
} from "@/api/auth";

import { setCsrfToken } from "@/api/axios";

import { AuthContext } from "./auth-context";


interface Props {
  children: ReactNode;
}


export function AuthProvider({
  children,
}: Props) {
  const [
    user,
    setUser,
  ] = useState<CurrentUser | null>(null);

  const [
    isLoading,
    setIsLoading,
  ] = useState(true);


  // ==================================================
  // CLEAR SESSION (React state only)
  // ==================================================

  function clearSession() {
    setCsrfToken(null);
    setUser(null);
  }


  // ==================================================
  // LOAD THE SESSION FROM THE SERVER
  // ==================================================

  /*
   * The access token lives in an httpOnly cookie that the browser sends
   * automatically. The server tells us who the user is, and gives us the
   * CSRF token that must accompany state-changing requests.
   */
  async function loadSession() {
    const currentUser =
      await getCurrentUser();

    const csrfToken =
      await getCsrfToken();

    setCsrfToken(csrfToken);
    setUser(currentUser);
  }


  // ==================================================
  // RESTORE SESSION
  // ==================================================

  useEffect(() => {
    async function restoreSession() {
      /*
       * Earlier versions kept the token in localStorage. Remove any
       * leftover copy so it cannot be read by scripts.
       */
      try {
        localStorage.removeItem(
          "access_token"
        );
      } catch {
        // Storage may be unavailable; nothing to clean up then.
      }

      try {
        await loadSession();

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
    /*
     * A successful login makes the server set the session cookie.
     */
    await loginRequest(
      email,
      password
    );

    try {
      await loadSession();

    } catch (error) {
      /*
       * If authentication succeeds but the user session cannot be
       * established, do not leave a half-open session behind.
       */
      clearSession();

      try {
        await logoutRequest();
      } catch {
        // The original error is more useful to the caller.
      }

      throw error;
    }
  }


  // ==================================================
  // LOGOUT
  // ==================================================

  function logout() {
    logoutRequest()
      .catch(() => {
        // Even if the request fails, leave the app.
      })
      .finally(() => {
        clearSession();

        window.location.href =
          "/login";
      });
  }


  // ==================================================
  // PROVIDER
  // ==================================================

  return (
    <AuthContext.Provider
      value={{
        user,
        isAuthenticated:
          !!user,
        isLoading,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}