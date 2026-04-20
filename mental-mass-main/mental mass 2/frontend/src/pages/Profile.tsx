import { useEffect, useState } from "react";
import { User, Mail, Activity, TrendingUp, Shield, LogOut } from "lucide-react";
import { Link } from "react-router-dom";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Button } from "@/components/ui/button";
import api from "@/services/axiosConfig";
import { useAuth } from "@/context/AuthContext";

const Profile = () => {
  const { user, logout, isAuthenticated } = useAuth();
  const [profileUser, setProfileUser] = useState(user);

  useEffect(() => {
    const fetchProfile = async () => {
      try {
        const response = await api.get("/profile");
        if (response?.data?.success && response.data.user) {
          setProfileUser(response.data.user);
        }
      } catch (error) {
        console.error("Failed to fetch profile:", error);
      }
    };

    if (isAuthenticated) fetchProfile();
  }, [isAuthenticated]);

  const mockUser = profileUser ?? user ?? {
    name: "Demo User",
    email: "demo@mentalmass.ai",
    totalSessions: 24,
    avgScore: 64,
    riskLevel: "Low",
  };

  return (
    <div className="page-container">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 sm:px-6 py-10">
        <div className="mb-8 animate-fade-in-up">
          <h1 className="text-3xl font-display font-bold mb-1">My Profile</h1>
          <p className="text-muted-foreground">
            Manage your account and wellness summary
          </p>
        </div>

        {/* Avatar + Name */}
        <div className="glass-card p-8 text-center mb-6 animate-fade-in-up">
          <div className="w-20 h-20 rounded-full gradient-primary flex items-center justify-center mx-auto mb-4 text-3xl font-display font-bold text-primary-foreground shadow-lg shadow-primary/25">
            {mockUser.name[0].toUpperCase()}
          </div>
          <h2 className="text-2xl font-display font-bold">{mockUser.name}</h2>
          <p className="text-muted-foreground flex items-center justify-center gap-1.5 mt-1">
            <Mail className="w-4 h-4" />
            {mockUser.email}
          </p>
        </div>

        {/* Stats */}
        <div className="grid grid-cols-3 gap-4 mb-6">
          {[
            {
              label: "Total Sessions",
              value: mockUser.totalSessions ?? 24,
              icon: Activity,
              color: "bg-primary/10 text-primary",
            },
            {
              label: "Avg. Score",
              value: mockUser.avgScore ?? 64,
              icon: TrendingUp,
              color: "bg-success-soft text-success",
            },
            {
              label: "Risk Level",
              value: mockUser.riskLevel ?? "Low",
              icon: Shield,
              color: "bg-lavender-soft text-lavender",
            },
          ].map((s, i) => (
            <div
              key={s.label}
              className="stat-card p-4 text-center animate-fade-in-up"
              style={{ animationDelay: `${i * 80}ms` }}
            >
              <div
                className={`w-9 h-9 rounded-xl ${s.color} flex items-center justify-center mx-auto mb-2`}
              >
                <s.icon className="w-5 h-5" />
              </div>
              <p className="text-xl font-display font-bold">{s.value}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{s.label}</p>
            </div>
          ))}
        </div>

        {/* Actions */}
        <div
          className="glass-card p-6 space-y-3 animate-fade-in-up"
          style={{ animationDelay: "240ms" }}
        >
          <Button
            variant="outline"
            className="w-full justify-start gap-3"
            asChild
          >
            <Link to="/settings">
              <Shield className="w-4 h-4 text-lavender" /> Privacy & Settings
            </Link>
          </Button>
          <Button
            variant="outline"
            className="w-full justify-start gap-3"
            asChild
          >
            <Link to="/dashboard">
              <Activity className="w-4 h-4 text-primary" /> View Dashboard
            </Link>
          </Button>
          {isAuthenticated && (
            <Button
              variant="outline"
              className="w-full justify-start gap-3 text-destructive hover:text-destructive"
              onClick={logout}
            >
              <LogOut className="w-4 h-4" /> Sign Out
            </Button>
          )}
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Profile;
