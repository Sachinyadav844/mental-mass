import { cn } from "@/lib/utils";

type Emotion =
  | "happy"
  | "sad"
  | "angry"
  | "neutral"
  | "fearful"
  | "surprised"
  | "disgusted";

const emotionConfig: Record<string, { color: string; emoji: string }> = {
  // Aliases for backend / DeepFace labels
  fear: {
    color: "bg-warning-soft text-warning-foreground border border-warning/30",
    emoji: "😨",
  },
  disgust: {
    color: "bg-orange-50 text-orange-600 border border-orange-200",
    emoji: "🤢",
  },
  happy: {
    color: "bg-success-soft text-success border border-success/30",
    emoji: "😊",
  },
  sad: {
    color: "bg-blue-50 text-blue-600 border border-blue-200",
    emoji: "😢",
  },
  angry: {
    color: "bg-destructive/10 text-destructive border border-destructive/30",
    emoji: "😠",
  },
  neutral: {
    color: "bg-muted text-muted-foreground border border-border",
    emoji: "😐",
  },
  fearful: {
    color: "bg-warning-soft text-warning-foreground border border-warning/30",
    emoji: "😨",
  },
  surprised: {
    color: "bg-lavender-soft text-lavender border border-lavender/30",
    emoji: "😲",
  },
  disgusted: {
    color: "bg-orange-50 text-orange-600 border border-orange-200",
    emoji: "🤢",
  },
};

const EmotionBadge = ({
  emotion,
  confidence,
}: {
  emotion: string;
  confidence?: number;
}) => {
  const key = emotion?.toLowerCase() as Emotion;
  const cfg = emotionConfig[key] ?? emotionConfig.neutral;
  return (
    <span
      className={cn(
        "inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-sm font-semibold",
        cfg.color,
      )}
    >
      <span>{cfg.emoji}</span>
      <span className="capitalize">{emotion || "Unknown"}</span>
      {confidence !== undefined && (
        <span className="opacity-70 text-xs">
          ({Math.round(confidence * 100)}%)
        </span>
      )}
    </span>
  );
};

export default EmotionBadge;
