import { useState } from "react";
import { CheckCircle, Loader2 } from "lucide-react";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

const questions = [
  "How often do you feel nervous, anxious, or on edge?",
  "How often do you find yourself unable to stop or control worrying?",
  "How often do you feel down, depressed, or hopeless?",
  "How often do you have little interest or pleasure in doing things?",
  "How often do you feel overwhelmed by your daily responsibilities?",
];

const options = ["Never", "Sometimes", "Often", "Very Often"];
const optionScores = [0, 1, 2, 3];

const getRiskLevel = (score: number) => {
  if (score <= 4) return { label: "Low Risk", color: "risk-low", emoji: "✅" };
  if (score <= 9)
    return { label: "Moderate Risk", color: "risk-medium", emoji: "⚠️" };
  return { label: "High Risk", color: "risk-high", emoji: "🚨" };
};

const SelfAssessment = () => {
  const [answers, setAnswers] = useState<(number | null)[]>(
    new Array(questions.length).fill(null),
  );
  const [submitted, setSubmitted] = useState(false);
  const [loading, setLoading] = useState(false);

  const setAnswer = (qi: number, val: number) => {
    setAnswers((prev) => {
      const n = [...prev];
      n[qi] = val;
      return n;
    });
  };

  const allAnswered = answers.every((a) => a !== null);

  const submit = async () => {
    if (!allAnswered) return;
    setLoading(true);
    await new Promise((r) => setTimeout(r, 1000));
    setSubmitted(true);
    setLoading(false);
  };

  const totalScore = answers.reduce((sum, a) => sum + (a ?? 0), 0);
  const risk = getRiskLevel(totalScore);

  if (submitted) {
    return (
      <div className="text-center py-8 animate-fade-in-up">
        <div className="text-5xl mb-4">{risk.emoji}</div>
        <h3 className="text-2xl font-display font-bold mb-2">{risk.label}</h3>
        <p className="text-muted-foreground mb-4">
          Assessment Score: <strong>{totalScore}/15</strong>
        </p>
        <div
          className={cn(
            "inline-block px-6 py-3 rounded-xl font-semibold",
            risk.color,
          )}
        >
          {risk.label}
        </div>
        <div className="mt-6">
          <Button
            variant="outline"
            onClick={() => {
              setSubmitted(false);
              setAnswers(new Array(questions.length).fill(null));
            }}
          >
            Retake Assessment
          </Button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      {questions.map((q, qi) => (
        <div
          key={qi}
          className="space-y-3 animate-fade-in-up"
          style={{ animationDelay: `${qi * 80}ms` }}
        >
          <p className="font-medium text-sm">
            <span className="text-primary font-bold mr-2">Q{qi + 1}.</span>
            {q}
          </p>
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
            {options.map((opt, oi) => (
              <button
                key={opt}
                onClick={() => setAnswer(qi, optionScores[oi])}
                className={cn(
                  "px-3 py-2 rounded-lg text-sm font-medium border transition-all",
                  answers[qi] === optionScores[oi]
                    ? "bg-primary text-primary-foreground border-primary shadow-sm"
                    : "bg-card border-border hover:border-primary/50 hover:bg-primary/5",
                )}
              >
                {opt}
              </button>
            ))}
          </div>
        </div>
      ))}
      <Button
        className="btn-primary w-full mt-4"
        onClick={submit}
        disabled={!allAnswered || loading}
      >
        {loading ? (
          <>
            <Loader2 className="w-4 h-4 animate-spin mr-2" /> Evaluating...
          </>
        ) : (
          <>
            <CheckCircle className="w-4 h-4 mr-2" /> Submit Assessment
          </>
        )}
      </Button>
    </div>
  );
};

export default SelfAssessment;
