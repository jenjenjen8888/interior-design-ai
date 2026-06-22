import axios from "axios";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

const client = axios.create({
  baseURL: API_BASE_URL,
});

export interface SuggestionRequest {
  message: string;
  image?: File;
  style: "pinterest" | "stock";
}

export interface SuggestionResponse {
  suggestion: string;
  style: string;
  references?: string[];
}

export const apiClient = {
  async getSuggestion(request: SuggestionRequest): Promise<SuggestionResponse> {
    const formData = new FormData();
    formData.append("message", request.message);
    formData.append("style", request.style);

    if (request.image) {
      formData.append("image", request.image);
    }

    const response = await client.post<SuggestionResponse>(
      "/api/v1/suggest",
      formData,
      {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      }
    );

    return response.data;
  },

  async healthCheck(): Promise<boolean> {
    try {
      await client.get("/health");
      return true;
    } catch {
      return false;
    }
  },
};
