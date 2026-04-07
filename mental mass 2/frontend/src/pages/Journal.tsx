import { BookOpen } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import JournalHistory from "@/components/JournalHistory";

const Journal = () => (
  <div className="page-container">
    <Navbar />
    <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 py-10">
      <div className="mb-8 animate-fade-in-up">
        <div className="flex items-center gap-3 mb-2">
          <div className="w-9 h-9 rounded-xl gradient-primary flex items-center justify-center">
            <BookOpen className="w-5 h-5 text-primary-foreground" />
          </div>
          <h1 className="text-3xl font-display font-bold">Mood Journal</h1>
        </div>
        <p className="text-muted-foreground ml-12">
          Review your emotional history and track wellness trends over time.
        </p>
      </div>

      <div
        className="glass-card p-6 animate-fade-in-up"
        style={{ animationDelay: "100ms" }}
      >
        <JournalHistory />
      </div>
    </div>
    <Footer />
  </div>
);

export default Journal;
