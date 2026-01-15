"use client";

import { useState } from "react";
import TextArea from "@/components/TextArea";
import ModeSelector from "@/components/ModeSelector";
import { paraphraseText } from "@/lib/api";

export default function Home() {
  const [inputText, setInputText] = useState("");
  const [outputText, setOutputText] = useState("");
  const [selectedMode, setSelectedMode] = useState("standard");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleParaphrase = async () => {
    if (!inputText.trim()) return;

    setIsLoading(true);
    setError(null);

    try {
      const response = await paraphraseText({
        text: inputText,
        mode: selectedMode,
      });
      setOutputText(response.paraphrased_text);
    } catch (err: unknown) {
      console.error("Paraphrase failed:", err);
      const errorResponse = (err as { response?: { data?: { detail?: string }; status?: number } })?.response;
      if (errorResponse?.data?.detail) {
        setError(errorResponse.data.detail);
      } else if (errorResponse?.status === 429) {
        setError("Rate limit exceeded. Please try again later.");
      } else {
        setError("Failed to paraphrase text. Please try again.");
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleClear = () => {
    setInputText("");
    setOutputText("");
    setError(null);
  };

  return (
    <div className="flex min-h-[calc(100vh-4rem)] bg-white">
      <div className="w-full max-w-7xl mx-auto px-4 py-6">
        {/* Mode Selector */}
        <div className="mb-6">
          <ModeSelector
            selectedMode={selectedMode}
            onModeChange={setSelectedMode}
          />
        </div>

        {/* Three-Column Layout */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 min-h-[600px] lg:h-[calc(100vh-12rem)]">
          {/* Column 1: Input */}
          <div className="flex flex-col h-full">
            <TextArea
              label="Original Text"
              value={inputText}
              onChange={setInputText}
              placeholder="Enter or paste your text here to paraphrase..."
              onAction={handleParaphrase}
              isLoading={isLoading}
              maxLength={5000}
            />
          </div>

          {/* Column 2: Pro Membership */}
          <div className="flex flex-col h-full min-h-[400px] lg:min-h-0">
            <div className="flex flex-col h-full border border-gray-200 rounded-lg bg-gradient-to-b from-teal-50 to-white p-4 lg:p-6">
              <div className="mb-4">
                <h2 className="text-xl font-bold text-gray-900 mb-2">
                  Pro Membership
                </h2>
                <p className="text-sm text-gray-600">
                  Unlock advanced features and unlimited paraphrasing
                </p>
              </div>

              <div className="flex-1 flex flex-col justify-center space-y-4">
                <div className="space-y-3">
                  <div className="flex items-start gap-2">
                    <svg
                      className="w-5 h-5 text-teal-600 mt-0.5 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span className="text-sm text-gray-700">
                      Unlimited paraphrasing
                    </span>
                  </div>
                  <div className="flex items-start gap-2">
                    <svg
                      className="w-5 h-5 text-teal-600 mt-0.5 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span className="text-sm text-gray-700">
                      Advanced AI modes
                    </span>
                  </div>
                  <div className="flex items-start gap-2">
                    <svg
                      className="w-5 h-5 text-teal-600 mt-0.5 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span className="text-sm text-gray-700">
                      Priority support
                    </span>
                  </div>
                  <div className="flex items-start gap-2">
                    <svg
                      className="w-5 h-5 text-teal-600 mt-0.5 flex-shrink-0"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path
                        strokeLinecap="round"
                        strokeLinejoin="round"
                        strokeWidth={2}
                        d="M5 13l4 4L19 7"
                      />
                    </svg>
                    <span className="text-sm text-gray-700">
                      No rate limits
                    </span>
                  </div>
                </div>

                <button
                  type="button"
                  className="w-full mt-6 px-4 py-2.5 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 transition-colors"
                >
                  Upgrade to Pro
                </button>
              </div>
            </div>
          </div>

          {/* Column 3: Output */}
          <div className="flex flex-col h-full">
            <TextArea
              label="Paraphrased Text"
              value={outputText}
              onChange={setOutputText}
              placeholder="Your paraphrased text will appear here..."
              readOnly={false}
              isLoading={isLoading}
            />
          </div>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mt-4 p-3 bg-red-50 border border-red-200 rounded-lg text-red-700 text-sm text-center">
            {error}
          </div>
        )}

        {/* Action Buttons (Mobile/Desktop) */}
        <div className="mt-4 flex flex-col sm:flex-row gap-3 justify-center">
          <button
            type="button"
            onClick={handleParaphrase}
            disabled={isLoading || !inputText.trim()}
            className="px-6 py-2.5 text-sm font-medium text-white bg-teal-600 rounded-lg hover:bg-teal-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            {isLoading ? "Paraphrasing..." : "Paraphrase"}
          </button>
          <button
            type="button"
            onClick={handleClear}
            disabled={isLoading || (!inputText && !outputText)}
            className="px-6 py-2.5 text-sm font-medium text-gray-700 bg-gray-100 rounded-lg hover:bg-gray-200 disabled:bg-gray-50 disabled:text-gray-400 disabled:cursor-not-allowed transition-colors"
          >
            Clear All
          </button>
        </div>
      </div>
    </div>
  );
}
