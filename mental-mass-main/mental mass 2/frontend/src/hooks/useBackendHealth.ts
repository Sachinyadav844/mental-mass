import { useEffect, useState } from "react";
import { checkBackendHealth } from "@/services/errorHandler";

/**
 * Custom hook to check backend health on component mount
 * @returns object with isHealthy, isLoading, error
 */
export const useBackendHealth = () => {
  const [isHealthy, setIsHealthy] = useState<boolean | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    const checkHealth = async () => {
      try {
        setIsLoading(true);
        const healthy = await checkBackendHealth();
        setIsHealthy(healthy);
        if (!healthy) {
          setError("Backend is not responding. Please ensure it's running on http://localhost:5000");
        } else {
          setError(null);
        }
      } catch (err) {
        setIsHealthy(false);
        setError("Failed to check backend status");
        console.error("[Health Check] Error:", err);
      } finally {
        setIsLoading(false);
      }
    };

    checkHealth();
  }, []);

  return { isHealthy, isLoading, error };
};
