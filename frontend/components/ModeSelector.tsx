"use client";

interface ModeSelectorProps {
  selectedMode: string;
  onModeChange: (mode: string) => void;
}

// Define all available modes with their display names and values
const MODES = [
  { value: "word_changer", label: "Word Changer" },
  { value: "fluency", label: "Fluency" },
  { value: "standard", label: "Standard" },
  { value: "formal", label: "Formal" },
  { value: "smooth", label: "Smooth" },
  { value: "creative", label: "Creative" },
  { value: "smarter", label: "Smarter" },
  { value: "shorten", label: "Shorten" },
  { value: "academic", label: "Academic" },
  { value: "expand", label: "Expand" },
] as const;

export default function ModeSelector({
  selectedMode,
  onModeChange,
}: ModeSelectorProps) {
  return (
    <div className="w-full">
      {/* Desktop: Full width with flex layout */}
      <div className="hidden md:flex items-center gap-1 border-b border-gray-200 overflow-x-auto">
        {MODES.map((mode) => {
          const isActive = selectedMode === mode.value;
          return (
            <button
              key={mode.value}
              type="button"
              onClick={() => onModeChange(mode.value)}
              className={`
                relative px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap
                ${
                  isActive
                    ? "text-teal-600"
                    : "text-gray-600 hover:text-gray-900"
                }
              `}
              aria-label={`Select ${mode.label} mode`}
              aria-pressed={isActive}
            >
              {mode.label}
              {/* Active indicator: teal underline */}
              {isActive && (
                <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-teal-600" />
              )}
            </button>
          );
        })}
      </div>

      {/* Mobile: Horizontal scrollable */}
      <div className="md:hidden overflow-x-auto scrollbar-hide">
        <div className="flex items-center gap-1 border-b border-gray-200 min-w-max">
          {MODES.map((mode) => {
            const isActive = selectedMode === mode.value;
            return (
              <button
                key={mode.value}
                type="button"
                onClick={() => onModeChange(mode.value)}
                className={`
                  relative px-4 py-3 text-sm font-medium transition-colors whitespace-nowrap
                  ${
                    isActive
                      ? "text-teal-600"
                      : "text-gray-600 hover:text-gray-900"
                  }
                `}
                aria-label={`Select ${mode.label} mode`}
                aria-pressed={isActive}
              >
                {mode.label}
                {/* Active indicator: teal underline */}
                {isActive && (
                  <span className="absolute bottom-0 left-0 right-0 h-0.5 bg-teal-600" />
                )}
              </button>
            );
          })}
        </div>
      </div>
    </div>
  );
}

