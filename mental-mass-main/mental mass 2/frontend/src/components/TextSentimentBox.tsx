import { useState } from "react";
import { MessageSquare, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Textarea } from "@/components/ui/textarea";
import api from "@/services/api";
import { getErrorMessage } from "@/services/errorHandler";

interface SentimentResult {
  sentiment: "positive" | "negative" | "neutral";
  score: number;
  keywords: string[];
}

const sentimentColors = {
  positive: "risk-low",
  negative: "risk-high",
  neutral: "bg-muted text-muted-foreground border border-border",
};

const sentimentEmoji = { positive: "😊", negative: "😔", neutral: "😐" };

const TextSentimentBox = ({
  onResult,
}: {
  onResult?: (r: SentimentResult) => void;
}) => {
  const [text, setText] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<SentimentResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const analyze = async () => {
    if (!text.trim()) return;
    setLoading(true);
    setError(null);
    try {
      const response = await api.post("/analyze_text", { text }, { timeout: 20000 });
      const data = response.data;

      if (data?.success && data?.sentiment) {
        const conf =
          data.confidence != null
            ? Number(data.confidence)
            : Number((data as { score?: number }).score ?? 0);
        const r: SentimentResult = {
          sentiment: data.sentiment,
          score: conf,
          keywords: Array.isArray(data.keywords) ? data.keywords : [],
        };
        setResult(r);
        setError(null);
        onResult?.(r);
      } else {
        const errorMsg = data?.message || data?.error || "Invalid sentiment response from server";
        setError(errorMsg);
        setResult(null);
      }
    } catch (error: any) {
      console.error("Sentiment analysis error", error);
      const errorMsg = getErrorMessage(error, "Sentiment analysis");
      setError(errorMsg);
      setResult(null);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-3">
      <Textarea
        placeholder="Describe how you're feeling today... e.g., 'I've been feeling overwhelmed with work lately and can't focus properly.'"
        value={text}
        onChange={(e) => setText(e.target.value)}
        rows={4}
        className="resize-none border-border/70 focus:border-primary/50 bg-muted/20"
      />
      <div className="flex items-center justify-between">
        <span className="text-xs text-muted-foreground">
          {text.length} characters
        </span>
        <Button
          size="sm"
          className="btn-primary"
          onClick={analyze}
          disabled={!text.trim() || loading}
        >
          {loading ? (
            <>
              <Loader2 className="w-4 h-4 animate-spin mr-1" /> Analyzing...
            </>
          ) : (
            <>
              <MessageSquare className="w-4 h-4 mr-1" /> Analyze Sentiment
            </>
          )}
        </Button>
      </div>

      {error && (
        <div className="p-3 rounded-xl bg-destructive/10 border border-destructive/20 text-destructive text-sm animate-fade-in">
          {error}
        </div>
      )}

      {result && (
        <div
          className={`p-4 rounded-xl animate-fade-in ${sentimentColors[result.sentiment]}`}
        >
          <div className="flex items-center justify-between mb-2">
            <span className="font-semibold capitalize flex items-center gap-2">
              <span>{sentimentEmoji[result.sentiment]}</span>
              {result.sentiment} Sentiment
            </span>
            <span className="text-sm font-medium">
              {Math.round(result.score * 100)}% confidence
            </span>
          </div>
          {result.keywords.length > 0 && (
            <div className="flex gap-2 flex-wrap mt-2">
              {result.keywords.map((k) => (
                <span
                  key={k}
                  className="text-xs px-2 py-0.5 bg-background/50 rounded-full border border-current/20"
                >
                  {k}
                </span>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default TextSentimentBox;
