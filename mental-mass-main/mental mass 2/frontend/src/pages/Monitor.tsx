import { useState, useEffect, useRef } from "react";
import {
  Sliders,
  Camera,
  MessageSquare,
  BarChart2,
  AlertTriangle,
  Sparkles,
  Scan,
  Loader2,
} from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import WebcamCapture from "@/components/WebcamCapture";
import TextSentimentBox from "@/components/TextSentimentBox";
import MoodScoreCard from "@/components/MoodScoreCard";
import RiskAlert from "@/components/RiskAlert";
import RecommendationCard from "@/components/RecommendationCard";
import AgeDetectionCard from "@/components/AgeDetectionCard";
import ChatbotBox from "@/components/ChatbotBox";
import { Button } from "@/components/ui/button";

type SectionCardProps = {
  icon: React.ComponentType<{ className?: string }>;
  title: string;
  children: React.ReactNode;
  color?: string;
};

const SectionCard = ({
  icon: Icon,
  title,
  children,
  color = "bg-primary/10 text-primary",
}: SectionCardProps) => (
  <div className="glass-card p-6 space-y-4 animate-fade-in-up">
    <div className="flex items-center gap-3 border-b border-border/50 pb-4">
      <div
        className={`w-9 h-9 rounded-xl flex items-center justify-center ${color}`}
      >
        <Icon className="w-5 h-5" />
      </div>
      <h2 className="font-display font-bold text-lg">{title}</h2>
    </div>
    {children}
  </div>
);

/** Mirrors backend EMOTION_NUMERIC_MAP / SENTIMENT_NUMERIC_MAP weights for offline fallback */
function computeLocalMoodScore(emotion: string, sentiment: string) {
  const em = emotion.toLowerCase();
  const sn = sentiment.toLowerCase();
  const emotionNum: Record<string, number> = {
    happy: 90,
    surprised: 60,
    surprise: 60,
    neutral: 60,
    uncertain: 50,
    fear: 30,
    fearful: 30,
    sad: 30,
    angry: 20,
    disgust: 15,
    disgusted: 15,
  };
  const sentimentNum: Record<string, number> = {
    positive: 90,
    neutral: 60,
    negative: 30,
  };
  const es = emotionNum[em] ?? 60;
  const ss = sentimentNum[sn] ?? 60;
  const score = Math.round(es * 0.6 + ss * 0.4);
  let risk_level = "Low Risk";
  if (score < 35) risk_level = "High Risk";
  else if (score < 60) risk_level = "Moderate Risk";
  return { score, risk_level };
}

