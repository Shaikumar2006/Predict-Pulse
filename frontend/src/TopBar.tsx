import { Search, Bell } from "lucide-react";

function TopBar() {
  return (
    <div className="border-b border-border px-6 py-4 flex items-center justify-between">
      <div className="flex items-center gap-2 text-secondary text-sm">
        <span>OVERVIEW</span> <span>›</span> <span className="text-primary font-medium">Dashboard</span>
      </div>
      <div className="flex items-center gap-4">
        <div className="flex items-center gap-2 bg-card border border-border rounded-lg px-3 py-1.5 text-secondary text-sm">
          🔍 Search
        </div>
        <span className="text-secondary">🔔</span>
      </div>
    </div>
  );
}

export default TopBar;