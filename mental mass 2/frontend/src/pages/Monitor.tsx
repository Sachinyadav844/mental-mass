import { useState } from "react";
import {
  Sliders,
  Camera,
  MessageSquare,
  BarChart2,
  AlertTriangle,
  Sparkles,
  Scan,
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
import { Loader2 } from "lucide-react";

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

const Monitor = () => {
  const [score, setScore] = useState(62);
  const [calculating, setCalculating] = useState(false);

  const recalculate = async () => {
    setCalculating(true);
    await new Promise((r) => setTimeout(r, 1200));
    setScore(Math.floor(Math.random() * 80) + 15);
    setCalculating(false);
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
            <WebcamCapture />
          </SectionCard>

          <SectionCard
            icon={MessageSquare}
            title="Text Sentiment Analysis"
            color="bg-primary/10 text-primary"
          >
            <TextSentimentBox />
          </SectionCard>

          <SectionCard
            icon={BarChart2}
            title="Mood Score"
            color="bg-success-soft text-success"
          >
            <div className="flex flex-col items-center gap-4">
              <MoodScoreCard score={score} />
              <Button
                variant="outline"
                size="sm"
                onClick={recalculate}
                disabled={calculating}
                className="w-full"
              >
                {calculating ? (
                  <>
                    <Loader2 className="w-4 h-4 animate-spin mr-2" />{" "}
                    Recalculating...
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
            <RiskAlert score={score} />
            <p className="text-xs text-muted-foreground">
              Score: {score}/100 · Updated just now
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
