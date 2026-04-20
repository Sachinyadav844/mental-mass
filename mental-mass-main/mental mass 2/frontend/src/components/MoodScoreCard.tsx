import { cn } from "@/lib/utils";

interface MoodScoreCardProps {
  score: number;
  category?: string;
}

const getCategory = (score: number) => {
  if (score >= 71)
    return {
      label: "Excellent",
      color: "text-success",
      ring: "stroke-success",
      bg: "bg-success-soft",
    };
  if (score >= 51)
    return {
      label: "Good",
      color: "text-primary",
      ring: "stroke-primary",
      bg: "bg-lavender-soft",
    };
  if (score >= 35)
    return {
      label: "Moderate",
      color: "text-warning",
      ring: "stroke-warning",
      bg: "bg-warning-soft",
    };
  return {
    label: "At Risk",
    color: "text-destructive",
    ring: "stroke-destructive",
    bg: "bg-destructive/10",
  };
};

const MoodScoreCard = ({ score }: MoodScoreCardProps) => {
  const cat = getCategory(score);
  const radius = 42;
  const circumference = 2 * Math.PI * radius;
  const dashOffset = circumference - (score / 100) * circumference;

  return (
    <div
      className={cn(
        "p-5 rounded-xl flex flex-col items-center gap-4 border",
        cat.bg,
      )}
    >
      <div className="relative w-32 h-32">
        <svg viewBox="0 0 100 100" className="transform -rotate-90 w-32 h-32">
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            strokeWidth="8"
            className="stroke-border/40"
          />
          <circle
            cx="50"
            cy="50"
            r={radius}
            fill="none"
            strokeWidth="8"
            strokeDasharray={circumference}
            strokeDashoffset={dashOffset}
            strokeLinecap="round"
            className={cn(cat.ring, "transition-all duration-1000")}
          />
        </svg>
        <div className="absolute inset-0 flex flex-col items-center justify-center">
          <span className={cn("text-3xl font-display font-bold", cat.color)}>
            {score}
          </span>
          <span className="text-xs text-muted-foreground">/100</span>
        </div>
      </div>
      <div className="text-center">
        <p className={cn("text-lg font-display font-bold", cat.color)}>
          {cat.label}
        </p>
        <p className="text-xs text-muted-foreground mt-0.5">Mood Score</p>
      </div>
    </div>
  );
};

export default MoodScoreCard;
