type Machine = { id: string; name: string; faultType: string };

type SidebarProps = {
  machines: Machine[];
  selectedId: string | null;
  view: "dashboard" | string;
  onSelectMachine: (id: string) => void;
  onGoToDashboard: () => void;
};

const disabledItems = ["Anomalies", "Maintenance", "Reports", "Settings"];

function Sidebar({ machines, view, onSelectMachine, onGoToDashboard }: SidebarProps) {
  return (
    <div className="w-64 bg-panel border-r border-border h-screen flex flex-col p-4 overflow-y-auto">
      <div className="flex items-center gap-2 mb-8">
        <div className="w-8 h-8 bg-info flex items-center justify-center text-background font-mono font-bold">P</div>
        <div>
          <p className="text-primary font-semibold text-sm">PredictPulse</p>
          <p className="text-secondary text-xs">Industrial intelligence</p>
        </div>
      </div>

      <button
        onClick={onGoToDashboard}
        className={`w-full text-left px-3 py-2 mb-6 border-l-4 ${
          view === "dashboard" ? "border-info text-info bg-card" : "border-transparent text-secondary hover:text-primary"
        }`}
      >
        <span className="text-sm font-medium">Dashboard</span>
      </button>

      <div className="space-y-2 mb-6">
        {machines.map((m) => (
          <button
            key={m.id}
            onClick={() => onSelectMachine(m.id)}
            className={`w-full text-left p-3 border-l-4 ${
              view === m.id ? "border-info bg-card" : "border-transparent hover:bg-card/50"
            }`}
          >
            <p className="text-primary text-sm font-medium">{m.name}</p>
            <p className="text-secondary text-xs mt-0.5">{m.faultType}</p>
          </button>
        ))}
      </div>

      <div className="mt-auto pt-4 border-t border-border">
        {disabledItems.map((label) => (
          <div key={label} className="text-secondary/40 px-3 py-1.5 text-sm cursor-not-allowed">
            {label}
          </div>
        ))}
      </div>
    </div>
  );
}

export default Sidebar;