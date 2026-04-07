import { ClipboardList } from "lucide-react";
import Navbar from "@/components/Navbar";
import Footer from "@/components/Footer";
import SelfAssessment from "@/components/SelfAssessment";

const Assessment = () => (
  <div className="page-container">
    <Navbar />
    <div className="max-w-2xl mx-auto px-4 sm:px-6 py-12">
      {/* Header */}
      <div className="text-center mb-10 animate-fade-in-up">
        <div className="w-12 h-12 rounded-xl gradient-primary flex items-center justify-center mx-auto mb-4 shadow-lg shadow-primary/25">
          <ClipboardList className="w-6 h-6 text-primary-foreground" />
        </div>
        <h1 className="text-4xl font-display font-bold mb-2">
          Mental Wellness Check
        </h1>
        <p className="text-muted-foreground">
          Quick 2-minute assessment. 5 questions. Personalized insights.
        </p>
      </div>

      {/* Assessment Card */}
      <div
        className="glass-card p-8 animate-fade-in-up"
        style={{ animationDelay: "100ms" }}
      >
        <div className="mb-6 p-4 rounded-xl bg-primary/5 border border-primary/15">
          <p className="text-sm text-primary font-medium">
            📋 How often have these feelings bothered you in the last 2 weeks?
          </p>
        </div>
        <SelfAssessment />
      </div>
    </div>
    <Footer />
  </div>
);

export default Assessment;
