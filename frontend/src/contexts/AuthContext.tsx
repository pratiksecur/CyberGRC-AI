import {
  createContext,
  useContext,
  useEffect,
  useState,
} from "react";

import type { ReactNode } from "react";

import { login as loginRequest } from "@/api/auth";

interface AuthContextType {
  token: string | null;
  isAuthenticated: boolean;

  login: (
    email: string,
    password: string
  ) => Promise<void>;

  logout: () => void;
}

const AuthContext =
  createContext<AuthContextType | null>(null);

interface Props {
  children: ReactNode;
}

export function AuthProvider({
  children,
}: Props) {

  const [token, setToken] =
    useState<string | null>(null);

  useEffect(() => {

    const savedToken =
      localStorage.getItem("access_token");

    if (savedToken) {
      setToken(savedToken);
    }

  }, []);

  async function login(
    email: string,
    password: string
  ) {

    const response =
      await loginRequest(email, password);

    localStorage.setItem(
      "access_token",
      response.access_token
    );

    setToken(response.access_token);
  }

  function logout() {

    localStorage.removeItem("access_token");

    setToken(null);

    window.location.href = "/login";
    }

  return (
    <AuthContext.Provider
      value={{
        token,
        isAuthenticated: !!token,
        login,
        logout,
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {

  const context =
    useContext(AuthContext);

  if (!context) {
    throw new Error(
      "useAuth must be used inside AuthProvider"
    );
  }

  return context;
}