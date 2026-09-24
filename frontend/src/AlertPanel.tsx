type AlertPanelProps = {
  severity: number;
  timeIndex: number;
  gracePeriod: number;
  moderateThreshold: number;
  criticalThreshold: number;
  efficiencyLossPct: number;
  weeklyCostRs: number;
  scheduledRepairCostRs: number;
};

function AlertPanel({
  severity, timeIndex, gracePeriod, moderateThreshold, criticalThreshold,
  efficiencyLossPct, weeklyCostRs, scheduledRepairCostRs,
}: AlertPanelProps) {
  if (timeIndex < gracePeriod) {
    return (
      <div className="border-l-4 border-info bg-card py-4 px-5">
        <p className="text-info font-semibold text-sm mb-1">Warming up</p>
        <p className="text-secondary text-sm">
          Startup vibration transients are expected in the first few readings — monitoring begins evaluating after this initial period.
        </p>
      </div>
    );
  }

  if (severity > criticalThreshold) {
    const avoidedLow = scheduledRepairCostRs * 2;
    const avoidedHigh = scheduledRepairCostRs * 4;
    return (
      <div className="border-l-4 border-critical bg-card py-4 px-5 space-y-2">
        <p className="text-critical font-semibold text-sm">High-severity anomaly detected</p>
        <p className="text-secondary text-sm">
          Estimated efficiency loss: <span className="font-mono text-primary">{efficiencyLossPct.toFixed(2)}%</span>, costing an estimated <span className="font-mono text-primary">₹{weeklyCostRs}</span>/week in excess energy alone. Recommend scheduling an inspection within the next few days.
        </p>
        <p className="text-secondary text-sm">
          Catching this now, rather than waiting for it to fail, could also avoid an estimated <span className="font-mono text-primary">₹{avoidedLow}–₹{avoidedHigh}</span> in emergency repair premium — reactive repairs are documented to cost 3–5x more than the same job done on a planned schedule.
        </p>
      </div>
    );
  }

  if (severity > moderateThreshold) {
    return (
      <div className="border-l-4 border-warning bg-card py-4 px-5">
        <p className="text-warning font-semibold text-sm mb-1">Moderate anomaly detected</p>
        <p className="text-secondary text-sm">
          Estimated efficiency loss: <span className="font-mono text-primary">{efficiencyLossPct.toFixed(2)}%</span>. Not urgent yet — monitor closely and plan inspection during the next scheduled downtime.
        </p>
      </div>
    );
  }

  return (
    <div className="border-l-4 border-healthy bg-card py-4 px-5">
      <p className="text-healthy font-semibold text-sm">Operating within normal parameters</p>
      <p className="text-secondary text-sm mt-1">No action needed.</p>
    </div>
  );
}

export default AlertPanel;