const Monitor = () => {
  const [emotionData, setEmotionData] = useState<any>(null);
  const [sentimentData, setSentimentData] = useState<any>(null);
  const [scoreData, setScoreData] = useState<any>(null);
  const [calculating, setCalculating] = useState(false);

  const sentimentRef = useRef(sentimentData);
  const emotionRef = useRef(emotionData);
  useEffect(() => {
    sentimentRef.current = sentimentData;
  }, [sentimentData]);
  useEffect(() => {
    emotionRef.current = emotionData;
  }, [emotionData]);

  const handleEmotionResult = async (faceResult: any) => {
    setEmotionData(faceResult);
    console.log("Emotion result:", faceResult);
    await recalculateScore(faceResult, sentimentRef.current);
  };

  const handleSentimentResult = async (sentimentResult: any) => {
    setSentimentData(sentimentResult);
    console.log("Sentiment result:", sentimentResult);
    await recalculateScore(emotionRef.current, sentimentResult);
  };

  const recalculateScore = async (emotion: any, sentiment: any) => {
    const em =
      emotion?.emotion != null && String(emotion.emotion).trim()
        ? String(emotion.emotion).trim()
        : "neutral";
    const sent =
      sentiment?.sentiment != null && String(sentiment.sentiment).trim()
        ? String(sentiment.sentiment).trim()
        : "neutral";

    setCalculating(true);
    try {
      const { calculateScore } = await import("@/services/api");
      const result = (await calculateScore({
        emotion: em,
        sentiment: sent,
      })) as { success?: boolean; score?: number; risk_level?: string; message?: string };

      if (result?.success && typeof result.score === "number") {
        setScoreData(result);
        console.log(
          "Backend calculated score:",
          result.score,
          "Risk:",
          result.risk_level
        );
        return;
      }
      throw new Error(result?.message || "Invalid score response");
    } catch (error) {
      console.error("Score calculation error:", error);
      const local = computeLocalMoodScore(em, sent);
      setScoreData({
        score: local.score,
        risk_level: local.risk_level,
        risk_color: "#999999",
        breakdown: undefined,
        emotion_score: undefined,
        sentiment_score: undefined,
        self_score: null,
      });
    } finally {
      setCalculating(false);
    }
  };

  return (
    <div className="page-container">
      <Navbar />
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
        <div className="mb-8 animate-fade-in-up">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center">
              <Sliders className="w-5 h-5 text-primary-foreground" />
            </div>
            <h1 className="text-3xl font-display font-bold">Mood Monitor</h1>
          </div>
          <p className="text-muted-foreground ml-12">
            Capture and analyze your emotional state using AI-powered multimodal
            analysis.
          </p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          <SectionCard
            icon={Camera}
            title="Facial Emotion Detection"
            color="bg-lavender-soft text-lavender"
          >
            <WebcamCapture onResult={handleEmotionResult} />
          </SectionCard>

          <SectionCard
            icon={MessageSquare}
            title="Text Sentiment Analysis"
            color="bg-primary/10 text-primary"
          >
            <TextSentimentBox onResult={handleSentimentResult} />
          </SectionCard>

          <SectionCard
            icon={BarChart2}
            title="Mood Score"
            color="bg-success-soft text-success"
          >
            <div className="flex flex-col items-center gap-4">
              <MoodScoreCard score={scoreData?.score || 50} />
              <Button
                variant="outline"
                size="sm"
                onClick={() =>
                  recalculateScore(
                    emotionData ?? { emotion: "neutral" },
                    sentimentData ?? { sentiment: "neutral" }
                  )
                }
                disabled={calculating}
                className="w-full"
              >
                {calculating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />{" "}
                    Calculating...
                  </>
                ) : (
                  "Recalculate Score"
                )}
              </Button>
            </div>
          </SectionCard>

          <SectionCard
            icon={AlertTriangle}
            title="Risk Alert"
            color="bg-warning-soft text-warning"
          >
            <RiskAlert score={scoreData?.score || 50} />
            <p className="text-xs text-muted-foreground">
              Score: {scoreData?.score || 50}/100 · Risk: {scoreData?.risk_level || 'Unknown'} · Updated just now
            </p>
          </SectionCard>

          <SectionCard
            icon={Sparkles}
            title="Personalized Recommendation"
            color="bg-lavender-soft text-lavender"
          >
            <RecommendationCard
              title="Try 5-Minute Mindful Breathing"
              description="Based on your current mood score, we recommend a short breathing exercise. Box breathing (4-4-4-4 pattern) can help regulate your stress response and improve focus."
              type="breathing"
            />
            <RecommendationCard
              title="Evening Journaling"
              description="Writing about your thoughts and feelings for just 10 minutes before bed can significantly improve your emotional processing and sleep quality."
              type="journaling"
            />
          </SectionCard>

          <SectionCard
            icon={MessageSquare}
            title="AI Chat Support"
            color="bg-primary/10 text-primary"
          >
            <ChatbotBox />
          </SectionCard>

          <SectionCard
            icon={Scan}
            title="Age Detection (Beta)"
            color="bg-lavender-soft text-lavender"
          >
            <AgeDetectionCard />
          </SectionCard>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Monitor;
