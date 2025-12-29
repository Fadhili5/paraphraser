export default function Header() {
  return (
    <header className="sticky top-0 z-50 w-full border-b border-gray-200 bg-white">
      <div className="container mx-auto flex h-16 items-center justify-between px-4">
        {/* Logo/Brand */}
        <div className="flex items-center gap-2">
          <h1 className="text-xl font-bold text-teal-600">AI Paraphraser</h1>
        </div>

        {/* Navigation - Basic for now, will be enhanced in Task 6 */}
        <nav className="hidden md:flex items-center gap-6">
          <a href="#" className="text-gray-600 hover:text-teal-600 transition-colors">
            Home
          </a>
        </nav>

        {/* Mobile menu button - placeholder for Task 6 */}
        <button className="md:hidden text-gray-600 hover:text-teal-600">
          <svg
            className="h-6 w-6"
            fill="none"
            stroke="currentColor"
            viewBox="0 0 24 24"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              strokeWidth={2}
              d="M4 6h16M4 12h16M4 18h16"
            />
          </svg>
        </button>
      </div>
    </header>
  );
}

