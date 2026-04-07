import { Scan, Clock } from "lucide-react";
import { Badge } from "@/components/ui/badge";

const AgeDetectionCard = () => (
  <div className="p-5 rounded-xl glass-card border border-dashed border-border/80">
    <div className="flex items-center justify-between mb-4">
      <div className="flex items-center gap-2">
        <div className="w-9 h-9 rounded-xl bg-lavender-soft flex items-center justify-center">
          <Scan className="w-5 h-5 text-lavender" />
        </div>
        <div>
          <p className="font-semibold text-sm">Age Detection</p>
          <p className="text-xs text-muted-foreground">
            AI-based age estimation
          </p>
        </div>
      </div>
      <Badge
        variant="secondary"
        className="flex items-center gap-1 bg-lavender-soft text-lavender border-lavender/30"
      >
        <Clock className="w-3 h-3" /> Coming Soon
      </Badge>
    </div>
    <div className="grid grid-cols-2 gap-3">
      <div className="p-3 rounded-lg bg-muted/40 text-center">
        <p className="text-2xl font-display font-bold text-muted-foreground/40">
          --
        </p>
        <p className="text-xs text-muted-foreground mt-1">Estimated Age</p>
      </div>
      <div className="p-3 rounded-lg bg-muted/40 text-center">
        <p className="text-sm font-medium text-muted-foreground/40 mt-1">--</p>
        <p className="text-xs text-muted-foreground mt-1">Age Group Advice</p>
      </div>
    </div>
    <p className="text-xs text-muted-foreground mt-3 text-center">
      Age-based wellness recommendations will be available soon
    </p>
  </div>
);

export default AgeDetectionCard;
