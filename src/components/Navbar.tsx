import { useLocation, Link } from "react-router-dom";
import { EnvironmentSwitcher } from "@/components/EnvironmentSwitcher";

export function Navbar() {
  const location = useLocation();
  const isDashboard = location.pathname === "/";

  return (
    <div className="w-full">
      <nav className="flex items-center px-6 h-14 bg-slate-900 border-b border-slate-800">
        {/* Left: Logo + Wordmark */}
        <div className="flex items-center gap-2 flex-shrink-0">
          <span className="text-xl">🚗</span>
          <span className="font-semibold text-white text-lg">DriveTrack</span>
        </div>

        {/* Center: Navigation Tabs */}
        <div className="flex items-center gap-1 mx-auto">
          <Link
            to="/"
            className={
              isDashboard
                ? "bg-emerald-900/40 text-emerald-400 rounded-full px-3 py-1 text-sm font-medium"
                : "text-slate-400 hover:text-slate-200 px-3 py-1 text-sm font-medium"
            }
          >
            Dashboard
          </Link>
          <span className="text-slate-500 cursor-default px-3 py-1 text-sm font-medium">
            Bookings
          </span>
        </div>

        {/* Right: Environment Switcher */}
        <div className="flex-shrink-0">
          <EnvironmentSwitcher />
        </div>
      </nav>
    </div>
  );
}
