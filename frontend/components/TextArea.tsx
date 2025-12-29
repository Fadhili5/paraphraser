"use client";

import { Upload, Mic, FilePlus, Languages } from "lucide-react";
import { useRef } from "react";

interface TextAreaProps {
  label: string;
  value: string;
  onChange: (value: string) => void;
  placeholder?: string;
  readOnly?: boolean;
  onAction?: () => void;
  isLoading?: boolean;
  maxLength?: number;
}

export default function TextArea({
  label,
  value,
  onChange,
  placeholder = "Enter your text here...",
  readOnly = false,
  onAction,
  isLoading = false,
  maxLength,
}: TextAreaProps) {
  const textareaRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleFileUpload = () => {
    fileInputRef.current?.click();
  };

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Only handle .txt files for now (Task 19 will add more formats)
    if (file.type === "text/plain" || file.name.endsWith(".txt")) {
      const reader = new FileReader();
      reader.onload = (event) => {
        const text = event.target?.result as string;
        if (text) {
          onChange(text);
        }
      };
      reader.readAsText(file);
    } else {
      alert("Please upload a .txt file");
    }
  };

  const handleMicClick = () => {
    // Placeholder for voice input functionality
    alert("Voice input coming soon");
  };

  const handleFilePlusClick = () => {
    // Placeholder for additional file operations
    alert("File operations coming soon");
  };

  const handleLanguageClick = () => {
    // Placeholder for language selection
    alert("Language selection coming soon");
  };

  const characterCount = value.length;
  const showCharacterCount = maxLength !== undefined;

  return (
    <div className="flex flex-col h-full">
      {/* Label */}
      <div className="flex items-center justify-between mb-2">
        <label className="text-sm font-medium text-gray-700">{label}</label>
        {showCharacterCount && (
          <span
            className={`text-xs ${
              characterCount > maxLength! * 0.9
                ? "text-red-500"
                : "text-gray-500"
            }`}
          >
            {characterCount} / {maxLength}
          </span>
        )}
      </div>

      {/* Toolbar */}
      <div className="flex items-center gap-2 p-2 border border-gray-200 rounded-t-lg bg-gray-50">
        <button
          type="button"
          onClick={handleFileUpload}
          className="p-1.5 text-gray-600 hover:text-teal-600 hover:bg-teal-50 rounded transition-colors"
          aria-label="Upload file"
          disabled={readOnly || isLoading}
        >
          <Upload className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={handleMicClick}
          className="p-1.5 text-gray-600 hover:text-teal-600 hover:bg-teal-50 rounded transition-colors"
          aria-label="Voice input"
          disabled={readOnly || isLoading}
        >
          <Mic className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={handleFilePlusClick}
          className="p-1.5 text-gray-600 hover:text-teal-600 hover:bg-teal-50 rounded transition-colors"
          aria-label="Add file"
          disabled={readOnly || isLoading}
        >
          <FilePlus className="h-4 w-4" />
        </button>
        <button
          type="button"
          onClick={handleLanguageClick}
          className="p-1.5 text-gray-600 hover:text-teal-600 hover:bg-teal-50 rounded transition-colors"
          aria-label="Select language"
          disabled={readOnly || isLoading}
        >
          <Languages className="h-4 w-4" />
        </button>
        <div className="flex-1" />
        {onAction && (
          <button
            type="button"
            onClick={onAction}
            disabled={isLoading || !value.trim()}
            className="px-4 py-1.5 text-sm font-medium text-white bg-teal-600 rounded hover:bg-teal-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? "Processing..." : "Action"}
          </button>
        )}
      </div>

      {/* TextArea */}
      <div className="relative flex-1 border border-t-0 border-gray-200 rounded-b-lg bg-white">
        <textarea
          ref={textareaRef}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          placeholder={placeholder}
          readOnly={readOnly}
          disabled={isLoading}
          maxLength={maxLength}
          className="w-full h-full p-4 resize-none border-0 rounded-b-lg focus:outline-none focus:ring-2 focus:ring-teal-500 focus:ring-inset disabled:bg-gray-50 disabled:cursor-not-allowed"
          aria-label={label}
        />
        {isLoading && (
          <div className="absolute inset-0 flex items-center justify-center bg-white bg-opacity-75 rounded-b-lg">
            <div className="flex flex-col items-center gap-2">
              <div className="w-8 h-8 border-4 border-teal-200 border-t-teal-600 rounded-full animate-spin" />
              <span className="text-sm text-gray-600">Loading...</span>
            </div>
          </div>
        )}
      </div>

      {/* Hidden file input */}
      <input
        ref={fileInputRef}
        type="file"
        accept=".txt"
        onChange={handleFileChange}
        className="hidden"
        aria-label="File upload"
      />
    </div>
  );
}

