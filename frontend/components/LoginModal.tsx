"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { X, Mail, Lock, Loader2 } from "lucide-react";
import { useGoogleReCaptcha } from "react-google-recaptcha-v3";
import { loginUser } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { ApiErrorResponse } from "@/lib/types";

// Zod schema for form validation
const loginSchema = z.object({
  email: z
    .string()
    .min(1, "Email is required")
    .email("Please enter a valid email address"),
  password: z
    .string()
    .min(1, "Password is required")
    .min(6, "Password must be at least 6 characters"),
});

type LoginFormData = z.infer<typeof loginSchema>;

interface LoginModalProps {
  isOpen: boolean;
  onClose: () => void;
  onRegisterClick?: () => void;
}

export default function LoginModal({
  isOpen,
  onClose,
  onRegisterClick,
}: LoginModalProps) {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const { login } = useAuth();
  const { executeRecaptcha } = useGoogleReCaptcha();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
  } = useForm<LoginFormData>({
    resolver: zodResolver(loginSchema),
  });

  const onSubmit = async (data: LoginFormData) => {
    setError(null);
    setIsLoading(true);

    try {
      // Generate reCAPTCHA token
      let recaptchaToken = "";
      if (executeRecaptcha) {
        try {
          recaptchaToken = await executeRecaptcha("login");
        } catch (recaptchaError) {
          console.error("reCAPTCHA error:", recaptchaError);
          setError("reCAPTCHA verification failed. Please try again.");
          setIsLoading(false);
          return;
        }
      } else {
        // If reCAPTCHA is not available, show warning but continue
        console.warn("reCAPTCHA is not available. Login may fail if backend requires it.");
      }

      const response = await loginUser({
        email: data.email,
        password: data.password,
        recaptcha_token: recaptchaToken,
      });

      // Token is automatically stored by loginUser and auth store
      // Update auth store state
      if (response.access_token) {
        login(response.access_token);
      }

      // Close modal and reset form on success
      reset();
      onClose();
    } catch (err: any) {
      // Log the full error for debugging
      console.error("Login error:", err);
      
      // Safely access error properties
      const errorResponse = err?.response;
      const errorMessage = err?.message || String(err);
      
      console.error("Error response:", errorResponse);
      console.error("Error message:", errorMessage);
      
      // Handle network errors (no response)
      if (!errorResponse) {
        const errorCode = err?.code;
        if (errorCode === 'ECONNABORTED' || errorMessage?.includes('timeout')) {
          setError("Request timed out. Please check your connection and try again.");
        } else if (errorMessage?.includes('Network Error') || errorCode === 'ERR_NETWORK') {
          setError("Network error. Please check if the backend server is running.");
        } else if (errorMessage?.includes('CORS')) {
          setError("CORS error. The backend server needs to be configured to allow requests from this origin.");
        } else {
          setError(`Connection error: ${errorMessage || "Unable to reach the server. Please check if the backend is running."}`);
        }
      }
      // Handle API errors with response
      else if (errorResponse?.status === 400) {
        const errorDetail = errorResponse?.data?.detail || "Invalid request. Please check your input.";
        setError(errorDetail);
      } else if (errorResponse?.status === 401) {
        setError("Invalid credentials. Please check your email and password.");
      } else if (errorResponse?.status === 403) {
        // reCAPTCHA verification failed or bot detected
        const errorDetail = errorResponse?.data?.detail || "reCAPTCHA verification failed";
        if (errorDetail.includes("Bot Detected")) {
          setError("Bot detected. Please try again.");
        } else {
          setError("reCAPTCHA verification failed. Please try again.");
        }
      } else if (errorResponse?.status === 503) {
        // reCAPTCHA service unavailable
        setError("reCAPTCHA verification services are currently unavailable. Please try again later.");
      } else if (errorResponse?.data?.detail) {
        setError(errorResponse.data.detail);
      } else if (errorResponse?.status) {
        setError(`Server error (${errorResponse.status}). Please try again.`);
      } else {
        setError(`An error occurred: ${errorMessage || "Please try again."}`);
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      reset();
      setError(null);
      onClose();
    }
  };

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget && !isLoading) {
      handleClose();
    }
  };

  if (!isOpen) return null;

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm"
      onClick={handleBackdropClick}
    >
      <div className="relative w-full max-w-md mx-4 bg-white rounded-lg shadow-xl dark:bg-gray-800">
        {/* Close button */}
        <button
          onClick={handleClose}
          disabled={isLoading}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
          aria-label="Close modal"
        >
          <X size={24} />
        </button>

        {/* Modal content */}
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Login
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
            Sign in to your account to continue
          </p>

          {/* Error message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Login form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Email field */}
            <div>
              <label
                htmlFor="email"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Email
              </label>
              <div className="relative">
                <Mail
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                  size={20}
                />
                <input
                  {...register("email")}
                  type="email"
                  id="email"
                  autoComplete="email"
                  disabled={isLoading}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                  placeholder="Enter your email"
                />
              </div>
              {errors.email && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.email.message}
                </p>
              )}
            </div>

            {/* Password field */}
            <div>
              <label
                htmlFor="password"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Password
              </label>
              <div className="relative">
                <Lock
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                  size={20}
                />
                <input
                  {...register("password")}
                  type="password"
                  id="password"
                  autoComplete="current-password"
                  disabled={isLoading}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                  placeholder="Enter your password"
                />
              </div>
              {errors.password && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.password.message}
                </p>
              )}
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading}
              className="w-full py-2 px-4 bg-teal-600 hover:bg-teal-700 text-white font-medium rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  <span>Logging in...</span>
                </>
              ) : (
                "Login"
              )}
            </button>
          </form>

          {/* Register link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Don't have an account?{" "}
              <button
                onClick={() => {
                  handleClose();
                  onRegisterClick?.();
                }}
                disabled={isLoading}
                className="text-teal-600 hover:text-teal-700 dark:text-teal-400 dark:hover:text-teal-300 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Sign up
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

