"use client";

import { useState, useRef, useEffect } from "react";
import { apiClient } from "@/lib/api";

interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
}

interface ChatInterfaceProps {
  uploadedImage: File | null;
}

export function ChatInterface({ uploadedImage }: ChatInterfaceProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: "welcome",
      role: "assistant",
      content:
        "Hi! I'm your interior design assistant. Upload a photo of your space or describe what you're looking for, and I'll give you personalized suggestions.\n\nYou can switch between styles above — Pinterest style gives you trending, aspirational ideas while Stock style gives you clean, professionally staged looks.",
      timestamp: new Date(),
    },
  ]);
  const [input, setInput] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [style, setStyle] = useState<"pinterest" | "stock">("pinterest");
  const messagesEndRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() && !uploadedImage) return;

    const userMessage: Message = {
      id: crypto.randomUUID(),
      role: "user",
      content: input || "(Uploaded an image for analysis)",
      timestamp: new Date(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput("");
    setIsLoading(true);

    try {
      const response = await apiClient.getSuggestion({
        message: input,
        image: uploadedImage || undefined,
        style,
      });

      const assistantMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content: response.suggestion,
        timestamp: new Date(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      const errorMessage: Message = {
        id: crypto.randomUUID(),
        role: "assistant",
        content:
          "Sorry, I encountered an error. Please try again or check that the backend is running.",
        timestamp: new Date(),
      };
      setMessages((prev) => [...prev, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  return (
    <div className="flex h-[600px] flex-col rounded-xl border border-brand-200 bg-white">
      {/* Style selector */}
      <div className="flex border-b border-brand-200 p-3">
        <div className="flex rounded-lg bg-brand-50 p-1">
          <button
            onClick={() => setStyle("pinterest")}
            className={`rounded-md px-4 py-1.5 text-sm font-medium transition ${
              style === "pinterest"
                ? "bg-white text-brand-800 shadow-sm"
                : "text-brand-600 hover:text-brand-800"
            }`}
          >
            Pinterest Style
          </button>
          <button
            onClick={() => setStyle("stock")}
            className={`rounded-md px-4 py-1.5 text-sm font-medium transition ${
              style === "stock"
                ? "bg-white text-brand-800 shadow-sm"
                : "text-brand-600 hover:text-brand-800"
            }`}
          >
            Stock Style
          </button>
        </div>
      </div>

      {/* Messages */}
      <div className="flex-1 overflow-y-auto p-4">
        <div className="flex flex-col gap-4">
          {messages.map((message) => (
            <div
              key={message.id}
              className={`flex ${
                message.role === "user" ? "justify-end" : "justify-start"
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  message.role === "user"
                    ? "bg-brand-600 text-white"
                    : "bg-brand-100 text-gray-800"
                }`}
              >
                <p className="whitespace-pre-wrap text-sm">{message.content}</p>
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className="rounded-lg bg-brand-100 px-4 py-2">
                <div className="flex gap-1">
                  <span className="h-2 w-2 animate-bounce rounded-full bg-brand-400" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-brand-400 [animation-delay:0.1s]" />
                  <span className="h-2 w-2 animate-bounce rounded-full bg-brand-400 [animation-delay:0.2s]" />
                </div>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input */}
      <div className="border-t border-brand-200 p-4">
        <div className="flex gap-2">
          <textarea
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your style or ask for suggestions..."
            className="flex-1 resize-none rounded-lg border border-brand-200 px-3 py-2 text-sm placeholder:text-gray-400 focus:border-brand-500 focus:outline-none focus:ring-1 focus:ring-brand-500"
            rows={2}
          />
          <button
            onClick={sendMessage}
            disabled={isLoading || (!input.trim() && !uploadedImage)}
            className="self-end rounded-lg bg-brand-600 px-4 py-2 text-sm font-medium text-white transition hover:bg-brand-700 disabled:cursor-not-allowed disabled:opacity-50"
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
