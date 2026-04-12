import api from "@/services/axiosConfig";

export const login = (data: { email: string; password: string }) =>
  api.post("/login", data);
export const register = (data: {
  name: string;
  email: string;
  password: string;
}) => api.post("/register", data);
export const analyzeFace = (data: FormData) =>
  api.post("/analyze_face", data).then((response) => response.data);
export const analyzeFaceImage = (
  base64Image: string,
  isWebcam: boolean = true
) =>
  api
    .post("/analyze_face", {
      image: base64Image,
      webcam: isWebcam,
    })
    .then((response) => response.data);
export const analyzeText = (data: { text: string }) => api.post("/analyze_text", data);
export const calculateScore = (data: object) => api.post("/calculate_score", data);
export const getRecommendation = () => api.get("/recommendation");
export const getTrendData = () => api.get("/trend_data");
export const sendChatbotMessage = (data: { message: string }) => api.post("/chatbot", data);
export const getEmotionStats = () => api.get("/emotion_stats");
export const getHistory = () => api.get("/history");
export const saveAssessment = (data: object) => api.post("/save_assessment", data);
export const getJournalHistory = (filter?: string) =>
  api.get("/journal/history", { params: { filter } });
export const exportReport = () => api.get("/export_report", { responseType: "blob" });

export default api;
