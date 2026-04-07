import { AlertTriangle, CheckCircle, Info, XCircle } from "lucide-react";

interface RiskAlertProps {
  score: number;
}

const RiskAlert = ({ score }: RiskAlertProps) => {
  if (score >= 71) {
    return (
      <div className="risk-low p-4 rounded-xl flex items-start gap-3 animate-fade-in">
        <CheckCircle className="w-5 h-5 text-success flex-shrink-0 mt-0.5" />
        <div>
          <p className="font-semibold">Excellent Mental Wellness</p>
          <p className="text-sm mt-0.5 opacity-80">
            Your mental wellness score indicates you're in great shape. Keep up
            your healthy habits!
          </p>
        </div>
      </div>
    );
  }
  if (score >= 35) {
    return (
      <div className="risk-medium p-4 rounded-xl flex items-start gap-3 animate-fade-in">
        <Info className="w-5 h-5 text-warning flex-shrink-0 mt-0.5" />
        <div>
          <p className="font-semibold">Moderate Stress Level</p>
          <p className="text-sm mt-0.5 opacity-80">
            You may be experiencing moderate stress. Consider mindfulness
            exercises and adequate rest.
          </p>
        </div>
      </div>
    );
  }
  return (
    <div className="risk-high p-4 rounded-xl flex items-start gap-3 animate-fade-in">
      <XCircle className="w-5 h-5 text-destructive flex-shrink-0 mt-0.5" />
      <div>
        <p className="font-semibold">High Risk Alert</p>
        <p className="text-sm mt-0.5 opacity-80">
          Your score indicates significant mental distress. We strongly
          recommend speaking with a mental health professional.
        </p>
        <button className="mt-2 text-xs font-semibold underline">
          Find resources →
        </button>
      </div>
    </div>
  );
};

export default RiskAlert;
