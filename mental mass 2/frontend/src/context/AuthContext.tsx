import React, {
  createContext,
  useContext,
  useState,
  useEffect,
  ReactNode,
} from "react";
import { login as apiLogin, register as apiRegister } from "@/services/api";

interface User {
  id: string;
  name: string;
  email: string;
  totalSessions?: number;
  avgScore?: number;
  riskLevel?: string;
}

interface AuthContextType {
  user: User | null;
  token: string | null;
  login: (email: string, password: string) => Promise<void>;
  register: (name: string, email: string, password: string) => Promise<void>;
  logout: () => void;
  isAuthenticated: boolean;
}
const AuthContext = createContext<AuthContextType | undefined>(undefined);

export const AuthProvider = ({ children }: { children: ReactNode }) => {
  const [user, setUser] = useState<User | null>(null);
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    const storedToken = localStorage.getItem("token");
    const storedUser = localStorage.getItem("user");
    if (storedToken && storedUser) {
      setToken(storedToken);
      setUser(JSON.parse(storedUser));
    }
  }, []);

  const finishLogin = (userData: User, userToken: string) => {
    setUser(userData);
    setToken(userToken);
    localStorage.setItem("token", userToken);
    localStorage.setItem("user", JSON.stringify(userData));
  };

  const login = async (email: string, password: string) => {
    const response = await apiLogin({ email, password });
    const { token: accessToken, user: fetchedUser } = response.data;

    if (!accessToken || !fetchedUser) {
      throw new Error("Invalid login response from server");
    }

    finishLogin(
      {
        id: fetchedUser.id ?? "",
        name: fetchedUser.name ?? fetchedUser.email,
        email: fetchedUser.email,
        totalSessions: fetchedUser.totalSessions,
        avgScore: fetchedUser.avgScore,
        riskLevel: fetchedUser.riskLevel,
      },
      accessToken,
    );
  };

  const register = async (name: string, email: string, password: string) => {
    const response = await apiRegister({ name, email, password });

    if (!response?.data?.token || !response?.data?.user) {
      throw new Error("Invalid register response from server");
    }

    const registeredUser = response.data.user;

    finishLogin(
      {
        id: registeredUser.id ?? "",
        name: registeredUser.name ?? name,
        email: registeredUser.email,
      },
      response.data.token,
    );
  };

  const logout = () => {
    setUser(null);
    setToken(null);
    localStorage.removeItem("token");
    localStorage.removeItem("user");
  };

  return (
    <AuthContext.Provider
      value={{ user, token, login, register, logout, isAuthenticated: !!token }}
    >
      {children}
    </AuthContext.Provider>
  );
};

export const useAuth = () => {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
};
