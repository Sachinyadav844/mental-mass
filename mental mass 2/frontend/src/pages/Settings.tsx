import { useState } from "react";
import {
  Settings as SettingsIcon,
  Bell,
  Moon,
  Trash2,
  Shield,
  AlertTriangle,
} from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import { Switch } from "@/components/ui/switch";
import { Label } from "@/components/ui/label";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog";

const Settings = () => {
  const [notifications, setNotifications] = useState(true);
  const [darkMode, setDarkMode] = useState(false);
  const [emailAlerts, setEmailAlerts] = useState(true);
  const { toast } = useToast();

  const save = () =>
    toast({
      title: "Settings saved",
      description: "Your preferences have been updated.",
    });

  return (
    <div className="page-container">
      <Navbar />
      <div className="max-w-2xl mx-auto px-4 sm:px-6 py-10">
        <div className="mb-8 animate-fade-in-up">
          <div className="flex items-center gap-3 mb-2">
            <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center">
              <SettingsIcon className="w-5 h-5 text-primary-foreground" />
            </div>
            <h1 className="text-3xl font-display font-bold">Settings</h1>
          </div>
          <p className="text-muted-foreground ml-12">
            Customize your MENTALMASS experience
          </p>
        </div>

        <div
          className="space-y-4 animate-fade-in-up"
          style={{ animationDelay: "100ms" }}
        >
          {/* Appearance */}
          <div className="glass-card p-6 space-y-4">
            <h2 className="font-display font-semibold flex items-center gap-2">
              <Moon className="w-4 h-4 text-lavender" /> Appearance
            </h2>
            <div className="flex items-center justify-between">
              <div>
                <Label>Dark Mode</Label>
                <p className="text-xs text-muted-foreground">
                  Switch to dark theme
                </p>
              </div>
              <Switch checked={darkMode} onCheckedChange={setDarkMode} />
            </div>
          </div>

          {/* Notifications */}
          <div className="glass-card p-6 space-y-4">
            <h2 className="font-display font-semibold flex items-center gap-2">
              <Bell className="w-4 h-4 text-primary" /> Notifications
            </h2>
            <div className="flex items-center justify-between">
              <div>
                <Label>Push Notifications</Label>
                <p className="text-xs text-muted-foreground">
                  Receive in-app notifications
                </p>
              </div>
              <Switch
                checked={notifications}
                onCheckedChange={setNotifications}
              />
            </div>
            <div className="flex items-center justify-between">
              <div>
                <Label>Email Alerts</Label>
                <p className="text-xs text-muted-foreground">
                  Get notified via email for high-risk alerts
                </p>
              </div>
              <Switch checked={emailAlerts} onCheckedChange={setEmailAlerts} />
            </div>
          </div>

          {/* Privacy */}
          <div className="glass-card p-6 space-y-3">
            <h2 className="font-display font-semibold flex items-center gap-2">
              <Shield className="w-4 h-4 text-success" /> Privacy
            </h2>
            <p className="text-sm text-muted-foreground">
              Your data is encrypted and never shared with third parties. All
              emotion analysis is processed locally when possible.
            </p>
            <div className="flex gap-2 flex-wrap text-xs">
              <span className="px-2 py-1 rounded-full bg-success-soft text-success border border-success/20">
                🔒 End-to-End Encrypted
              </span>
              <span className="px-2 py-1 rounded-full bg-success-soft text-success border border-success/20">
                ✅ GDPR Compliant
              </span>
              <span className="px-2 py-1 rounded-full bg-success-soft text-success border border-success/20">
                🚫 No Data Selling
              </span>
            </div>
          </div>

          <Button className="btn-primary w-full" onClick={save}>
            Save Settings
          </Button>

          {/* Danger Zone */}
          <div className="glass-card p-6 border-destructive/30">
            <h2 className="font-display font-semibold flex items-center gap-2 text-destructive mb-3">
              <AlertTriangle className="w-4 h-4" /> Danger Zone
            </h2>
            <p className="text-sm text-muted-foreground mb-4">
              Permanently delete your account and all associated data. This
              action cannot be undone.
            </p>
            <AlertDialog>
              <AlertDialogTrigger asChild>
                <Button variant="destructive" size="sm" className="gap-2">
                  <Trash2 className="w-4 h-4" /> Delete Account
                </Button>
              </AlertDialogTrigger>
              <AlertDialogContent>
                <AlertDialogHeader>
                  <AlertDialogTitle>Are you absolutely sure?</AlertDialogTitle>
                  <AlertDialogDescription>
                    This will permanently delete your MENTALMASS account and all
                    your wellness data including mood history, journal entries,
                    and assessment results.
                  </AlertDialogDescription>
                </AlertDialogHeader>
                <AlertDialogFooter>
                  <AlertDialogCancel>Cancel</AlertDialogCancel>
                  <AlertDialogAction className="bg-destructive text-destructive-foreground hover:bg-destructive/90">
                    Delete Account
                  </AlertDialogAction>
                </AlertDialogFooter>
              </AlertDialogContent>
            </AlertDialog>
          </div>
        </div>
      </div>
      <Footer />
    </div>
  );
};

export default Settings;
