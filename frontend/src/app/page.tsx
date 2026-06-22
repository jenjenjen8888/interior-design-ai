export default function HomePage() {
  return (
    <div className="flex flex-col items-center gap-8 py-12">
      <div className="text-center">
        <h2 className="text-3xl font-bold text-brand-900">
          Transform Your Space with AI
        </h2>
        <p className="mt-3 max-w-lg text-gray-600">
          Upload a photo of your room or describe your style, and get
          personalized interior design suggestions powered by AI.
        </p>
      </div>

      <div className="grid w-full max-w-3xl gap-6 md:grid-cols-2">
        <a
          href="/suggest?mode=photo"
          className="flex flex-col items-center gap-3 rounded-xl border border-brand-200 bg-white p-8 shadow-sm transition hover:border-brand-400 hover:shadow-md"
        >
          <svg
            className="h-12 w-12 text-brand-500"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M6.827 6.175A2.31 2.31 0 015.186 7.23c-.38.054-.757.112-1.134.175C2.999 7.58 2.25 8.507 2.25 9.574V18a2.25 2.25 0 002.25 2.25h15A2.25 2.25 0 0021.75 18V9.574c0-1.067-.75-1.994-1.802-2.169a47.865 47.865 0 00-1.134-.175 2.31 2.31 0 01-1.64-1.055l-.822-1.316a2.192 2.192 0 00-1.736-1.039 48.774 48.774 0 00-5.232 0 2.192 2.192 0 00-1.736 1.039l-.821 1.316z"
            />
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M16.5 12.75a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0z"
            />
          </svg>
          <h3 className="text-lg font-medium text-brand-800">Upload a Photo</h3>
          <p className="text-center text-sm text-gray-500">
            Take or upload a photo of your space and get AI suggestions
          </p>
        </a>

        <a
          href="/suggest?mode=text"
          className="flex flex-col items-center gap-3 rounded-xl border border-brand-200 bg-white p-8 shadow-sm transition hover:border-brand-400 hover:shadow-md"
        >
          <svg
            className="h-12 w-12 text-brand-500"
            fill="none"
            viewBox="0 0 24 24"
            strokeWidth={1.5}
            stroke="currentColor"
            aria-hidden="true"
          >
            <path
              strokeLinecap="round"
              strokeLinejoin="round"
              d="M7.5 8.25h9m-9 3H12m-9.75 1.51c0 1.6 1.123 2.994 2.707 3.227 1.129.166 2.27.293 3.423.379.35.026.67.21.865.501L12 21l2.755-4.133a1.14 1.14 0 01.865-.501 48.172 48.172 0 003.423-.379c1.584-.233 2.707-1.626 2.707-3.228V6.741c0-1.602-1.123-2.995-2.707-3.228A48.394 48.394 0 0012 3c-2.392 0-4.744.175-7.043.513C3.373 3.746 2.25 5.14 2.25 6.741v6.018z"
            />
          </svg>
          <h3 className="text-lg font-medium text-brand-800">
            Describe Your Style
          </h3>
          <p className="text-center text-sm text-gray-500">
            Tell us what you&apos;re looking for and get tailored recommendations
          </p>
        </a>
      </div>
    </div>
  );
}
