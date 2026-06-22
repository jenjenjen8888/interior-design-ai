import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Interior Design AI",
  description: "AI-powered interior design suggestions for your space",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en">
      <body className="min-h-screen bg-brand-50 text-gray-900 antialiased">
        <header className="border-b border-brand-200 bg-white">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4">
            <h1 className="text-xl font-semibold text-brand-800">
              Interior Design AI
            </h1>
            <nav className="flex gap-4">
              <a href="/" className="text-sm text-brand-600 hover:text-brand-800">
                Home
              </a>
              <a href="/suggest" className="text-sm text-brand-600 hover:text-brand-800">
                Get Suggestions
              </a>
            </nav>
          </div>
        </header>
        <main className="mx-auto max-w-7xl px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
