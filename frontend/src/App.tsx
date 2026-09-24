import { useState, useEffect } from "react";
import Sidebar from "./Sidebar";
import TopBar from "./TopBar";
import KpiCard from "./KpiCard";
import HealthChart from "./HealthChart";
import AlertPanel from "./AlertPanel";
import InsightsPanel from "./InsightsPanel";
import FleetOverview from "./FleetOverview";

type Contribution = { label: string; pctAboveBaseline: number };

type Record = {
  index: number;
  severity: number;
  healthScore: number;
  weeklyCostRs: number;
  efficiencyLossPct: number;
  daysToCritical: number | null;
  contributions: Contribution[];
};

type Machine = {
  id: string;
  name: string;
  faultType: string;
  recordingIntervalMinutes: number;
  gracePeriodSnapshots: number;
  moderateThreshold: number;
  criticalThreshold: number;
  ratedPowerKw: number;
  tariffRsPerKwh: number;
  scheduledRepairCostRs: number;
  records: Record[];
};

type MachineData = { machines: Machine[] };
type Trend = { text: string; isGood: boolean };

function downsample(points: { index: number; healthScore: number }[], maxPoints = 300) {
  if (points.length <= maxPoints) return points;
  const step = points.length / maxPoints;
  const result: typeof points = [];
  for (let i = 0; i < maxPoints; i++) result.push(points[Math.floor(i * step)]);
  result.push(points[points.length - 1]);
  return result;
}

function computeTrend(
  records: Record[], currentIndex: number,
  key: "healthScore" | "weeklyCostRs" | "efficiencyLossPct", higherIsGood: boolean
): Trend | null {
  const lookback = Math.min(20, currentIndex);
  if (lookback < 1) return null;
  const past = records[currentIndex - lookback];
  const curr = records[currentIndex];
  const diff = curr[key] - past[key];
  if (Math.abs(diff) < 0.01) return null;
  const pct = past[key] !== 0 ? (diff / Math.abs(past[key])) * 100 : 0;
  const isUp = diff > 0;
  const isGood = higherIsGood ? isUp : !isUp;
  return { text: `${isUp ? "↑" : "↓"} ${Math.abs(pct).toFixed(1)}% vs ${lookback} steps ago`, isGood };
}

