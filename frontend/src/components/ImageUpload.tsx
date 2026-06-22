"use client";

import { useCallback } from "react";
import { useDropzone } from "react-dropzone";

interface ImageUploadProps {
  onUpload: (file: File) => void;
}

export function ImageUpload({ onUpload }: ImageUploadProps) {
  const onDrop = useCallback(
    (acceptedFiles: File[]) => {
      if (acceptedFiles.length > 0) {
        onUpload(acceptedFiles[0]);
      }
    },
    [onUpload]
  );

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "image/*": [".jpeg", ".jpg", ".png", ".webp", ".heic"],
    },
    maxFiles: 1,
    maxSize: 10 * 1024 * 1024, // 10MB
  });

  return (
    <div
      {...getRootProps()}
      className={`flex cursor-pointer flex-col items-center justify-center rounded-xl border-2 border-dashed p-8 transition ${
        isDragActive
          ? "border-brand-500 bg-brand-50"
          : "border-brand-200 bg-white hover:border-brand-400"
      }`}
    >
      <input {...getInputProps()} />
      <svg
        className="mb-3 h-10 w-10 text-brand-400"
        fill="none"
        viewBox="0 0 24 24"
        strokeWidth={1.5}
        stroke="currentColor"
        aria-hidden="true"
      >
        <path
          strokeLinecap="round"
          strokeLinejoin="round"
          d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5"
        />
      </svg>
      {isDragActive ? (
        <p className="text-sm text-brand-600">Drop your image here...</p>
      ) : (
        <>
          <p className="text-sm font-medium text-brand-700">
            Drag & drop a photo of your room
          </p>
          <p className="mt-1 text-xs text-gray-500">
            or click to browse (JPEG, PNG, WebP — max 10MB)
          </p>
        </>
      )}
    </div>
  );
}
