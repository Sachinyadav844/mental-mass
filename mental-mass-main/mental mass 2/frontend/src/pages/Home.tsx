import { Link } from "react-router-dom";
import {
  ArrowRight,
  Brain,
  Activity,
  MessageSquare,
  TrendingUp,
  Bell,
  Sparkles,
  Play,
  CheckCircle,
  BarChart3,
  Users,
  Zap,
} from "lucide-react";
import { Button } from "@/components/ui/button";
import heroImage from "@/assets/hero.png";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";

const features = [
  {
    icon: Brain,
    title: "Emotion Detection",
    desc: "Real-time AI analysis of facial expressions.",
    color: "bg-lavender-soft text-lavender",
  },
  {
    icon: MessageSquare,
    title: "Sentiment Analysis",
    desc: "Understand your written emotional tone.",
    color: "bg-primary/10 text-primary",
  },
  {
    icon: TrendingUp,
    title: "Mood Scoring",
    desc: "Quantify your wellness on a 0–100 scale.",
    color: "bg-success-soft text-success",
  },
  {
    icon: Bell,
    title: "Risk Alerts",
    desc: "Proactive notifications for concerns.",
    color: "bg-destructive/10 text-destructive",
  },
  {
    icon: Sparkles,
    title: "AI Recommendations",
    desc: "Personalized wellness suggestions.",
    color: "bg-warning-soft text-warning",
  },
  {
    icon: BarChart3,
    title: "Analytics",
    desc: "Track trends and gain insights.",
    color: "bg-lavender-soft text-lavender",
  },
];

const stats = [
  { label: "Users Active", value: "10K+", icon: Users },
  { label: "Accuracy Rate", value: "94%", icon: Zap },
  { label: "Emotions Tracked", value: "7+", icon: Brain },
];

const Home = () => (
  <div className="page-container">
    <Navbar />

    {/* Hero Section */}
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-16 lg:py-24">
      <div className="grid lg:grid-cols-2 gap-12 items-center">
        <div className="space-y-6 animate-fade-in-up">
          <div className="inline-flex items-center gap-2 px-3 py-1.5 rounded-full bg-primary/10 border border-primary/20 text-primary text-sm font-medium">
            <span className="w-2 h-2 rounded-full bg-primary" />
            AI-Powered Mental Wellness
          </div>
          <h1 className="text-5xl sm:text-6xl lg:text-7xl font-display font-bold leading-tight">
            Monitor Your <span className="text-gradient">Mental Health</span>{" "}
            in Real-Time
          </h1>
          <p className="text-lg text-muted-foreground max-w-lg">
            Multimodal AI analysis of emotions through facial expressions and
            text sentiment. Get personalized wellness insights instantly.
          </p>
          <div className="flex flex-wrap gap-3 pt-2">
            <Button
              size="lg"
              className="btn-primary gap-2 text-base hover:scale-105 transition-transform"
              asChild
            >
              <Link to="/monitor">
                <Activity className="w-5 h-5" /> Get Started Free
              </Link>
            </Button>
            <Button
              size="lg"
              variant="outline"
              className="gap-2 text-base hover:bg-muted/80 transition-all"
              asChild
            >
              <Link to="/features">
                Learn More <ArrowRight className="w-4 h-4" />
              </Link>
            </Button>
          </div>
        </div>
        <div
          className="flex justify-center animate-fade-in"
          style={{ animationDelay: "200ms" }}
        >
          <div className="relative">
            <div className="absolute inset-0 bg-gradient-to-br from-primary/20 to-lavender/20 rounded-3xl blur-3xl" />
            <img
              src={heroImage}
              alt="Mental wellness AI brain"
              className="relative w-full max-w-lg rounded-3xl object-cover drop-shadow-2xl hover:scale-105 transition-transform duration-300"
            />
          </div>
        </div>
      </div>
    </section>

    {/* Stats Section */}
    <section className="bg-gradient-to-r from-primary/5 to-lavender/5 py-12">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="grid md:grid-cols-3 gap-8">
          {stats.map((stat, i) => {
            const Icon = stat.icon;
            return (
              <div
                key={stat.label}
                className="text-center animate-fade-in-up"
                style={{ animationDelay: `${i * 60}ms` }}
              >
                <div className="flex justify-center mb-3">
                  <div className="w-12 h-12 rounded-xl bg-primary/10 flex items-center justify-center">
                    <Icon className="w-6 h-6 text-primary" />
                  </div>
                </div>
                <p className="text-3xl font-display font-bold">{stat.value}</p>
                <p className="text-sm text-muted-foreground mt-1">
                  {stat.label}
                </p>
              </div>
            );
          })}
        </div>
      </div>
    </section>

    {/* Features Grid */}
    <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
      <div className="text-center mb-12 animate-fade-in-up">
        <h2 className="text-4xl font-display font-bold mb-3">
          Powerful Features,<span className="text-gradient"> Simple Design</span>
        </h2>
        <p className="text-lg text-muted-foreground">
          Everything you need for mental wellness
        </p>
      </div>
      <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-6">
        {features.map((f, i) => (
          <div
            key={f.title}
            className="feature-card p-6 group hover:shadow-lg hover:-translate-y-1 transition-all duration-300 animate-fade-in-up"
            style={{ animationDelay: `${i * 60}ms` }}
          >
            <div
              className={`w-12 h-12 rounded-xl ${f.color} flex items-center justify-center mb-4 group-hover:scale-110 transition-transform`}
            >
              <f.icon className="w-6 h-6" />
            </div>
            <h3 className="font-display font-bold text-lg mb-1">{f.title}</h3>
            <p className="text-muted-foreground text-sm">{f.desc}</p>
          </div>
        ))}
      </div>
    </section>

    {/* CTA Section */}
    <section className="bg-gradient-to-r from-primary/10 via-lavender/10 to-primary/5 py-16">
      <div className="max-w-2xl mx-auto px-4 text-center animate-fade-in-up">
        <h2 className="text-3xl font-display font-bold mb-3">
          Start Monitoring Your <span className="text-gradient">Wellness</span>
        </h2>
        <p className="text-muted-foreground mb-6">
          Free, private, and AI-powered. No credit card required.
        </p>
        <Button
          size="lg"
          className="btn-primary text-base hover:scale-105 transition-transform"
          asChild
        >
          <Link to="/monitor">Begin Now</Link>
        </Button>
      </div>
    </section>

    <Footer />
  </div>
);

export default Home;
