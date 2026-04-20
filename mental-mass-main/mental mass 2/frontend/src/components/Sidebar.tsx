import { Link, useLocation } from "react-router-dom";
import {
  Brain,
  LayoutDashboard,
  Activity,
  BookOpen,
  ClipboardList,
  User,
  Settings,
  ChevronLeft,
  ChevronRight,
} from "lucide-react";
import { useState } from "react";
import { cn } from "@/lib/utils";

const links = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/monitor", label: "Monitor", icon: Activity },
  { href: "/journal", label: "Journal", icon: BookOpen },
  { href: "/assessment", label: "Assessment", icon: ClipboardList },
  { href: "/profile", label: "Profile", icon: User },
  { href: "/settings", label: "Settings", icon: Settings },
];

const Sidebar = () => {
  const [collapsed, setCollapsed] = useState(false);
  const { pathname } = useLocation();

  return (
    <aside
      className={cn(
        "hidden md:flex flex-col h-screen sticky top-0 transition-all duration-300 sidebar-nav text-primary-foreground",
        collapsed ? "w-16" : "w-60",
      )}
    >
      <div className="flex items-center gap-2 px-4 py-5 border-b border-white/10">
        <div className="w-8 h-8 rounded-lg bg-white/20 flex items-center justify-center flex-shrink-0">
          <Brain className="w-5 h-5" />
        </div>
        {!collapsed && (
          <span className="font-display font-bold text-sm">MENTALMASS</span>
        )}
      </div>

      <nav className="flex-1 px-2 py-4 space-y-1 overflow-y-auto">
        {links.map(({ href, label, icon: Icon }) => {
          const active = pathname === href;
          return (
            <Link
              key={href}
              to={href}
              className={cn(
                "flex items-center gap-3 px-3 py-2.5 rounded-lg text-sm font-medium transition-all",
                active
                  ? "bg-white/20 text-white shadow-sm"
                  : "text-white/70 hover:bg-white/10 hover:text-white",
              )}
              title={collapsed ? label : undefined}
            >
              <Icon className="w-4.5 h-4.5 flex-shrink-0" />
              {!collapsed && <span>{label}</span>}
            </Link>
          );
        })}
      </nav>

      <button
        onClick={() => setCollapsed(!collapsed)}
        className="flex items-center justify-center p-3 border-t border-white/10 text-white/60 hover:text-white hover:bg-white/10 transition-colors"
      >
        {collapsed ? (
          <ChevronRight className="w-4 h-4" />
        ) : (
          <ChevronLeft className="w-4 h-4" />
        )}
      </button>
    </aside>
  );
};

export default Sidebar;
