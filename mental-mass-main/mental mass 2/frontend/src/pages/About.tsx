import { Brain, Heart, Shield, Zap } from "lucide-react";
import { Link } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";

const values = [
  {
    icon: Heart,
    title: "Empathy First",
    desc: "Designed with compassion for mental health.",
    color: "bg-destructive/10 text-destructive",
  },
  {
    icon: Shield,
    title: "Privacy by Design",
    desc: "Your data is secure. Always encrypted.",
    color: "bg-success-soft text-success",
  },
  {
    icon: Zap,
    title: "AI-Powered",
    desc: "State-of-the-art models for accuracy.",
    color: "bg-warning-soft text-warning",
  },
  {
    icon: Brain,
    title: "Inclusive",
    desc: "Built for everyone seeking wellness.",
    color: "bg-lavender-soft text-lavender",
  },
];

const About = () => (
  <div className="page-container">
    <Navbar />
    <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-16">
      {/* Hero */}
      <div className="text-center mb-16 animate-fade-in-up">
        <div className="w-16 h-16 rounded-2xl gradient-primary flex items-center justify-center mx-auto mb-6 shadow-lg shadow-primary/25">
          <Brain className="w-9 h-9 text-primary-foreground" />
        </div>
        <h1 className="text-5xl font-display font-bold mb-4">
          About<span className="text-gradient"> MENTALMASS</span>
        </h1>
        <p className="text-lg text-muted-foreground">
          AI-driven mental wellness monitoring for everyone.
        </p>
      </div>

      {/* Mission */}
      <div
        className="glass-card p-8 mb-12 animate-fade-in-up"
        style={{ animationDelay: "100ms" }}
      >
        <h2 className="text-2xl font-display font-bold mb-4">Our Mission</h2>
        <p className="text-muted-foreground leading-relaxed mb-4">
          Mental health challenges often go unnoticed until they become severe.
          We created MENTALMASS to enable continuous, accessible wellness
          monitoring using AI.
        </p>
        <p className="text-muted-foreground leading-relaxed">
          By analyzing emotions through facial expressions and text, we help
          people catch concerns early and take proactive steps toward better
          mental health.
        </p>
      </div>

      {/* Values */}
      <h2 className="text-2xl font-display font-bold mb-6 animate-fade-in-up">
        Our Values
      </h2>
      <div className="grid sm:grid-cols-2 gap-6 mb-12">
        {values.map((v, i) => (
          <div
            key={v.title}
            className="feature-card p-6 group hover:shadow-lg hover:-translate-y-1 transition-all animate-fade-in-up"
            style={{ animationDelay: `${i * 80}ms` }}
          >
            <div
              className={`w-10 h-10 rounded-xl ${v.color} flex items-center justify-center mb-3 group-hover:scale-110 transition-transform`}
            >
              <v.icon className="w-5 h-5" />
            </div>
            <h3 className="font-display font-bold text-lg mb-1">{v.title}</h3>
            <p className="text-sm text-muted-foreground">{v.desc}</p>
          </div>
        ))}
      </div>

      {/* CTA */}
      <div
        className="text-center animate-fade-in-up"
        style={{ animationDelay: "400ms" }}
      >
        <Button size="lg" className="btn-primary gap-2 text-base" asChild>
          <Link to="/monitor">Start Your Journey</Link>
        </Button>
      </div>
    </div>
    <Footer />
  </div>
);

export default About;
