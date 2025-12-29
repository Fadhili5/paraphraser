import { useAuthStore } from '@/store/authStore';
import { useEffect } from 'react';

/**
 * Custom hook to access auth state and functions
 * 
 * @example
 * ```tsx
 * const { isAuthenticated, token, login, logout } = useAuth();
 * ```
 */
export const useAuth = () => {
  const { token, isAuthenticated, login, logout, checkAuth } = useAuthStore();

  // Check auth state on mount and when storage changes
  useEffect(() => {
    // Initial check
    checkAuth();

    // Listen to storage changes (e.g., from other tabs)
    const handleStorageChange = (e: StorageEvent) => {
      if (e.key === 'auth_token' || e.key === 'auth-storage') {
        checkAuth();
      }
    };

    // Listen to login/logout events from API functions
    const handleLogin = (e: Event) => {
      const customEvent = e as CustomEvent<{ token: string }>;
      if (customEvent.detail?.token) {
        login(customEvent.detail.token);
      }
    };

    const handleLogout = () => {
      logout();
    };

    window.addEventListener('storage', handleStorageChange);
    window.addEventListener('auth:login', handleLogin);
    window.addEventListener('auth:logout', handleLogout);

    return () => {
      window.removeEventListener('storage', handleStorageChange);
      window.removeEventListener('auth:login', handleLogin);
      window.removeEventListener('auth:logout', handleLogout);
    };
  }, [checkAuth, logout]);

  return {
    token,
    isAuthenticated,
    login,
    logout,
    checkAuth,
  };
};

