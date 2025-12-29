import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import { setToken, removeToken, getToken } from '@/lib/api';

// Token expiration: 24 hours (1440 minutes) from backend config
const TOKEN_EXPIRATION_HOURS = 24;

interface AuthState {
  token: string | null;
  isAuthenticated: boolean;
  login: (token: string) => void;
  logout: () => void;
  checkAuth: () => void;
}

/**
 * Decode JWT token without verification (client-side only for expiration check)
 * Note: This doesn't verify the signature, only decodes the payload
 */
const decodeTokenPayload = (token: string): { exp?: number; user_id?: string } | null => {
  try {
    const base64Url = token.split('.')[1];
    if (!base64Url) return null;
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(
      atob(base64)
        .split('')
        .map((c) => '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2))
        .join('')
    );
    return JSON.parse(jsonPayload);
  } catch (error) {
    return null;
  }
};

/**
 * Check if token is expired
 */
const isTokenExpired = (token: string): boolean => {
  const payload = decodeTokenPayload(token);
  if (!payload || !payload.exp) return true;
  
  // exp is in seconds, Date.now() is in milliseconds
  const expirationTime = payload.exp * 1000;
  const currentTime = Date.now();
  
  return currentTime >= expirationTime;
};

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => {
      // Listen to login/logout events from API functions
      if (typeof window !== 'undefined') {
        const handleLogin = (e: Event) => {
          const customEvent = e as CustomEvent<{ token: string }>;
          if (customEvent.detail?.token) {
            get().login(customEvent.detail.token);
          }
        };

        const handleLogout = () => {
          get().logout();
        };

        window.addEventListener('auth:login', handleLogin);
        window.addEventListener('auth:logout', handleLogout);
      }

      return {
        token: null,
        isAuthenticated: false,

        login: (token: string) => {
          // Store token in localStorage via API helper
          setToken(token);
          set({ token, isAuthenticated: true });
        },

        logout: () => {
          // Remove token from localStorage via API helper
          removeToken();
          set({ token: null, isAuthenticated: false });
        },

        checkAuth: () => {
          // Check if token exists and is not expired
          const token = getToken();
          if (!token) {
            set({ token: null, isAuthenticated: false });
            return;
          }

          // Check if token is expired
          if (isTokenExpired(token)) {
            // Token expired, clear it
            removeToken();
            set({ token: null, isAuthenticated: false });
            return;
          }

          // Token is valid
          set({ token, isAuthenticated: true });
        },
      };
    },
    {
      name: 'auth-storage',
      storage: createJSONStorage(() => localStorage),
      // Only persist token, isAuthenticated is computed
      partialize: (state) => ({ token: state.token }),
      // On rehydrate, check if token is still valid
      onRehydrateStorage: () => (state) => {
        if (state) {
          state.checkAuth();
        }
      },
    }
  )
);

// Initialize auth state on mount
if (typeof window !== 'undefined') {
  useAuthStore.getState().checkAuth();
}

