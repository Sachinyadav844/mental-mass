import {
  Brain,
  MessageSquare,
  TrendingUp,
  Bell,
  Sparkles,
  Scan,
  BarChart2,
  BookOpen,
} from "lucide-react";
import { Link } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";

const features = [
  {
    icon: Brain,
    title: "Facial Emotion Detection",
    status: "live",
    desc: "AI-powered emotion recognition.",
    color: "bg-lavender-soft text-lavender",
  },
  {
    icon: MessageSquare,
    title: "Text Sentiment Analysis",
    status: "live",
    desc: "Understand emotional tone in text.",
    color: "bg-primary/10 text-primary",
  },
  {
    icon: TrendingUp,
    title: "Mood Scoring",
    status: "live",
    desc: "Composite wellness score 0–100.",
    color: "bg-success-soft text-success",
  },
  {
    icon: Bell,
    title: "Risk Alerts",
    status: "live",
    desc: "Proactive mental health notifications.",
    color: "bg-destructive/10 text-destructive",
  },
  {
    icon: Sparkles,
    title: "Personalized Recommendations",
    status: "live",
    desc: "AI-curated wellness suggestions.",
    color: "bg-warning-soft text-warning",
  },
  {
    icon: Scan,
    title: "Age Detection",
    status: "coming",
    desc: "Upcoming feature for age insights.",
    color: "bg-lavender-soft text-lavender",
  },
  {
    icon: BarChart2,
    title: "Analytics Dashboard",
    status: "live",
    desc: "Track trends and visualize data.",
    color: "bg-primary/10 text-primary",
  },
  {
    icon: BookOpen,
    title: "Mood Journal",
    status: "live",
    desc: "Log and review emotional history.",
    color: "bg-success-soft text-success",
  },
];

const Features = () => (
  <div className="page-container">
    <Navbar />
    <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      <div className="text-center mb-16 animate-fade-in-up">
        <h1 className="text-5xl font-display font-bold mb-3">
          Platform<span className="text-gradient"> Features</span>
        </h1>
        <p className="text-lg text-muted-foreground max-w-2xl mx-auto">
          Comprehensive AI tools for mental wellness monitoring and insights.
        </p>
      </div>

      <div className="grid md:grid-cols-2 gap-6 mb-12">
        {features.map((f, i) => (
          <div
            key={f.title}
            className="feature-card p-6 group hover:shadow-lg hover:-translate-y-1 transition-all duration-300 animate-fade-in-up"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <div className="flex items-start gap-4">
              <div
                className={`w-12 h-12 rounded-xl ${f.color} flex items-center justify-center flex-shrink-0 group-hover:scale-110 transition-transform`}
              >
                <f.icon className="w-6 h-6" />
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-2">
                  <h3 className="font-display font-bold text-lg">
                    {f.title}
                  </h3>
                  <span
                    className={`text-xs px-2.5 py-1 rounded-full font-semibold whitespace-nowrap ${f.status === "live" ? "bg-success-soft text-success" : "bg-lavender-soft text-lavender"}`}
                  >
                    {f.status === "live" ? "● Live" : "○ Soon"}
                  </span>
                </div>
                <p className="text-muted-foreground">{f.desc}</p>
              </div>
            </div>
          </div>
        ))}
      </div>

      <div className="text-center animate-fade-in-up">
        <Button size="lg" className="btn-primary gap-2 text-base" asChild>
          <Link to="/monitor">Explore All Features</Link>
        </Button>
      </div>
    </div>
    <Footer />
  </div>
);

export default Features;
