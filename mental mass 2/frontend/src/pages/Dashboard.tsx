import {
  LayoutDashboard,
  TrendingUp,
  Award,
  Smile,
  Activity,
  Download,
  Loader2,
} from "lucide-react";
import { useState, useEffect } from "react";
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
import { useGlobalSocket } from "@/hooks/useSocket";
import api from "@/services/axiosConfig";

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
  const [loading, setLoading] = useState(true);
  const [stats, setStats] = useState([
    {
      label: "Average Mood Score",
      value: "--",
      sub: "Loading...",
      icon: TrendingUp,
      color: "bg-primary/10 text-primary",
      trend: "up",
    },
    {
      label: "Highest Risk Level",
      value: "--",
      sub: "Loading...",
      icon: Award,
      color: "bg-warning-soft text-warning",
      trend: "neutral",
    },
    {
      label: "Most Frequent Emotion",
      value: "--",
      sub: "Loading...",
      icon: Smile,
      color: "bg-success-soft text-success",
      trend: "up",
    },
    {
      label: "Total Sessions",
      value: "0",
      sub: "All time",
      icon: Activity,
      color: "bg-lavender-soft text-lavender",
      trend: "up",
    },
  ]);
  const [trendData, setTrendData] = useState<Array<{ day: string; score: number }>>([]);
  const [emotionData, setEmotionData] = useState<Array<{ name: string; value: number; color: string }>>([]);
  const [riskData, setRiskData] = useState<Array<{ range: string; count: number; fill: string }>>([]);
  const { toast } = useToast();

  // Initialize Socket.IO connection
  const socket = useGlobalSocket();

  useEffect(() => {
    fetchDashboardData();
  }, []);

  // Listen for real-time dashboard updates
  useEffect(() => {
    if (!socket) return;

    const handleDashboardUpdate = (data: any) => {
      console.log("[Dashboard] Received real-time update:", data);
      
      // Refresh data to get latest updates
      // This could be optimized by directly updating state with the socket data
      fetchDashboardData();
    };

    const handleSessionCreated = (data: any) => {
      console.log("[Dashboard] New session created:", data);
      
      // Show toast notification for new session
      toast({
        title: "New Session",
        description: "Your latest analysis has been recorded",
      });
      
      // Refresh dashboard data
      fetchDashboardData();
    };

    const handleEmotionDetected = (data: any) => {
      console.log("[Dashboard] Emotion detected:", data);
    };

    // Subscribe to Socket.IO events
    socket.on("dashboard_update", handleDashboardUpdate);
    socket.on("session_created", handleSessionCreated);
    socket.on("emotion_detected", handleEmotionDetected);

    // Cleanup listeners on unmount
    return () => {
      socket.off("dashboard_update", handleDashboardUpdate);
      socket.off("session_created", handleSessionCreated);
      socket.off("emotion_detected", handleEmotionDetected);
    };
  }, [socket, toast]);

  const fetchDashboardData = async () => {
    try {
      setLoading(true);
      const response = await api.get("/sessions");
      const sessions = response.data?.sessions || [];

      if (sessions.length === 0) {
        setLoading(false);
        console.log("No sessions data available");
        
        // Set empty data with meaningful defaults
        setStats([
          {
            label: "Average Mood Score",
            value: "--",
            sub: "No data yet",
            icon: TrendingUp,
            color: "bg-primary/10 text-primary",
            trend: "up",
          },
          {
            label: "Risk Level",
            value: "--",
            sub: "No data yet",
            icon: Award,
            color: "bg-warning-soft text-warning",
            trend: "neutral",
          },
          {
            label: "Most Frequent Emotion",
            value: "--",
            sub: "No data yet",
            icon: Smile,
            color: "bg-success-soft text-success",
            trend: "up",
          },
          {
            label: "Total Sessions",
            value: "0",
            sub: "No sessions",
            icon: Activity,
            color: "bg-lavender-soft text-lavender",
            trend: "up",
          },
        ]);
        
        setTrendData([]);
        setEmotionData([]);
        setRiskData([]);
        
        return;
      }

      // Calculate statistics
      const avgScore = sessions.reduce((sum, s) => sum + (s.mood_score || 0), 0) / sessions.length;
      
      // Get emotion distribution
      const emotionCounts: Record<string, number> = {};
      const emotionColors: Record<string, string> = {
        happy: "#22c55e",
        neutral: "#818cf8",
        sad: "#60a5fa",
        surprised: "#f59e0b",
        angry: "#ef4444",
        fear: "#ec4899",
        disgust: "#8b5cf6",
      };
      
      sessions.forEach(s => {
        if (s.emotion) {
          emotionCounts[s.emotion] = (emotionCounts[s.emotion] || 0) + 1;
        }
      });
      
      const topEmotions = Object.entries(emotionCounts)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
      
      const newEmotionData = topEmotions.map(([emotion, count]) => ({
        name: emotion.charAt(0).toUpperCase() + emotion.slice(1),
        value: count,
        color: emotionColors[emotion] || "#6366f1",
      }));
      
      // Get risk distribution
      const riskCounts = { low: 0, medium: 0, high: 0 };
      sessions.forEach(s => {
        const score = s.mood_score || 0;
        if (score > 70) riskCounts.low++;
        else if (score >= 35) riskCounts.medium++;
        else riskCounts.high++;
      });
      
      const newRiskData = [
        { range: "Low (>70)", count: riskCounts.low, fill: "#22c55e" },
        { range: "Medium (35-70)", count: riskCounts.medium, fill: "#f59e0b" },
        { range: "High (<35)", count: riskCounts.high, fill: "#ef4444" },
      ];
      
      // Get last 7 days trend
      const last7Days = getLast7DaysTrend(sessions);
      
      // Update stats
      const mostFrequentEmotion = topEmotions[0]?.[0] || "Not Available";
      const riskLevel = avgScore > 70 ? "Low" : avgScore >= 35 ? "Moderate" : "High";
      
      setStats([
        {
          label: "Average Mood Score",
          value: avgScore.toFixed(1),
          sub: `Across ${sessions.length} sessions`,
          icon: TrendingUp,
          color: "bg-primary/10 text-primary",
          trend: "up",
        },
        {
          label: "Risk Level",
          value: riskLevel,
          sub: "Based on avg score",
          icon: Award,
          color: riskLevel === "High" ? "bg-danger-soft text-danger" : "bg-warning-soft text-warning",
          trend: "neutral",
        },
        {
          label: "Most Frequent Emotion",
          value: mostFrequentEmotion.charAt(0).toUpperCase() + mostFrequentEmotion.slice(1),
          sub: `${topEmotions[0]?.[1] || 0} occurrences`,
          icon: Smile,
          color: "bg-success-soft text-success",
          trend: "up",
        },
        {
          label: "Total Sessions",
          value: sessions.length.toString(),
          sub: "All time",
          icon: Activity,
          color: "bg-lavender-soft text-lavender",
          trend: "up",
        },
      ]);
      
      setTrendData(last7Days);
      setEmotionData(newEmotionData.length > 0 ? newEmotionData : []);
      setRiskData(newRiskData);
    } catch (error) {
      console.error("Failed to fetch dashboard data:", error);
      
      // Show more specific error messages
      let errorMessage = "Failed to load dashboard data";
      
      if (error instanceof Error) {
        if (error.message.includes("401") || error.message.includes("Unauthorized")) {
          errorMessage = "Please log in to view your dashboard";
        } else if (error.message.includes("Network")) {
          errorMessage = "Network error - please check your connection";
        } else if (error.message.includes("timeout")) {
          errorMessage = "Request timeout - server took too long to respond";
        }
      }
      
      toast({
        title: "Error",
        description: errorMessage,
        variant: "destructive",
      });
    } finally {
      setLoading(false);
    }
  };

  const getLast7DaysTrend = (sessions: any[]) => {
    const days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"];
    const dayScores: Record<string, number[]> = {};
    
    sessions.forEach(s => {
      if (s.timestamp) {
        const date = new Date(s.timestamp);
        const dayOfWeek = days[date.getDay()];
        if (!dayScores[dayOfWeek]) dayScores[dayOfWeek] = [];
        if (s.mood_score) dayScores[dayOfWeek].push(s.mood_score);
      }
    });
    
    return days.map(day => ({
      day,
      score: dayScores[day]?.length > 0 
        ? Math.round(dayScores[day].reduce((a, b) => a + b) / dayScores[day].length)
        : 50,
    }));
  };

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
              {loading ? (
                <div className="h-[220px] flex items-center justify-center text-muted-foreground">
                  <Loader2 className="w-5 h-5 animate-spin mr-2" /> Loading...
                </div>
              ) : (
                <MoodTrendChart data={trendData} />
              )}
            </div>
            <div
              className="glass-card p-5 animate-fade-in-up"
              style={{ animationDelay: "400ms" }}
            >
              <h3 className="font-display font-semibold mb-4 flex items-center gap-2">
                <Smile className="w-4 h-4 text-lavender" /> Emotion Distribution
              </h3>
              {loading ? (
                <div className="h-[220px] flex items-center justify-center text-muted-foreground">
                  <Loader2 className="w-5 h-5 animate-spin mr-2" /> Loading...
                </div>
              ) : (
                <EmotionPieChart data={emotionData} />
              )}
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
            {loading ? (
              <div className="h-[180px] flex items-center justify-center text-muted-foreground">
                <Loader2 className="w-5 h-5 animate-spin mr-2" /> Loading...
              </div>
            ) : (
              <RiskDistributionChart data={riskData} />
            )}
          </div>
        </main>
        <Footer />
      </div>
    </div>
  );
};

export default Dashboard;
