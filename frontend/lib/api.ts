import axios, { AxiosInstance, AxiosError, InternalAxiosRequestConfig, AxiosResponse } from 'axios';
import type {
  UserRegisterRequest,
  UserRegisterResponse,
  UserLoginRequest,
  TokenResponse,
  ParaphraseRequest,
  ParaphraseResponse,
  ApiErrorResponse,
} from './types';


const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Create axios instance
const apiClient: AxiosInstance = axios.create({
  baseURL: API_URL,
  timeout: 180000, // 30 seconds
  headers: {
    'Content-Type': 'application/json',
  },
});

// Token storage key
const TOKEN_STORAGE_KEY = 'auth_token';

// Helper functions for token management
export const getToken = (): string | null => {
  if (typeof window === 'undefined') return null;
  return localStorage.getItem(TOKEN_STORAGE_KEY);
};

export const setToken = (token: string): void => {
  if (typeof window === 'undefined') return;
  localStorage.setItem(TOKEN_STORAGE_KEY, token);
};

export const removeToken = (): void => {
  if (typeof window === 'undefined') return;
  localStorage.removeItem(TOKEN_STORAGE_KEY);
};

// Request interceptor: Add auth token to headers
apiClient.interceptors.request.use(
  (config: InternalAxiosRequestConfig) => {
    const token = getToken();
    if (token && config.headers) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error: AxiosError) => {
    return Promise.reject(error);
  }
);

// Response interceptor: Handle errors globally
apiClient.interceptors.response.use(
  (response: AxiosResponse) => {
    return response;
  },
  (error: AxiosError<ApiErrorResponse>) => {
    // Handle 401 Unauthorized - token expired or invalid
    if (error.response?.status === 401) {
      removeToken();
      // Dispatch events for auth store and UI to handle
      if (typeof window !== 'undefined') {
        // Dispatch logout event for auth store
        window.dispatchEvent(new CustomEvent('auth:logout'));
        // Dispatch unauthorized event to open login modal
        // Only dispatch if not already on a login/register page
        window.dispatchEvent(new CustomEvent('auth:unauthorized'));
      }
    }

    // Handle 429 Rate Limit
    if (error.response?.status === 429) {
      // Rate limit error will be handled by the calling component
      // Error detail contains: "Rate limit exceeded. Try again in {ttl}s."
    }

    return Promise.reject(error);
  }
);

// API Functions

/**
 * Register a new user
 * POST /users/v1/users/register
 */
export const registerUser = async (
  data: UserRegisterRequest
): Promise<UserRegisterResponse> => {
  const response = await apiClient.post<UserRegisterResponse>(
    '/v1/users/register',
    data
  );
  return response.data;
};

/**
 * Login user
 * POST /users/v1/users/login
 */
export const loginUser = async (
  data: UserLoginRequest
): Promise<TokenResponse> => {
  const response = await apiClient.post<TokenResponse>(
    '/v1/users/login',
    data
  );
  
  // Store token after successful login
  if (response.data.access_token) {
    setToken(response.data.access_token);
    // Dispatch event for auth store to update
    if (typeof window !== 'undefined') {
      window.dispatchEvent(new CustomEvent('auth:login', { 
        detail: { token: response.data.access_token } 
      }));
    }
  }
  
  return response.data;
};

/**
 * Logout user (removes token)
 */
export const logoutUser = (): void => {
  removeToken();
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('auth:logout'));
  }
};

/**
 * Paraphrase text
 * POST /v1/paraphrase
 * Works for both authenticated and anonymous users
 */
export const paraphraseText = async (
  data: ParaphraseRequest
): Promise<ParaphraseResponse> => {
  const response = await apiClient.post<ParaphraseResponse>(
    '/v1/paraphrase',
    data
  );
  return response.data;
};

export default apiClient;