function App() {
  const [data, setData] = useState<MachineData | null>(null);
  const [view, setView] = useState<"dashboard" | string>("dashboard");
  const [selectedMachineId, setSelectedMachineId] = useState<string | null>(null);
  const [timeIndex, setTimeIndex] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);

  useEffect(() => {
    fetch("/machine_data.json")
      .then((res) => res.json())
      .then((json: MachineData) => setData(json));
  }, []);

  const machine = data?.machines.find((m) => m.id === selectedMachineId) ?? null;

  useEffect(() => {
    if (machine) setTimeIndex(machine.records.length - 1);
  }, [machine]);

  useEffect(() => {
    if (!isPlaying || !machine) return;
    const interval = setInterval(() => {
      setTimeIndex((prev) => {
        if (prev >= machine.records.length - 1) { setIsPlaying(false); return prev; }
        return prev + 1;
      });
    }, 30);
    return () => clearInterval(interval);
  }, [isPlaying, machine]);

  if (!data) {
    return <div className="bg-background min-h-screen text-primary p-8">Loading...</div>;
  }

  const safeIndex = machine ? Math.min(timeIndex, machine.records.length - 1) : 0;
  const current = machine ? machine.records[safeIndex] : null;
  const chartPoints = machine
    ? downsample(machine.records.slice(0, safeIndex + 1).map((r) => ({ index: r.index, healthScore: r.healthScore })))
    : [];

  return (
    <div className="bg-background min-h-screen flex">
      <Sidebar
        machines={data.machines}
        selectedId={selectedMachineId}
        view={view}
        onSelectMachine={(id) => { setSelectedMachineId(id); setView(id); setIsPlaying(false); }}
        onGoToDashboard={() => setView("dashboard")}
      />

      <div className="flex-1">
        <TopBar />

        <div className="p-8 space-y-6">
          {view === "dashboard" ? (
            <>
              <div>
                <h1 className="text-primary text-2xl font-semibold">Predictive Maintenance & Energy-Cost Advisor</h1>
                <p className="text-secondary text-sm mt-1">
                  Real vibration-based failure detection, validated across 3 bearings on the same industrial test rig.
                </p>
              </div>
              <FleetOverview machines={data.machines} />
            </>
          ) : machine && current ? (
            <>
              <div>
                <h1 className="text-primary text-2xl font-semibold">{machine.name}</h1>
                <p className="text-secondary text-sm mt-1">{machine.faultType}</p>
              </div>

              <div>
                <p className="text-primary font-semibold mb-1">Live monitoring replay</p>
                <p className="text-secondary text-sm mb-2">
                  Drag to simulate time passing, or press Play. Each step = {machine.recordingIntervalMinutes} minutes of real recorded data.
                </p>
                <div className="flex items-center gap-4">
                  <button
                    onClick={() => { if (timeIndex >= machine.records.length - 1) setTimeIndex(0); setIsPlaying((p) => !p); }}
                    className="bg-info text-background font-semibold px-4 py-2 text-sm whitespace-nowrap"
                  >
                    {isPlaying ? "Pause" : "Play"}
                  </button>
                  <input type="range" min={0} max={machine.records.length - 1} value={timeIndex}
                    onChange={(e) => { setIsPlaying(false); setTimeIndex(Number(e.target.value)); }} className="w-full" />
                </div>
                <p className="text-secondary text-sm font-mono mt-1">Snapshot {safeIndex} of {machine.records.length - 1}</p>
              </div>

              <div className="grid grid-cols-3 gap-6 items-center">
                <KpiCard hero label="Health Score" value={`${current.healthScore}/100`} accentColor="#38BDF8"
                  trend={computeTrend(machine.records, safeIndex, "healthScore", true)} />
                <KpiCard label="Estimated Excess Cost" value={`₹${current.weeklyCostRs}/week`} accentColor="#F59E0B"
                  trend={computeTrend(machine.records, safeIndex, "weeklyCostRs", false)} />
                <KpiCard label="Efficiency Loss" value={`${current.efficiencyLossPct}%`} accentColor="#EF4444"
                  trend={computeTrend(machine.records, safeIndex, "efficiencyLossPct", false)} />
              </div>

              <AlertPanel
                severity={current.severity} timeIndex={safeIndex} gracePeriod={machine.gracePeriodSnapshots}
                moderateThreshold={machine.moderateThreshold} criticalThreshold={machine.criticalThreshold}
                efficiencyLossPct={current.efficiencyLossPct} weeklyCostRs={current.weeklyCostRs}
                scheduledRepairCostRs={machine.scheduledRepairCostRs}
              />

              <div className="grid grid-cols-2 gap-4">
                <HealthChart points={chartPoints} />
                <InsightsPanel daysToCritical={current.daysToCritical} contributions={current.contributions} />
              </div>

              <details className="bg-card border border-border p-5">
                <summary className="text-primary font-semibold cursor-pointer">How is this cost calculated?</summary>
                <div className="text-secondary text-sm mt-3 space-y-1">
                  <p>Current severity score: <span className="font-mono text-primary">{current.severity.toFixed(3)}</span> (0 = healthy, 1 = most anomalous observed)</p>
                  <p>This bearing's critical threshold: <span className="font-mono text-primary">{machine.criticalThreshold}</span>, adaptively calibrated from its own healthy-baseline noise level</p>
                  <p>Estimated efficiency loss scaled within the literature-reported 1.5–4% range for bearing faults</p>
                  <p>Healthy motor efficiency assumed: 91.7% (IEC 60034-30-1 nominal for a 15 kW IE3-class motor)</p>
                  <p>Operating assumption: <span className="font-mono text-primary">{machine.ratedPowerKw} kW</span> rated motor, <span className="font-mono text-primary">₹{machine.tariffRsPerKwh}/kWh</span> tariff</p>
                  <p className="italic mt-2">Literature-grounded approximations for a representative case, not precision figures for this specific machine.</p>
                </div>
              </details>
            </>
          ) : null}
        </div>
      </div>
    </div>
  );
}

export default App;