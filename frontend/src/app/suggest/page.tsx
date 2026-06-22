"use client";

import { useState } from "react";
import { ImageUpload } from "@/components/ImageUpload";
import { ChatInterface } from "@/components/ChatInterface";

export default function SuggestPage() {
  const [uploadedImage, setUploadedImage] = useState<File | null>(null);
  const [imagePreview, setImagePreview] = useState<string | null>(null);

  const handleImageUpload = (file: File) => {
    setUploadedImage(file);
    const reader = new FileReader();
    reader.onloadend = () => {
      setImagePreview(reader.result as string);
    };
    reader.readAsDataURL(file);
  };

  const handleRemoveImage = () => {
    setUploadedImage(null);
    setImagePreview(null);
  };

  return (
    <div className="flex flex-col gap-6 lg:flex-row">
      {/* Left panel: Image upload */}
      <div className="w-full lg:w-1/3">
        <div className="sticky top-8">
          <h2 className="mb-4 text-lg font-semibold text-brand-800">
            Your Space
          </h2>
          {imagePreview ? (
            <div className="relative">
              <img
                src={imagePreview}
                alt="Uploaded room"
                className="w-full rounded-lg border border-brand-200 object-cover"
              />
              <button
                onClick={handleRemoveImage}
                className="absolute right-2 top-2 rounded-full bg-white/80 p-1 text-gray-600 hover:bg-white hover:text-gray-900"
                aria-label="Remove image"
              >
                <svg className="h-5 w-5" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" d="M6 18L18 6M6 6l12 12" />
                </svg>
              </button>
            </div>
          ) : (
            <ImageUpload onUpload={handleImageUpload} />
          )}
        </div>
      </div>

      {/* Right panel: Chat interface */}
      <div className="w-full lg:w-2/3">
        <ChatInterface uploadedImage={uploadedImage} />
      </div>
    </div>
  );
}
