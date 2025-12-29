"use client";

import { useState, useEffect } from "react";
import Header from "@/components/Header";
import LoginModal from "@/components/LoginModal";
import RegisterModal from "@/components/RegisterModal";
import { useAuth } from "@/hooks/useAuth";

interface AuthProviderProps {
  children: React.ReactNode;
}

/**
 * AuthProvider component that manages authentication state and modals
 * Handles login/register modals and integrates with auth store
 */
export default function AuthProvider({ children }: AuthProviderProps) {
  const [isLoginModalOpen, setIsLoginModalOpen] = useState(false);
  const [isRegisterModalOpen, setIsRegisterModalOpen] = useState(false);
  const { checkAuth } = useAuth();

  // Check auth state on mount and periodically for token expiration
  useEffect(() => {
    // Initial check
    checkAuth();

    // Check token expiration every 5 minutes
    const interval = setInterval(() => {
      checkAuth();
    }, 5 * 60 * 1000); // 5 minutes

    return () => clearInterval(interval);
  }, [checkAuth]);

  // Listen for 401 errors to open login modal
  useEffect(() => {
    const handleUnauthorized = () => {
      setIsLoginModalOpen(true);
    };

    window.addEventListener("auth:unauthorized", handleUnauthorized);

    return () => {
      window.removeEventListener("auth:unauthorized", handleUnauthorized);
    };
  }, []);

  const handleLoginClick = () => {
    setIsLoginModalOpen(true);
    setIsRegisterModalOpen(false);
  };

  const handleRegisterClick = () => {
    setIsRegisterModalOpen(true);
    setIsLoginModalOpen(false);
  };

  const handleLoginClose = () => {
    setIsLoginModalOpen(false);
  };

  const handleRegisterClose = () => {
    setIsRegisterModalOpen(false);
  };

  const handleLogout = () => {
    // Logout is handled by the Header component via logoutUser
    // This is just a callback for any additional cleanup if needed
  };

  return (
    <>
      <Header
        onLoginClick={handleLoginClick}
        onRegisterClick={handleRegisterClick}
        onLogoutClick={handleLogout}
      />
      {children}
      <LoginModal
        isOpen={isLoginModalOpen}
        onClose={handleLoginClose}
        onRegisterClick={handleRegisterClick}
      />
      <RegisterModal
        isOpen={isRegisterModalOpen}
        onClose={handleRegisterClose}
        onLoginClick={handleLoginClick}
      />
    </>
  );
}

