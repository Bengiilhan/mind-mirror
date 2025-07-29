import { createContext, useContext, useState, useCallback } from "react";
import { useToast } from "@chakra-ui/react";

const AuthContext = createContext();

export function AuthProvider({ children }) {
  const [isAuthenticated, setIsAuthenticated] = useState(!!localStorage.getItem("token"));
  const toast = useToast();

  const login = useCallback((token) => {
    localStorage.setItem("token", token);
    setIsAuthenticated(true);
    toast({
      title: "Giriş başarılı!",
      status: "success",
      duration: 3000,
      isClosable: true,
    });
  }, [toast]);

  const logout = useCallback(() => {
    localStorage.removeItem("token");
    setIsAuthenticated(false);
    toast({
      title: "Çıkış yapıldı",
      status: "info",
      duration: 3000,
      isClosable: true,
    });
  }, [toast]);

  return (
    <AuthContext.Provider value={{ isAuthenticated, login, logout }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
} 