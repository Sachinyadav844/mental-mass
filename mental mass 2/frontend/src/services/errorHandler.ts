import axios, { AxiosError } from "axios";

interface ErrorResponse {
  message: string;
  isNetworkError: boolean;
}

/**
 * Parse API error and determine if it's a network error or API error
 * @param error - The error object from axios
 * @returns Object with message and isNetworkError flag
 */
export const parseApiError = (error: any): ErrorResponse => {
  console.error("[API Error]", error);

  // Check if it's an axios error
  if (axios.isAxiosError(error)) {
    const axiosError = error as AxiosError<any>;

    // Has response = API error (4xx, 5xx)
    if (axiosError.response) {
      const data = axiosError.response.data;
      const message =
        data?.message || data?.error || `Server error: ${axiosError.response.status}`;
      return {
        message,
        isNetworkError: false,
      };
    }

    // No response = network/connection error
    if (axiosError.code === "ECONNABORTED") {
      return {
        message: "Request timeout. Backend may be unresponsive.",
        isNetworkError: true,
      };
    }

    if (axiosError.code === "ECONNREFUSED" || axiosError.code === "ENOTFOUND") {
      return {
        message: "Cannot connect to backend at http://localhost:5000",
        isNetworkError: true,
      };
    }

    // Generic network error
    if (axiosError.message === "Network Error") {
      return {
        message: "Network error: Cannot reach backend server",
        isNetworkError: true,
      };
    }

    return {
      message: error.message || "Network request failed",
      isNetworkError: true,
    };
  }

  // Non-axios error
  return {
    message: error?.message || "Unknown error occurred",
    isNetworkError: false,
  };
};

/**
 * Check backend connectivity
 * @returns true if backend is reachable, false otherwise
 */
export const checkBackendHealth = async (): Promise<boolean> => {
  try {
    const response = await axios.get("http://localhost:5000/health", {
      timeout: 5000,
    });
    return response.status === 200;
  } catch (error) {
    console.warn("[Health Check] Backend not responding:", error);
    return false;
  }
};

/**
 * Get user-friendly error message with model loading detection
 */
export const getErrorMessage = (error: any, operationName: string = "Operation"): string => {
  const parsed = parseApiError(error);

  // Check for model-specific errors
  if (parsed.message.includes("DeepFace") || parsed.message.includes("emotion")) {
    return "AI emotion model is loading. Please try again in a moment.";
  }

  if (parsed.isNetworkError) {
    return `${parsed.message}. Please check if the backend is running on http://localhost:5000`;
  }

  return parsed.message || `${operationName} failed. Please try again.`;
};
