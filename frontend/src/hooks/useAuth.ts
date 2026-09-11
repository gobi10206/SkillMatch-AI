import { useState, useCallback } from "react";
import { api, setSession, clearSession } from "../services/api";
import type { UserOut } from "../types";

export function useAuth() {
  const [user, setUser] = useState<UserOut | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const login = useCallback(async (email: string, password: string) => {
    setLoading(true);
    setError(null);
    try {
      const { data } = await api.post("/auth/login", { email, password });
      setSession(data.access_token, data.refresh_token);
      const me = await api.get("/auth/me");
      setUser(me.data);
      return true;
    } catch (err: any) {
      setError(err?.response?.data?.detail || "Login failed");
      return false;
    } finally {
      setLoading(false);
    }
  }, []);

  const register = useCallback(
    async (email: string, password: string, fullName: string, role: string) => {
      setLoading(true);
      setError(null);
      try {
        await api.post("/auth/register", { email, password, full_name: fullName, role });
        return await login(email, password);
      } catch (err: any) {
        setError(err?.response?.data?.detail || "Registration failed");
        return false;
      } finally {
        setLoading(false);
      }
    },
    [login]
  );

  const logout = useCallback(() => {
    clearSession();
    setUser(null);
  }, []);

  return { user, loading, error, login, register, logout };
}
