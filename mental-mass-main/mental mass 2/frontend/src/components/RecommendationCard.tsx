import { Lightbulb, Heart, Zap, Wind, Music, BookOpen } from "lucide-react";

interface RecommendationCardProps {
  title?: string;
  description?: string;
  type?:
    | "meditation"
    | "exercise"
    | "breathing"
    | "music"
    | "journaling"
    | "general";
}

const typeConfig = {
  meditation: { icon: Heart, color: "text-lavender", bg: "bg-lavender-soft" },
  exercise: { icon: Zap, color: "text-success", bg: "bg-success-soft" },
  breathing: { icon: Wind, color: "text-primary", bg: "bg-primary/10" },
  music: { icon: Music, color: "text-warning", bg: "bg-warning-soft" },
  journaling: { icon: BookOpen, color: "text-primary", bg: "bg-lavender-soft" },
  general: { icon: Lightbulb, color: "text-lavender", bg: "bg-lavender-soft" },
};

const RecommendationCard = ({
  title = "Try Mindful Breathing",
  description = "Take 5 minutes for deep breathing exercises. Inhale for 4 seconds, hold for 4, exhale for 6. This activates your parasympathetic nervous system.",
  type = "breathing",
}: RecommendationCardProps) => {
  const cfg = typeConfig[type];
  const Icon = cfg.icon;

  return (
    <div className="p-5 rounded-xl glass-card border-l-4 border-l-primary/60 animate-fade-in">
      <div className="flex items-start gap-4">
        <div
          className={`w-10 h-10 rounded-xl ${cfg.bg} flex items-center justify-center flex-shrink-0`}
        >
          <Icon className={`w-5 h-5 ${cfg.color}`} />
        </div>
        <div>
          <p className="font-display font-semibold text-foreground">{title}</p>
          <p className="text-sm text-muted-foreground mt-1 leading-relaxed">
            {description}
          </p>
        </div>
      </div>
    </div>
  );
};

export default RecommendationCard;
