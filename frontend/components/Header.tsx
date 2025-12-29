"use client";

import { useState, useEffect } from "react";
import { Menu, X, Globe, User, LogOut, History } from "lucide-react";
import { getToken } from "@/lib/api";

interface HeaderProps {
  onLoginClick?: () => void;
  onRegisterClick?: () => void;
  onLogoutClick?: () => void;
}

// Supported languages
const LANGUAGES = [
  { code: "en", name: "English" },
  { code: "es", name: "Español" },
  { code: "fr", name: "Français" },
  { code: "de", name: "Deutsch" },
  { code: "it", name: "Italiano" },
  { code: "pt", name: "Português" },
] as const;

export default function Header({
  onLoginClick,
  onRegisterClick,
  onLogoutClick,
}: HeaderProps) {
  const [isMobileMenuOpen, setIsMobileMenuOpen] = useState(false);
  const [isLanguageMenuOpen, setIsLanguageMenuOpen] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState("en");
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  // Check authentication status
  useEffect(() => {
    const checkAuth = () => {
      const token = getToken();
      setIsAuthenticated(!!token);
    };
    checkAuth();
    // Listen for storage changes (e.g., when token is set/removed)
    window.addEventListener("storage", checkAuth);
    // Check periodically (for same-tab updates)
    const interval = setInterval(checkAuth, 1000);
    return () => {
      window.removeEventListener("storage", checkAuth);
      clearInterval(interval);
    };
  }, []);

  const handleLanguageSelect = (code: string) => {
    setSelectedLanguage(code);
    setIsLanguageMenuOpen(false);
    // TODO: Implement language change functionality
  };

  const handleLogout = () => {
    if (onLogoutClick) {
      onLogoutClick();
    }
    setIsAuthenticated(false);
    setIsMobileMenuOpen(false);
  };

  const currentLanguage = LANGUAGES.find((lang) => lang.code === selectedLanguage);

  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo/Brand */}
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold text-teal-600">AI Paraphraser</h1>
        </div>

        {/* Desktop Navigation */}
        <nav className="hidden md:flex items-center gap-6">
          <a
            href="#"
            className="text-gray-600 hover:text-teal-600 transition-colors"
          >
            Home
          </a>
          {isAuthenticated && (
            <button
              className="flex items-center gap-2 text-gray-600 hover:text-teal-600 transition-colors"
              aria-label="View history"
            >
              <History className="h-4 w-4" />
              <span>History</span>
            </button>
          )}
        </nav>

        {/* Desktop Right Side: Language & Auth */}
        <div className="hidden md:flex items-center gap-4">
          {/* Language Selector */}
          <div className="relative">
            <button
              type="button"
              onClick={() => setIsLanguageMenuOpen(!isLanguageMenuOpen)}
              className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-teal-600 transition-colors rounded-md hover:bg-gray-50"
              aria-label="Select language"
              aria-expanded={isLanguageMenuOpen}
            >
              <Globe className="h-4 w-4" />
              <span className="text-sm">{currentLanguage?.name}</span>
            </button>

            {/* Language Dropdown */}
            {isLanguageMenuOpen && (
              <>
                <div
                  className="fixed inset-0 z-10"
                  onClick={() => setIsLanguageMenuOpen(false)}
                />
                <div className="absolute right-0 mt-2 w-48 bg-white border border-gray-200 rounded-lg shadow-lg z-20">
                  <div className="py-1">
                    {LANGUAGES.map((lang) => (
                      <button
                        key={lang.code}
                        type="button"
                        onClick={() => handleLanguageSelect(lang.code)}
                        className={`w-full text-left px-4 py-2 text-sm transition-colors ${
                          selectedLanguage === lang.code
                            ? "bg-teal-50 text-teal-600 font-medium"
                            : "text-gray-700 hover:bg-gray-50"
                        }`}
                      >
                        {lang.name}
                      </button>
                    ))}
                  </div>
                </div>
              </>
            )}
          </div>

          {/* Auth Buttons / User Menu */}
          {isAuthenticated ? (
            <div className="flex items-center gap-3">
              <button
                type="button"
                className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-teal-600 transition-colors rounded-md hover:bg-gray-50"
                aria-label="User menu"
              >
                <User className="h-4 w-4" />
                <span className="text-sm">Profile</span>
              </button>
              <button
                type="button"
                onClick={handleLogout}
                className="flex items-center gap-2 px-3 py-2 text-gray-600 hover:text-red-600 transition-colors rounded-md hover:bg-gray-50"
                aria-label="Logout"
              >
                <LogOut className="h-4 w-4" />
                <span className="text-sm">Logout</span>
              </button>
            </div>
          ) : (
            <div className="flex items-center gap-2">
              <button
                type="button"
                onClick={onLoginClick}
                className="px-4 py-2 text-sm text-gray-700 hover:text-teal-600 transition-colors"
              >
                Login
              </button>
              <button
                type="button"
                onClick={onRegisterClick}
                className="px-4 py-2 text-sm font-medium text-white bg-teal-600 rounded-md hover:bg-teal-700 transition-colors"
              >
                Sign Up
              </button>
            </div>
          )}
        </div>

        {/* Mobile Menu Button */}
        <button
          type="button"
          onClick={() => setIsMobileMenuOpen(!isMobileMenuOpen)}
          className="md:hidden p-2 text-gray-600 hover:text-teal-600 transition-colors"
          aria-label="Toggle mobile menu"
          aria-expanded={isMobileMenuOpen}
        >
          {isMobileMenuOpen ? (
            <X className="h-6 w-6" />
          ) : (
            <Menu className="h-6 w-6" />
          )}
        </button>
      </div>

      {/* Mobile Menu */}
      {isMobileMenuOpen && (
        <div className="md:hidden border-t border-gray-200 bg-white">
          <div className="container mx-auto px-4 py-4 space-y-3">
            {/* Mobile Navigation Links */}
            <a
              href="#"
              className="block py-2 text-gray-600 hover:text-teal-600 transition-colors"
              onClick={() => setIsMobileMenuOpen(false)}
            >
              Home
            </a>
            {isAuthenticated && (
              <button
                type="button"
                className="flex items-center gap-2 w-full py-2 text-left text-gray-600 hover:text-teal-600 transition-colors"
                onClick={() => setIsMobileMenuOpen(false)}
              >
                <History className="h-4 w-4" />
                <span>History</span>
              </button>
            )}

            {/* Mobile Language Selector */}
            <div className="pt-3 border-t border-gray-200">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">Language</span>
                <Globe className="h-4 w-4 text-gray-600" />
              </div>
              <div className="grid grid-cols-2 gap-2">
                {LANGUAGES.map((lang) => (
                  <button
                    key={lang.code}
                    type="button"
                    onClick={() => handleLanguageSelect(lang.code)}
                    className={`px-3 py-2 text-sm text-left rounded-md transition-colors ${
                      selectedLanguage === lang.code
                        ? "bg-teal-50 text-teal-600 font-medium"
                        : "text-gray-700 hover:bg-gray-50"
                    }`}
                  >
                    {lang.name}
                  </button>
                ))}
              </div>
            </div>

            {/* Mobile Auth Buttons */}
            <div className="pt-3 border-t border-gray-200 space-y-2">
              {isAuthenticated ? (
                <>
                  <button
                    type="button"
                    className="flex items-center gap-2 w-full py-2 text-left text-gray-600 hover:text-teal-600 transition-colors"
                    onClick={() => setIsMobileMenuOpen(false)}
                  >
                    <User className="h-4 w-4" />
                    <span>Profile</span>
                  </button>
                  <button
                    type="button"
                    onClick={handleLogout}
                    className="flex items-center gap-2 w-full py-2 text-left text-red-600 hover:text-red-700 transition-colors"
                  >
                    <LogOut className="h-4 w-4" />
                    <span>Logout</span>
                  </button>
                </>
              ) : (
                <>
                  <button
                    type="button"
                    onClick={() => {
                      if (onLoginClick) onLoginClick();
                      setIsMobileMenuOpen(false);
                    }}
                    className="w-full py-2 text-sm text-gray-700 hover:text-teal-600 transition-colors"
                  >
                    Login
                  </button>
                  <button
                    type="button"
                    onClick={() => {
                      if (onRegisterClick) onRegisterClick();
                      setIsMobileMenuOpen(false);
                    }}
                    className="w-full py-2 text-sm font-medium text-white bg-teal-600 rounded-md hover:bg-teal-700 transition-colors"
                  >
                    Sign Up
                  </button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </header>
  );
}

