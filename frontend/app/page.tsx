export default function Home() {
  return (
    <div className="flex min-h-screen items-center justify-center bg-white">
      <main className="flex flex-col items-center gap-8 p-8">
        <h1 className="text-4xl font-bold text-gray-900">
          AI Paraphraser Frontend
        </h1>
        <div className="flex flex-col gap-4">
          <p className="text-lg text-gray-600">
            Next.js project initialized successfully!
          </p>
          {/* Test Tailwind teal color */}
          <div className="rounded-lg bg-teal-500 px-6 py-3 text-white">
            Tailwind CSS is working - Teal color test
          </div>
        </div>
      </main>
    </div>
  );
}
