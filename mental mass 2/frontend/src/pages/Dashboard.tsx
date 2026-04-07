import {
  LayoutDashboard,
  TrendingUp,
  Award,
  Smile,
  Activity,
  Download,
  Loader2,
} from "lucide-react";
import { useState } from "react";
import Navbar from "@/components/Navbar";
import Sidebar from "@/components/Sidebar";
import Footer from "@/components/Footer";
import {
  MoodTrendChart,
  EmotionPieChart,
  RiskDistributionChart,
} from "@/components/DashboardCharts";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";

const stats = [
  {
    label: "Average Mood Score",
    value: "64",
    sub: "+5 this week",
    icon: TrendingUp,
    color: "bg-primary/10 text-primary",
    trend: "up",
  },
  {
    label: "Highest Risk Level",
    value: "Moderate",
    sub: "Last 7 days",
    icon: Award,
    color: "bg-warning-soft text-warning",
    trend: "neutral",
  },
  {
    label: "Most Frequent Emotion",
    value: "Happy 😊",
    sub: "35% of sessions",
    icon: Smile,
    color: "bg-success-soft text-success",
    trend: "up",
  },
  {
    label: "Total Sessions",
    value: "24",
    sub: "This month",
    icon: Activity,
    color: "bg-lavender-soft text-lavender",
    trend: "up",
  },
];

const Dashboard = () => {
  const [exporting, setExporting] = useState(false);
  const { toast } = useToast();

  const handleExport = async () => {
    setExporting(true);
    await new Promise((r) => setTimeout(r, 1500));
    setExporting(false);
    toast({
      title: "Report Ready",
      description: "Your wellness report has been downloaded.",
    });
  };

  return (
    <div className="flex min-h-screen bg-background">
      <Sidebar />
      <div className="flex-1 flex flex-col min-w-0">
        <Navbar />
        <main className="flex-1 p-6 max-w-6xl w-full mx-auto">
          {/* Header */}
          <div className="flex items-center justify-between mb-8 animate-fade-in-up">
            <div>
              <div className="flex items-center gap-3 mb-1">
                <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center">
                  <LayoutDashboard className="w-5 h-5 text-primary-foreground" />
                </div>
                <h1 className="text-3xl font-display font-bold">
                  Analytics Dashboard
                </h1>
              </div>
              <p className="text-muted-foreground ml-12">
                Your wellness journey at a glance
              </p>
            </div>
            <Button
              className="btn-primary gap-2"
              onClick={handleExport}
              disabled={exporting}
            >
              {exporting ? (
                <>
                  <Loader2 className="w-4 h-4 animate-spin" /> Exporting...
                </>
              ) : (
                <>
                  <Download className="w-4 h-4" /> Export PDF
                </>
              )}
            </Button>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
            {stats.map((s, i) => (
              <div
                key={s.label}
                className="stat-card p-4 animate-fade-in-up"
                style={{ animationDelay: `${i * 80}ms` }}
              >
                <div
                  className={`w-9 h-9 rounded-xl ${s.color} flex items-center justify-center mb-3`}
                >
                  <s.icon className="w-5 h-5" />
                </div>
                <p className="text-2xl font-display font-bold">{s.value}</p>
                <p className="text-xs text-muted-foreground mt-1">{s.label}</p>
                <p className="text-xs text-success font-medium mt-0.5">
                  {s.sub}
                </p>
              </div>
            ))}
          </div>

          {/* Charts */}
          <div className="grid lg:grid-cols-2 gap-6 mb-6">
            <div
              className="glass-card p-5 animate-fade-in-up"
              style={{ animationDelay: "320ms" }}
            >
              <h3 className="font-display font-semibold mb-4 flex items-center gap-2">
                <TrendingUp className="w-4 h-4 text-primary" /> Mood Trend (7
                Days)
              </h3>
              <MoodTrendChart />
            </div>
            <div
              className="glass-card p-5 animate-fade-in-up"
              style={{ animationDelay: "400ms" }}
            >
              <h3 className="font-display font-semibold mb-4 flex items-center gap-2">
                <Smile className="w-4 h-4 text-lavender" /> Emotion Distribution
              </h3>
              <EmotionPieChart />
            </div>
          </div>

          <div
            className="glass-card p-5 animate-fade-in-up"
            style={{ animationDelay: "480ms" }}
          >
            <h3 className="font-display font-semibold mb-4 flex items-center gap-2">
              <Activity className="w-4 h-4 text-warning" /> Risk Level
              Distribution
            </h3>
            <RiskDistributionChart />
          </div>
        </main>
        <Footer />
      </div>
    </div>
  );
};

export default Dashboard;
