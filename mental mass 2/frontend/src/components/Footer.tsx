import { Brain, Mail, Github, Linkedin } from "lucide-react";
import { Link } from "react-router-dom";

const Footer = () => (
  <footer className="bg-card border-t border-border/40 py-12 mt-auto">
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
      <div className="grid md:grid-cols-4 gap-8 mb-8">
        {/* Brand */}
        <div className="md:col-span-1">
          <div className="flex items-center gap-2 mb-2">
            <div className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center">
              <Brain className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="font-display font-bold text-lg text-gradient">
              MENTALMASS
            </span>
          </div>
          <p className="text-xs text-muted-foreground">
            AI wellness monitoring
          </p>
        </div>

        {/* Links */}
        <div>
          <h4 className="text-sm font-semibold mb-3 text-foreground">
            Product
          </h4>
          <div className="space-y-2 text-sm text-muted-foreground">
            <Link
              to="/"
              className="hover:text-primary transition-colors block"
            >
              Home
            </Link>
            <Link
              to="/features"
              className="hover:text-primary transition-colors block"
            >
              Features
            </Link>
            <Link
              to="/monitor"
              className="hover:text-primary transition-colors block"
            >
              Monitor
            </Link>
          </div>
        </div>

        {/* Company */}
        <div>
          <h4 className="text-sm font-semibold mb-3 text-foreground">
            Company
          </h4>
          <div className="space-y-2 text-sm text-muted-foreground">
            <Link
              to="/about"
              className="hover:text-primary transition-colors block"
            >
              About
            </Link>
            <a
              href="mailto:contact@mentalmass.ai"
              className="hover:text-primary transition-colors block"
            >
              Contact
            </a>
          </div>
        </div>

        {/* Social */}
        <div>
          <h4 className="text-sm font-semibold mb-3 text-foreground">
            Connect
          </h4>
          <div className="flex gap-3">
            <a
              href="https://github.com"
              target="_blank"
              rel="noopener noreferrer"
              className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center text-muted-foreground hover:text-primary hover:bg-primary/10 transition-colors"
            >
              <Github className="w-4 h-4" />
            </a>
            <a
              href="https://linkedin.com"
              target="_blank"
              rel="noopener noreferrer"
              className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center text-muted-foreground hover:text-primary hover:bg-primary/10 transition-colors"
            >
              <Linkedin className="w-4 h-4" />
            </a>
            <a
              href="mailto:contact@mentalmass.ai"
              className="w-9 h-9 rounded-lg bg-muted flex items-center justify-center text-muted-foreground hover:text-primary hover:bg-primary/10 transition-colors"
            >
              <Mail className="w-4 h-4" />
            </a>
          </div>
        </div>
      </div>

      <div className="pt-8 border-t border-border/40 text-center text-xs text-muted-foreground">
        © 2026 MENTALMASS. All rights reserved. @mentalmass_sneha
      </div>
    </div>
  </footer>
);

export default Footer;
