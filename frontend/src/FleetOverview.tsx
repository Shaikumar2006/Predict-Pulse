import { useState, useEffect } from "react";
import { PieChart, Pie, Cell, ResponsiveContainer } from "recharts";
import KpiCard from "./KpiCard";

type Contribution = { label: string; pctAboveBaseline: number };
type MachineRecord = {
  index: number; severity: number; healthScore: number; weeklyCostRs: number;
  efficiencyLossPct: number; daysToCritical: number | null; contributions: Contribution[];
};
type Machine = {
  id: string; name: string; faultType: string; recordingIntervalMinutes: number;
  gracePeriodSnapshots: number; moderateThreshold: number; criticalThreshold: number;
  ratedPowerKw: number; tariffRsPerKwh: number; scheduledRepairCostRs: number; records: MachineRecord[];
};

type Status = "Critical" | "Warning" | "Healthy";
const statusColors: Record<Status, string> = { Critical: "#EF4444", Warning: "#F59E0B", Healthy: "#22C55E" };

function statusFor(m: Machine, record: MachineRecord, index: number): Status {
  if (index < m.gracePeriodSnapshots) return "Healthy";
  if (record.severity > m.criticalThreshold) return "Critical";
  if (record.severity > m.moderateThreshold) return "Warning";
  return "Healthy";
}

type FleetOverviewProps = { machines: Machine[] };

function FleetOverview({ machines }: FleetOverviewProps) {
  const [fraction, setFraction] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    if (!isPlaying) return;
    const interval = setInterval(() => {
      setFraction((prev) => {
        if (prev >= 1) { setIsPlaying(false); return 1; }
        return Math.min(prev + 0.002, 1);
      });
    }, 30);
    return () => clearInterval(interval);
  }, [isPlaying]);

  const rows = machines.map((m) => {
    const idx = Math.min(Math.floor(fraction * (m.records.length - 1)), m.records.length - 1);
    const record = m.records[Math.max(idx, 0)];
    return { machine: m, record, status: statusFor(m, record, idx) };
  });

  const healthyCount = rows.filter((r) => r.status === "Healthy").length;
  const warningCount = rows.filter((r) => r.status === "Warning").length;
  const criticalCount = rows.filter((r) => r.status === "Critical").length;
  const totalCostAtRisk = rows.reduce((sum, r) => sum + r.record.weeklyCostRs, 0);

  const pieData = [
    { name: "Healthy", value: healthyCount, color: statusColors.Healthy },
    { name: "Warning", value: warningCount, color: statusColors.Warning },
    { name: "Critical", value: criticalCount, color: statusColors.Critical },
  ].filter((d) => d.value > 0);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-primary text-xl font-semibold">Plant overview</h2>
        <p className="text-secondary text-sm mt-1">
          Real machine health across every validated bearing. Drag or play to see each bearing's recorded condition at the same relative point in its life.
        </p>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={() => { if (fraction >= 1) setFraction(0); setIsPlaying((p) => !p); }}
          className="bg-info text-background font-semibold px-4 py-2 text-sm whitespace-nowrap"
        >
          {isPlaying ? "Pause" : "Play"}
        </button>
        <input type="range" min={0} max={1} step={0.001} value={fraction}
          onChange={(e) => { setIsPlaying(false); setFraction(Number(e.target.value)); }} className="w-full" />
        <span className="text-secondary text-sm font-mono whitespace-nowrap">{Math.round(fraction * 100)}%</span>
      </div>

      <div className="grid grid-cols-4 gap-4">
        <KpiCard label="Machines monitored" value={String(machines.length)} accentColor="#38BDF8" />
        <KpiCard label="Healthy" value={String(healthyCount)} accentColor="#22C55E" />
        <KpiCard label="Needs attention" value={String(warningCount + criticalCount)} accentColor="#F59E0B" />
        <KpiCard label="Estimated cost at risk" value={`₹${totalCostAtRisk}/week`} accentColor="#EF4444" />
      </div>

      <div className="grid grid-cols-2 gap-4">
        <div className="bg-card border border-border p-5">
          <p className="text-primary font-semibold mb-4">Fleet health breakdown</p>
          <div className="flex items-center gap-6">
            <div style={{ width: 140, height: 140 }}>
              <ResponsiveContainer>
                <PieChart>
                  <Pie data={pieData} dataKey="value" innerRadius={40} outerRadius={65} paddingAngle={pieData.length > 1 ? 4 : 0}>
                    {pieData.map((d) => <Cell key={d.name} fill={d.color} />)}
                  </Pie>
                </PieChart>
              </ResponsiveContainer>
            </div>
            <div className="space-y-2">
              {(["Healthy", "Warning", "Critical"] as Status[]).map((s) => (
                <div key={s} className="flex items-center gap-2 text-sm">
                  <div className="w-2 h-2" style={{ backgroundColor: statusColors[s] }} />
                  <span className="text-primary">{s}</span>
                  <span className="text-secondary font-mono">{s === "Healthy" ? healthyCount : s === "Warning" ? warningCount : criticalCount}</span>
                </div>
              ))}
            </div>
          </div>
        </div>

        <div className="bg-card border border-border p-5">
          <p className="text-primary font-semibold mb-1">Machines at a glance</p>
          <p className="text-secondary text-xs mb-3">Select a machine from the sidebar to open its live detail view.</p>
          <div className="space-y-1">
            {rows.map(({ machine, record, status }) => (
              <div key={machine.id} className="flex items-center justify-between py-2 border-b border-border last:border-0">
                <div>
                  <p className="text-primary text-sm font-medium">{machine.name}</p>
                  <p className="text-secondary text-xs">{machine.faultType}</p>
                </div>
                <div className="flex items-center gap-4">
                  <span className="text-secondary text-xs font-mono">{record.healthScore}/100</span>
                  <span className="text-xs font-semibold" style={{ color: statusColors[status] }}>{status}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default FleetOverview;