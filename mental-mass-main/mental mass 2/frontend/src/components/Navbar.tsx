import { useState } from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Brain,
  Menu,
  X,
  ChevronDown,
  User,
  LogOut,
  Settings,
  LayoutDashboard,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";

const navLinks = [
  { href: "/", label: "Home" },
  { href: "/about", label: "About" },
  { href: "/features", label: "Features" },
  { href: "/monitor", label: "Monitor" },
  { href: "/dashboard", label: "Dashboard" },
  { href: "/journal", label: "Journal" },
  { href: "/assessment", label: "Assessment" },
];

const Navbar = () => {
  const [open, setOpen] = useState(false);
  const { pathname } = useLocation();
  const { user, logout, isAuthenticated } = useAuth();

  return (
    <nav className="sticky top-0 z-50 bg-card/80 backdrop-blur-md border-b border-border/60 shadow-sm">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <Link
            to="/"
            className="flex items-center gap-2 font-display font-800 text-xl"
          >
            <div className="w-8 h-8 rounded-lg gradient-primary flex items-center justify-center">
              <Brain className="w-5 h-5 text-primary-foreground" />
            </div>
            <span className="text-gradient font-display font-bold text-lg">
              MENTALMASS
            </span>
          </Link>

          {/* Desktop links */}
          <div className="hidden lg:flex items-center gap-1">
            {navLinks.map((l) => (
              <Link
                key={l.href}
                to={l.href}
                className={`px-3 py-1.5 rounded-lg text-sm font-medium transition-all duration-300 ${
                  pathname === l.href
                    ? "text-primary bg-primary/10 font-semibold"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/70"
                }`}
              >
                {l.label}
              </Link>
            ))}
          </div>

          {/* Right side */}
          <div className="hidden lg:flex items-center gap-3">
            {isAuthenticated && user ? (
              <DropdownMenu>
                <DropdownMenuTrigger asChild>
                  <Button
                    variant="ghost"
                    className="flex items-center gap-2 h-9"
                  >
                    <div className="w-7 h-7 rounded-full gradient-primary flex items-center justify-center text-primary-foreground text-xs font-bold">
                      {user.name[0].toUpperCase()}
                    </div>
                    <span className="text-sm font-medium">{user.name}</span>
                    <ChevronDown className="w-3.5 h-3.5 text-muted-foreground" />
                  </Button>
                </DropdownMenuTrigger>
                <DropdownMenuContent align="end" className="w-48">
                  <DropdownMenuItem asChild>
                    <Link to="/profile" className="flex items-center gap-2">
                      <User className="w-4 h-4" /> Profile
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/dashboard" className="flex items-center gap-2">
                      <LayoutDashboard className="w-4 h-4" /> Dashboard
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuItem asChild>
                    <Link to="/settings" className="flex items-center gap-2">
                      <Settings className="w-4 h-4" /> Settings
                    </Link>
                  </DropdownMenuItem>
                  <DropdownMenuSeparator />
                  <DropdownMenuItem
                    onClick={logout}
                    className="text-destructive flex items-center gap-2"
                  >
                    <LogOut className="w-4 h-4" /> Logout
                  </DropdownMenuItem>
                </DropdownMenuContent>
              </DropdownMenu>
            ) : (
              <>
                <Button variant="ghost" size="sm" asChild>
                  <Link to="/login">Login</Link>
                </Button>
                <Button size="sm" className="btn-primary" asChild>
                  <Link to="/register">Get Started</Link>
                </Button>
              </>
            )}
          </div>

          {/* Mobile burger */}
          <button
            className="lg:hidden p-2 rounded-md text-muted-foreground hover:text-foreground"
            onClick={() => setOpen(!open)}
          >
            {open ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
        </div>
      </div>

      {/* Mobile drawer */}
      {open && (
        <div className="lg:hidden border-t border-border/60 bg-card/95 backdrop-blur-md animate-fade-in">
          <div className="px-4 py-4 space-y-1">
            {navLinks.map((l) => (
              <Link
                key={l.href}
                to={l.href}
                onClick={() => setOpen(false)}
                className={`block px-3 py-2.5 rounded-md text-sm font-medium transition-colors ${
                  pathname === l.href
                    ? "text-primary bg-primary/8 font-semibold"
                    : "text-muted-foreground hover:text-foreground"
                }`}
              >
                {l.label}
              </Link>
            ))}
            <div className="pt-3 border-t border-border/60 flex gap-2">
              {isAuthenticated ? (
                <Button
                  variant="outline"
                  size="sm"
                  onClick={logout}
                  className="w-full"
                >
                  Logout
                </Button>
              ) : (
                <>
                  <Button
                    variant="outline"
                    size="sm"
                    asChild
                    className="flex-1"
                  >
                    <Link to="/login" onClick={() => setOpen(false)}>
                      Login
                    </Link>
                  </Button>
                  <Button size="sm" className="btn-primary flex-1" asChild>
                    <Link to="/register" onClick={() => setOpen(false)}>
                      Register
                    </Link>
                  </Button>
                </>
              )}
            </div>
          </div>
        </div>
      )}
    </nav>
  );
};

export default Navbar;
