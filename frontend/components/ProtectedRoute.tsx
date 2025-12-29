"use client";

import { useEffect, useState } from "react";
import { useAuth } from "@/hooks/useAuth";

interface ProtectedRouteProps {
  children: React.ReactNode;
  fallback?: React.ReactNode;
  redirectToLogin?: boolean;
}

/**
 * ProtectedRoute component that ensures user is authenticated
 * If not authenticated, shows fallback or triggers login modal
 * 
 * @example
 * ```tsx
 * <ProtectedRoute>
 *   <HistoryPage />
 * </ProtectedRoute>
 * ```
 */
export default function ProtectedRoute({
  children,
  fallback,
  redirectToLogin = true,
}: ProtectedRouteProps) {
  const { isAuthenticated, checkAuth } = useAuth();
  const [isChecking, setIsChecking] = useState(true);

  useEffect(() => {
    // Check auth state on mount
    checkAuth();
    setIsChecking(false);
  }, [checkAuth]);

  // Show loading state while checking
  if (isChecking) {
    return (
      <div className="flex items-center justify-center min-h-[400px]">
        <div className="text-gray-600">Loading...</div>
      </div>
    );
  }

  // Trigger login modal if not authenticated and redirectToLogin is true
  useEffect(() => {
    if (!isAuthenticated && redirectToLogin && !isChecking) {
      window.dispatchEvent(new CustomEvent("auth:unauthorized"));
    }
  }, [isAuthenticated, redirectToLogin, isChecking]);

  // If not authenticated, show fallback
  if (!isAuthenticated) {
    return (
      fallback || (
        <div className="flex flex-col items-center justify-center min-h-[400px] p-4">
          <h2 className="text-xl font-semibold text-gray-900 mb-2">
            Authentication Required
          </h2>
          <p className="text-gray-600 text-center mb-4">
            Please log in to access this page.
          </p>
        </div>
      )
    );
  }

  // User is authenticated, render children
  return <>{children}</>;
}

