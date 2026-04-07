import { useState, useEffect } from "react";
import {
  Calendar,
  Filter,
  TrendingUp,
  TrendingDown,
  Minus,
} from "lucide-react";
import EmotionBadge from "./EmotionBadge";
import Loader from "./Loader";
import { cn } from "@/lib/utils";

interface JournalEntry {
  id: string;
  date: string;
  emotion: string;
  sentiment: string;
  score: number;
  riskLevel: "low" | "medium" | "high";
}

const mockData: JournalEntry[] = [
  {
    id: "1",
    date: "2024-02-15",
    emotion: "happy",
    sentiment: "positive",
    score: 78,
    riskLevel: "low",
  },
  {
    id: "2",
    date: "2024-02-14",
    emotion: "neutral",
    sentiment: "neutral",
    score: 55,
    riskLevel: "medium",
  },
  {
    id: "3",
    date: "2024-02-13",
    emotion: "sad",
    sentiment: "negative",
    score: 30,
    riskLevel: "high",
  },
  {
    id: "4",
    date: "2024-02-12",
    emotion: "happy",
    sentiment: "positive",
    score: 72,
    riskLevel: "low",
  },
  {
    id: "5",
    date: "2024-02-11",
    emotion: "neutral",
    sentiment: "neutral",
    score: 48,
    riskLevel: "medium",
  },
  {
    id: "6",
    date: "2024-02-10",
    emotion: "surprised",
    sentiment: "positive",
    score: 65,
    riskLevel: "low",
  },
  {
    id: "7",
    date: "2024-02-09",
    emotion: "sad",
    sentiment: "negative",
    score: 28,
    riskLevel: "high",
  },
];

const riskColors: Record<string, string> = {
  low: "risk-low",
  medium: "risk-medium",
  high: "risk-high",
};

const JournalHistory = () => {
  const [filter, setFilter] = useState<"7" | "30" | "all">("7");
  const [data, setData] = useState<JournalEntry[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setTimeout(() => {
      setData(mockData);
      setLoading(false);
    }, 800);
  }, [filter]);

  if (loading) return <Loader message="Loading journal history..." />;

  return (
    <div className="space-y-4">
      {/* Filter */}
      <div className="flex items-center gap-2">
        <Filter className="w-4 h-4 text-muted-foreground" />
        {(["7", "30", "all"] as const).map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={cn(
              "px-3 py-1.5 rounded-lg text-sm font-medium border transition-all",
              filter === f
                ? "bg-primary text-primary-foreground border-primary"
                : "border-border hover:border-primary/50",
            )}
          >
            {f === "all" ? "All Time" : `Last ${f} Days`}
          </button>
        ))}
      </div>

      {/* Table */}
      <div className="overflow-x-auto rounded-xl border border-border">
        <table className="w-full text-sm">
          <thead>
            <tr className="bg-muted/50 border-b border-border">
              <th className="text-left px-4 py-3 font-semibold text-muted-foreground">
                Date
              </th>
              <th className="text-left px-4 py-3 font-semibold text-muted-foreground">
                Emotion
              </th>
              <th className="text-left px-4 py-3 font-semibold text-muted-foreground">
                Sentiment
              </th>
              <th className="text-left px-4 py-3 font-semibold text-muted-foreground">
                Score
              </th>
              <th className="text-left px-4 py-3 font-semibold text-muted-foreground">
                Risk
              </th>
            </tr>
          </thead>
          <tbody>
            {data.map((entry, i) => (
              <tr
                key={entry.id}
                className={cn(
                  "border-b border-border/50 hover:bg-muted/30 transition-colors animate-fade-in",
                )}
                style={{ animationDelay: `${i * 60}ms` }}
              >
                <td className="px-4 py-3 text-muted-foreground flex items-center gap-2">
                  <Calendar className="w-3.5 h-3.5" />
                  {entry.date}
                </td>
                <td className="px-4 py-3">
                  <EmotionBadge emotion={entry.emotion} />
                </td>
                <td className="px-4 py-3 capitalize text-muted-foreground">
                  {entry.sentiment}
                </td>
                <td className="px-4 py-3">
                  <span className="font-semibold text-foreground flex items-center gap-1">
                    {entry.score >= 60 ? (
                      <TrendingUp className="w-3.5 h-3.5 text-success" />
                    ) : entry.score >= 40 ? (
                      <Minus className="w-3.5 h-3.5 text-warning" />
                    ) : (
                      <TrendingDown className="w-3.5 h-3.5 text-destructive" />
                    )}
                    {entry.score}
                  </span>
                </td>
                <td className="px-4 py-3">
                  <span
                    className={cn(
                      "px-2 py-0.5 rounded-full text-xs font-semibold capitalize",
                      riskColors[entry.riskLevel],
                    )}
                  >
                    {entry.riskLevel}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default JournalHistory;
