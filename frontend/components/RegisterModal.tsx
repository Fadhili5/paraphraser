"use client";

import { useState, useEffect } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import { X, Mail, Lock, User, Phone, Loader2, Check, XCircle } from "lucide-react";
import { registerUser } from "@/lib/api";
import { loginUser } from "@/lib/api";
import { useAuth } from "@/hooks/useAuth";
import type { ApiErrorResponse } from "@/lib/types";

// Password strength requirements (matching backend)
const PASSWORD_REQUIREMENTS = {
  minLength: 8,
  hasDigit: /\d/,
  hasUppercase: /[A-Z]/,
  hasLowercase: /[a-z]/,
  hasSpecial: /[!@#$%^&*()[\]?"'<>]/,
};

// Zod schema for form validation
const registerSchema = z.object({
  username: z
    .string()
    .min(1, "Username is required")
    .min(3, "Username must be at least 3 characters")
    .max(50, "Username must be less than 50 characters"),
  email: z
    .string()
    .min(1, "Email is required")
    .email("Please enter a valid email address"),
  password: z
    .string()
    .min(1, "Password is required")
    .min(8, "Password must be at least 8 characters")
    .refine((val) => PASSWORD_REQUIREMENTS.hasDigit.test(val), {
      message: "Password must contain at least one digit",
    })
    .refine((val) => PASSWORD_REQUIREMENTS.hasUppercase.test(val), {
      message: "Password must contain at least one uppercase letter",
    })
    .refine((val) => PASSWORD_REQUIREMENTS.hasLowercase.test(val), {
      message: "Password must contain at least one lowercase letter",
    })
    .refine((val) => PASSWORD_REQUIREMENTS.hasSpecial.test(val), {
      message: "Password must contain at least one special character",
    }),
  phone_number: z
    .string()
    .min(1, "Phone number is required")
    .regex(/^\+?[\d\s-()]+$/, "Please enter a valid phone number"),
});

type RegisterFormData = z.infer<typeof registerSchema>;

interface RegisterModalProps {
  isOpen: boolean;
  onClose: () => void;
  onLoginClick?: () => void;
}

// Password strength checker
const checkPasswordStrength = (password: string) => {
  return {
    minLength: password.length >= PASSWORD_REQUIREMENTS.minLength,
    hasDigit: PASSWORD_REQUIREMENTS.hasDigit.test(password),
    hasUppercase: PASSWORD_REQUIREMENTS.hasUppercase.test(password),
    hasLowercase: PASSWORD_REQUIREMENTS.hasLowercase.test(password),
    hasSpecial: PASSWORD_REQUIREMENTS.hasSpecial.test(password),
  };
};

export default function RegisterModal({
  isOpen,
  onClose,
  onLoginClick,
}: RegisterModalProps) {
  const [error, setError] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [password, setPassword] = useState("");
  const [passwordStrength, setPasswordStrength] = useState(
    checkPasswordStrength("")
  );
  const { login } = useAuth();

  const {
    register,
    handleSubmit,
    formState: { errors },
    reset,
    watch,
  } = useForm<RegisterFormData>({
    resolver: zodResolver(registerSchema),
  });

  // Watch password field for strength indicator
  const watchedPassword = watch("password", "");

  useEffect(() => {
    setPassword(watchedPassword || "");
    setPasswordStrength(checkPasswordStrength(watchedPassword || ""));
  }, [watchedPassword]);

  const onSubmit = async (data: RegisterFormData) => {
    setError(null);
    setIsLoading(true);

    try {
      // Register user
      const response = await registerUser({
        username: data.username,
        email: data.email,
        password: data.password,
        phone_number: data.phone_number,
      });

      // Auto-login after successful registration
      try {
        const loginResponse = await loginUser({
          email: data.email,
          password: data.password,
        });

        // Token is automatically stored by loginUser and auth store
        // Update auth store state
        if (loginResponse.access_token) {
          login(loginResponse.access_token);
        }

        // Close modal and reset form on success
        reset();
        onClose();
      } catch (loginErr: any) {
        // Registration succeeded but login failed - show success message and redirect to login
        setError(
          "Registration successful! Please login with your credentials."
        );
        setTimeout(() => {
          reset();
          onClose();
          onLoginClick?.();
        }, 2000);
      }
    } catch (err: any) {
      // Handle API errors
      if (err.response?.status === 400) {
        const errorDetail = err.response.data?.detail || "";
        if (errorDetail.includes("already exists")) {
          setError("User with this email or username already exists.");
        } else if (errorDetail.includes("too weak") || errorDetail.includes("Password")) {
          setError("Password is too weak. Please check the requirements below.");
        } else {
          setError(errorDetail || "Invalid input. Please check your information.");
        }
      } else if (err.response?.data?.detail) {
        setError(err.response.data.detail);
      } else {
        setError("An error occurred. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleClose = () => {
    if (!isLoading) {
      reset();
      setError(null);
      setPassword("");
      setPasswordStrength(checkPasswordStrength(""));
      onClose();
    }
  };

  const handleBackdropClick = (e: React.MouseEvent<HTMLDivElement>) => {
    if (e.target === e.currentTarget && !isLoading) {
      handleClose();
    }
  };

  if (!isOpen) return null;

  const allRequirementsMet = Object.values(passwordStrength).every((v) => v);

  return (
    <div
      className="fixed inset-0 z-50 flex items-center justify-center bg-black/50 backdrop-blur-sm overflow-y-auto"
      onClick={handleBackdropClick}
    >
      <div className="relative w-full max-w-md mx-4 my-8 bg-white rounded-lg shadow-xl dark:bg-gray-800">
        {/* Close button */}
        <button
          onClick={handleClose}
          disabled={isLoading}
          className="absolute top-4 right-4 text-gray-400 hover:text-gray-600 dark:hover:text-gray-300 disabled:opacity-50 disabled:cursor-not-allowed transition-colors z-10"
          aria-label="Close modal"
        >
          <X size={24} />
        </button>

        {/* Modal content */}
        <div className="p-6">
          <h2 className="text-2xl font-bold text-gray-900 dark:text-white mb-2">
            Create Account
          </h2>
          <p className="text-sm text-gray-600 dark:text-gray-400 mb-6">
            Sign up to get started with AI Paraphraser
          </p>

          {/* Error message */}
          {error && (
            <div className="mb-4 p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
              <p className="text-sm text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}

          {/* Register form */}
          <form onSubmit={handleSubmit(onSubmit)} className="space-y-4">
            {/* Username field */}
            <div>
              <label
                htmlFor="username"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Username
              </label>
              <div className="relative">
                <User
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                  size={20}
                />
                <input
                  {...register("username")}
                  type="text"
                  id="username"
                  autoComplete="username"
                  disabled={isLoading}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                  placeholder="Enter your username"
                />
              </div>
              {errors.username && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.username.message}
                </p>
              )}
            </div>

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
                  autoComplete="new-password"
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

              {/* Password strength indicator */}
              {password && (
                <div className="mt-2 p-3 bg-gray-50 dark:bg-gray-900/50 rounded-md border border-gray-200 dark:border-gray-700">
                  <p className="text-xs font-medium text-gray-700 dark:text-gray-300 mb-2">
                    Password Requirements:
                  </p>
                  <ul className="space-y-1 text-xs">
                    <li
                      className={`flex items-center gap-2 ${
                        passwordStrength.minLength
                          ? "text-green-600 dark:text-green-400"
                          : "text-gray-500 dark:text-gray-400"
                      }`}
                    >
                      {passwordStrength.minLength ? (
                        <Check size={14} />
                      ) : (
                        <XCircle size={14} />
                      )}
                      At least 8 characters
                    </li>
                    <li
                      className={`flex items-center gap-2 ${
                        passwordStrength.hasDigit
                          ? "text-green-600 dark:text-green-400"
                          : "text-gray-500 dark:text-gray-400"
                      }`}
                    >
                      {passwordStrength.hasDigit ? (
                        <Check size={14} />
                      ) : (
                        <XCircle size={14} />
                      )}
                      At least one digit
                    </li>
                    <li
                      className={`flex items-center gap-2 ${
                        passwordStrength.hasUppercase
                          ? "text-green-600 dark:text-green-400"
                          : "text-gray-500 dark:text-gray-400"
                      }`}
                    >
                      {passwordStrength.hasUppercase ? (
                        <Check size={14} />
                      ) : (
                        <XCircle size={14} />
                      )}
                      At least one uppercase letter
                    </li>
                    <li
                      className={`flex items-center gap-2 ${
                        passwordStrength.hasLowercase
                          ? "text-green-600 dark:text-green-400"
                          : "text-gray-500 dark:text-gray-400"
                      }`}
                    >
                      {passwordStrength.hasLowercase ? (
                        <Check size={14} />
                      ) : (
                        <XCircle size={14} />
                      )}
                      At least one lowercase letter
                    </li>
                    <li
                      className={`flex items-center gap-2 ${
                        passwordStrength.hasSpecial
                          ? "text-green-600 dark:text-green-400"
                          : "text-gray-500 dark:text-gray-400"
                      }`}
                    >
                      {passwordStrength.hasSpecial ? (
                        <Check size={14} />
                      ) : (
                        <XCircle size={14} />
                      )}
                      At least one special character (!@#$%^&*...)
                    </li>
                  </ul>
                </div>
              )}
            </div>

            {/* Phone number field */}
            <div>
              <label
                htmlFor="phone_number"
                className="block text-sm font-medium text-gray-700 dark:text-gray-300 mb-2"
              >
                Phone Number
              </label>
              <div className="relative">
                <Phone
                  className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400"
                  size={20}
                />
                <input
                  {...register("phone_number")}
                  type="tel"
                  id="phone_number"
                  autoComplete="tel"
                  disabled={isLoading}
                  className="w-full pl-10 pr-4 py-2 border border-gray-300 dark:border-gray-600 rounded-md focus:ring-2 focus:ring-teal-500 focus:border-teal-500 dark:bg-gray-700 dark:text-white disabled:opacity-50 disabled:cursor-not-allowed"
                  placeholder="Enter your phone number"
                />
              </div>
              {errors.phone_number && (
                <p className="mt-1 text-sm text-red-600 dark:text-red-400">
                  {errors.phone_number.message}
                </p>
              )}
            </div>

            {/* Submit button */}
            <button
              type="submit"
              disabled={isLoading || (password.length > 0 && !allRequirementsMet)}
              className="w-full py-2 px-4 bg-teal-600 hover:bg-teal-700 text-white font-medium rounded-md transition-colors disabled:opacity-50 disabled:cursor-not-allowed flex items-center justify-center gap-2"
            >
              {isLoading ? (
                <>
                  <Loader2 className="animate-spin" size={20} />
                  <span>Creating account...</span>
                </>
              ) : (
                "Sign Up"
              )}
            </button>
          </form>

          {/* Login link */}
          <div className="mt-6 text-center">
            <p className="text-sm text-gray-600 dark:text-gray-400">
              Already have an account?{" "}
              <button
                onClick={() => {
                  handleClose();
                  onLoginClick?.();
                }}
                disabled={isLoading}
                className="text-teal-600 hover:text-teal-700 dark:text-teal-400 dark:hover:text-teal-300 font-medium disabled:opacity-50 disabled:cursor-not-allowed"
              >
                Sign in
              </button>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

